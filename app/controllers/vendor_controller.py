import logging
from datetime import datetime
from uuid import UUID

from flask import Blueprint, request, session

from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.notification import Notification, NotificationType
from app.entities.size import Size
from app.entities.user import User
from app.entities.vendor import BaseVendorSchema, Vendor, VendorType
from app.entities.webhook import Webhook
from app.repositories.vendor_repository import VendorRepository
from app.services.vendor_service import VendorService
from app.services.webhook_service import WebhookService
from app.socketio_singleton import SocketioSingleton
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema

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
        # ToDo: értesítése bekapcsolása / eszköz, vagy utána nézni hogy működik máshol
        bp.add_url_rule(
            "/<vendor_id>/notifications/<notification_type>/subscribe",
            view_func=self.handle_notification_subscribe,
            methods=["POST"],
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
            view_func=self.handle_save_settings,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<vendor_id>", view_func=self.handle_get_settings, methods=["GET"]
        )
        bp.add_url_rule(
            "/<vendor_id>/menus", view_func=self.handle_menu_get, methods=["GET"]
        )
        # ToDo: update import, make export
        bp.add_url_rule(
            "/<vendor_id>/menus/import", view_func=self.import_menu, methods=["POST"]
        )

    @require_auth
    @require_admin
    @handle_request
    def handle_get_all_vendors(self, db):
        result = self.vendor_service.get_vendors(db)
        return {"data": [v.serialized for v in result]}, 200

    @require_auth
    @require_admin
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
    @require_admin
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
                notification_type=NotificationType(notification_type),
                endpoint=notification_json["endpoint"],
                p256dh=notification_json["keys"]["p256dh"],
                auth=notification_json["keys"]["auth"],
            )
        )
        socketio.emit("be_user_update", User.get_one_by_id(user_id).serialized)

        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    @require_auth
    def handle_notification_unsubscribe(self, vendor_id, notification_type):
        # todo: Refactor after Notification Service
        user_id = session.get("user_id")
        notifications = Notification.find_by_vendor_id_user_id(
            vendor_id, user_id, NotificationType(notification_type)
        )
        for noti in notifications:
            if noti.delete():
                socketio.emit("be_user_update", User.get_one_by_id(user_id).serialized)
                return {"msg": "OK"}, 200
            else:
                return {"error": "Someting went wrong"}, 500

    @validate_url_params(IDSchema())
    def handle_notification_status(self, vendor_id, notification_type):
        # todo: Refactor after Notification Service
        user_id = session.get("user_id")
        if not user_id:
            return {"data": {"status": False}}, 200
        notification = Notification.find_by_pk(vendor_id, user_id, notification_type)
        if notification:
            return {"data": {"status": True}}, 200
        else:
            return {"data": {"status": False}}, 200

    @require_auth
    @require_admin
    @validate_data(BaseVendorSchema())
    @handle_request
    def handle_create(self, db, data):
        vendor = self.vendor_service.create_vendor(db, data)
        return {"data": vendor.serialized}, 200

    @require_auth
    @require_admin
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
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_webhooks(self, db, vendor_id):
        webhooks = self.webhook_service.find_by_vendor_id(db, vendor_id)

        return {"data": {"vendors": [wh.serialized for wh in webhooks]}}, 200

    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_settings(self, db, vendor_id):
        vendor = self.vendor_service.get_vendor(db, vendor_id)
        # Todo: There are public and private settings. Migrate to a vendor_setting table id,vendor_id,key,value,is_public,setting_type
        return {"data": vendor.serialized}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_save_settings(self, db, vendor_id):
        settings = request.json["data"]
        vendor = self.vendor_service.get_vendor(db, vendor_id)
        self.vendor_service.update_settings(vendor, settings)
        socketio.emit(
            "be_vendors_update",
            [v.serialized for v in VendorService.find_all_active(db)],
        )

        return {"data": vendor.settings}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_menu_get(self, db, vendor_id):
        result = self.vendor_service.get_menus(db, vendor_id, request.args)
        return {"data": result}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def import_menu(self, db, vendor_id):
        self.vendor_service.import_menu(db, vendor_id, request.files)
        return {"msg": "OK"}, 201
