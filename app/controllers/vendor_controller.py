from datetime import datetime

from flask import Blueprint, request, session

from app.entities.notification import Notification, NotificationType
from app.entities.vendor import BaseVendorSchema
from app.repositories.user_repository import UserRepository
from app.services.vendor_service import VendorService
from app.services.webhook_service import WebhookService
from app.socketio_singleton import SocketioSingleton
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    require_vendor_manager,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema
from app.utils.vendor_resolvers import vendor_from_kwarg
from app.event_manager import event_manager

socketio = SocketioSingleton.get_instance()


class VendorController:
    def __init__(self, vendor_service: VendorService, webhook_service: WebhookService):
        self.vendor_service = vendor_service
        self.webhook_service = webhook_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("vendor_controller", __name__, url_prefix="/api/vendor")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("", view_func=self.handle_get_all_vendors, methods=["GET"])
        bp.add_url_rule(
            "/<vendor_id>/activate", view_func=self.handle_activation, methods=["PUT"]
        )
        bp.add_url_rule(
            "/<vendor_id>/deactivate",
            view_func=self.handle_deactivation,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<vendor_id>/notifications/<notification_type>/subscribe",
            view_func=self.handle_notification_subscribe,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/<vendor_id>/notifications/<notification_type>/unsubscribe/device",
            view_func=self.handle_notification_unsubscribe_device,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/<vendor_id>/notifications/<notification_type>/unsubscribe",
            view_func=self.handle_notification_unsubscribe,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/<vendor_id>/notifications/<notification_type>",
            view_func=self.handle_notification_status,
            methods=["GET"],
        )
        bp.add_url_rule("", view_func=self.handle_create, methods=["POST"])
        bp.add_url_rule(
            "/<vendor_id>/scan", view_func=self.handle_run_scan, methods=["GET"]
        )
        bp.add_url_rule(
            "/<vendor_id>/webhooks", view_func=self.handle_get_webhooks, methods=["GET"]
        )
        bp.add_url_rule(
            "/<vendor_id>/settings",
            view_func=self.handle_get_full_settings,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<vendor_id>/settings",
            view_func=self.handle_save_settings,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<vendor_id>", view_func=self.handle_get_settings, methods=["GET"]
        )
        bp.add_url_rule(
            "/<vendor_id>/menus", view_func=self.handle_menu_get, methods=["GET"]
        )
        bp.add_url_rule(
            "/<vendor_id>/menus/import", view_func=self.import_menu, methods=["POST"]
        )
        bp.add_url_rule(
            "/<vendor_id>/plugin-settings",
            view_func=self.handle_get_plugin_settings,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<vendor_id>/plugin-settings",
            view_func=self.handle_save_plugin_settings,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<vendor_id>/order",
            view_func=self.handle_create_order,
            methods=["POST"],
        )

    @require_auth
    @handle_request
    def handle_get_all_vendors(self, db):
        from app.repositories.user_repository import UserRepository
        from app.services.access_group_service import AccessGroupService

        user_id = session.get("user_id")
        managed_vendor_ids = None
        if not UserRepository(db).is_admin(user_id):
            managed_vendor_ids = AccessGroupService.list_managed_vendor_ids(db, user_id)
        result = self.vendor_service.get_vendors(db, managed_vendor_ids=managed_vendor_ids)
        return {"data": [v.serialized for v in result]}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_deactivation(self, db, vendor_id):
        self.vendor_service.deactivate_vendor(db, vendor_id)
        socketio.emit(
            "be_vendors_update",
            [v.serialized for v in self.vendor_service.find_all_active(db)],
        )
        return {"msg": "OK"}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_activation(self, db, vendor_id):
        self.vendor_service.activate_vendor(db, vendor_id)
        socketio.emit(
            "be_vendors_update",
            [v.serialized for v in self.vendor_service.find_all_active(db)],
        )
        return {"msg": "OK"}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_notification_subscribe(self, db, vendor_id, notification_type):
        # todo: Refactor after Notification Service
        user_id = session.get("user_id")
        notification_json = request.json["data"]
        Notification.add(
            Notification(
                vendor_id=vendor_id,
                user_id=user_id,
                notification_types=[NotificationType(notification_type)],
                endpoint=notification_json["endpoint"],
                p256dh=notification_json["keys"]["p256dh"],
                auth=notification_json["keys"]["auth"],
            )
        )
        socketio.emit(
            "be_user_update", UserRepository(db).get_by_id(user_id).serialized
        )

        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @handle_request
    def handle_notification_unsubscribe(self, db, vendor_id, notification_type):
        # todo: Refactor after Notification Service
        user_id = session.get("user_id")
        Notification.remove_type_for_user(vendor_id, user_id, NotificationType(notification_type))
        socketio.emit(
            "be_user_update",
            UserRepository(db).get_by_id(user_id).serialized,
        )
        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @handle_request
    def handle_notification_unsubscribe_device(self, db, vendor_id, notification_type):
        user_id = session.get("user_id")
        endpoint = request.json.get("endpoint")
        if not endpoint:
            return {"error": "endpoint required"}, 400
        Notification.remove_type_for_device(vendor_id, user_id, endpoint, NotificationType(notification_type))
        socketio.emit(
            "be_user_update",
            UserRepository(db).get_by_id(user_id).serialized,
        )
        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    def handle_notification_status(self, vendor_id, notification_type):
        # todo: Refactor after Notification Service
        user_id = session.get("user_id")
        if not user_id:
            return {"data": {"subscribed": False, "device_subscribed": False}}, 200
        notifications = Notification.find_by_vendor_id_user_id(
            vendor_id, user_id, NotificationType(notification_type)
        )
        endpoint = request.args.get("endpoint")
        subscribed = len(notifications) > 0
        device_subscribed = any(n.endpoint == endpoint for n in notifications) if endpoint else False
        return {"data": {"subscribed": subscribed, "device_subscribed": device_subscribed}}, 200

    @require_auth
    @require_admin
    @validate_data(BaseVendorSchema())
    @handle_request
    def handle_create(self, db, data):
        vendor = self.vendor_service.create_vendor(db, data)
        return {"data": vendor.serialized}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_run_scan(self, db, vendor_id):
        menu_date = request.args.get("menu_date")
        try:
            datetime.strptime(menu_date, "%Y-%m-%d")
        except ValueError as e:
            menu_date = None
        try:
            self.vendor_service.scan_menu(db, vendor_id, menu_date)
        except NotImplementedError as e:
            return {
                "error": f"Vendor {vendor_id} does not support automatic menu filling"
            }, 405
        return {"msg": f"Vendor scan ran for {vendor_id} id"}, 201

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_webhooks(self, db, vendor_id):
        webhooks = self.webhook_service.find_by_vendor_id(db, vendor_id)

        return {"data": {"vendors": [wh.serialized for wh in webhooks]}}, 200

    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_settings(self, db, vendor_id):
        vendor = self.vendor_service.get_vendor(db, vendor_id)
        return {"data": vendor.public_serialized}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_full_settings(self, db, vendor_id):
        vendor = self.vendor_service.get_vendor(db, vendor_id)
        return {"data": vendor.serialized}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_save_settings(self, db, vendor_id):
        data = request.json["data"]
        vendor = self.vendor_service.get_vendor(db, vendor_id)
        errors = self.vendor_service.update_settings(vendor, data, db=db)
        if errors:
            return {"errors": errors}, 422
        db.commit()
        socketio.emit(
            "be_vendors_update",
            [v.serialized for v in VendorService.find_all_active(db)],
        )
        from app.utils.vendor_settings import load_vendor_settings

        return {"data": load_vendor_settings(vendor)}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_menu_get(self, db, vendor_id):
        result = self.vendor_service.get_menus(db, vendor_id, request.args)
        return {"data": result}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def import_menu(self, db, vendor_id):
        self.vendor_service.import_menu(db, vendor_id, request.files)
        return {"msg": "OK"}, 201

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_plugin_settings(self, db, vendor_id):
        result = self.vendor_service.get_plugin_settings(db, vendor_id)
        if result is None:
            return {"error": "Vendor has no plugin"}, 404
        return {"data": result}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_save_plugin_settings(self, db, vendor_id):
        patch = request.json.get("data", {})
        vendor, errors = self.vendor_service.update_plugin_settings(db, vendor_id, patch)
        if vendor is None:
            if "error" in errors:
                return {"error": errors["error"]}, 400
            return {"errors": errors}, 422
        if errors:
            return {"errors": errors}, 422
        db.commit()
        return {"data": self.vendor_service.get_plugin_settings(db, vendor_id)}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_create_order(self, db, vendor_id):
        from datetime import date, datetime, time
        from app.repositories.vendor_repository import VendorRepository
        from app.services.order_service import OrderService, _adhoc_close_for_vendor
        from app.scheduler import schedule_once

        vendor = VendorRepository(db).get_by_id(vendor_id)
        if not vendor:
            return {"error": "vendor_not_found"}, 404

        body = request.json or {}
        open_until_raw = body.get("open_until")

        if not open_until_raw:
            return {"error": "open_until_required"}, 400

        open_until = None
        close_time = None

        if open_until_raw:
            if "T" in str(open_until_raw):
                dt = datetime.fromisoformat(open_until_raw)
                open_until = dt.date()
                if dt.time() != time(0, 0):
                    close_time = dt.time()
            else:
                open_until = date.fromisoformat(open_until_raw)

        user_id = session.get("user_id")

        event_manager.trigger_event(
            "beforeOpen@" + str(vendor_id),
            {"vendor_id": str(vendor_id), "open_until": str(open_until)},
        )

        try:
            order, created = OrderService.create_order_for_vendor(db, vendor, open_until, close_time, user_id=user_id)
        except ValueError as e:
            msg = str(e)
            if msg == "open_until_before_today":
                return {"error": msg}, 400
            return {"error": msg}, 409

        if created and close_time is not None:
            target_date = open_until or order.open_from
            target_dt = datetime.combine(target_date, close_time)
            task_id = f"{vendor_id}-adhoc-close-{order.id}"
            schedule_once(task_id, target_dt, _adhoc_close_for_vendor, str(vendor_id))

        db.commit()

        if created:
            event_manager.trigger_event(
                "afterOpen@" + str(vendor_id),
                {"order_id": order.id, "order": order.serialized},
            )
            from app.services.order_service import OrderService
            room = f"{vendor_id}@{order.open_from}"
            socketio.emit(
                "be_order_update",
                {"order": order.serialized, "basket": OrderService.get_order_items(order)},
                to=room,
            )
            socketio.emit(
                "be_menu_update",
                {"menus": VendorService.get_menu_items(db, str(vendor_id), str(order.open_from))},
                to=room,
            )

        status = 201 if created else 200
        return {"data": order.serialized}, status
