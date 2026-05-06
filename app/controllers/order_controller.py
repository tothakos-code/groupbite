import logging
from datetime import date

from flask import Blueprint, request
from flask_socketio import join_room, leave_room, rooms

from app.db.session import get_session
from app.entities.order import BaseOrderSchema, Order
from app.repositories.order_repository import OrderRepository
from app.repositories.vendor_repository import VendorRepository
from app.services.order_service import OrderService
from app.services.user_basket_service import UserBasketService
from app.services.vendor_service import VendorService
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


class OrderController:
    def __init__(
        self, order_service: OrderService, user_basket_service: UserBasketService
    ):
        self.order_service = order_service
        self.user_basket_service = user_basket_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("order_controller", __name__, url_prefix="/api/order")

    def _register_routes(self):
        bp = self.blueprint
        # TODO: change to GET and use query params
        bp.add_url_rule("/", view_func=self.handle_get_orders, methods=["GET"])
        bp.add_url_rule(
            "/history", view_func=self.handle_order_history, methods=["POST"]
        )
        bp.add_url_rule(
            "/<int:order_id>", view_func=self.handle_get_basket, methods=["GET"]
        )
        bp.add_url_rule(
            "/<int:order_id>", view_func=self.handle_order_update, methods=["PUT"]
        )
        bp.add_url_rule(
            "/<int:order_id>/order_fee",
            view_func=self.handle_update_order_fee,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<order_id>/user/<user_id>/copy-from/<src_user_id>",
            view_func=self.handle_copy_basket,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<order_id>/user/<user_id>/item/<item_id>/size/<size_id>",
            view_func=self.handle_add_to_basket,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<order_id>/user/<user_id>/item/<item_id>/size/<size_id>",
            view_func=self.handle_remove_from_basket,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/<order_id>/user/<user_id>",
            view_func=self.handle_clear_user_basket,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/<order_id>/state", view_func=self.handle_close_order, methods=["PUT"]
        )
        bp.add_url_rule(
            "/<order_id>/send-email",
            view_func=self.handle_manual_email_order,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/statistics", view_func=self.handle_get_statistics, methods=["GET"]
        )
        bp.add_url_rule(
            "/<int:order_id>", view_func=self.handle_delete_order, methods=["DELETE"]
        )

    @handle_request
    def handle_order_history(self, db):
        date_from = request.json["date_from"]
        date_to = request.json["date_to"]
        result = self.order_service.get_history(db, date_from, date_to)

        return {"data": result}, 200

    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_basket(self, db, order_id):
        order = self.order_service.get_order_by_id(db, order_id)
        return_obj = order.serialized
        return_obj["basket"] = self.order_service.get_order_items(order, db=db)
        return {"data": return_obj}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @validate_data(BaseOrderSchema())
    @handle_request
    def handle_order_update(self, db, data, order_id):
        order = self.order_service.update_order(db, order_id, data)

        socketio.emit(
            "be_order_update",
            {"order": order.serialized},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"data": order.serialized}, 200

    @handle_request
    def handle_get_statistics(self, db):
        result = self.order_service.get_statistics(db)
        return {"data": result}, 200

    @require_auth
    @require_admin
    @handle_request
    def handle_get_orders(self, db):
        orders = self.order_service.get_all_order(db, request.args)
        return {"data": orders}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_update_order_fee(self, db, order_id):
        order = self.order_service.update_order_fee(
            db, order_id, request.json["data"]["order_fee"]
        )
        socketio.emit(
            "be_order_update",
            {
                "order": order.serialized,
            },
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"msg": "OK"}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_copy_basket(self, db, order_id, user_id, src_user_id):
        order = self.order_service.copy_basket(db, order_id, user_id, src_user_id)
        db.commit()
        menus = VendorService(self.order_service).get_menu_items(
            db, order.vendor_id, str(order.open_from)
        )
        socketio.emit(
            "be_order_update",
            {"basket": self.order_service.get_order_items(order, db=db)},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        socketio.emit(
            "be_menu_update",
            {"menus": menus},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"msg": "OK"}, 201

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_to_basket(self, db, order_id, user_id, item_id, size_id):
        option_choice_ids = (request.json or {}).get("option_choice_ids", [])
        basket_item = self.order_service.add_to_basket(
            db, order_id, user_id, item_id, size_id,
            option_choice_ids=option_choice_ids,
        )
        db.commit()
        if basket_item:
            order = basket_item.order
            db.expire(order, ["items"])
            logging.info(basket_item)
            logging.info(basket_item.order)
            socketio.emit(
                "be_order_update",
                {"basket": self.order_service.get_order_items(order, db=db)},
                to=f"{order.vendor_id}@{order.open_from}",
            )
            menus = VendorService(self.order_service).get_menu_items(
                db, order.vendor_id, str(order.open_from)
            )
            socketio.emit(
                "be_menu_update",
                {"menus": menus},
                to=f"{order.vendor_id}@{order.open_from}",
            )
            return {"msg": "OK"}, 201
        else:
            return {"error": "Item out of stock"}, 400

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_remove_from_basket(self, db, order_id, user_id, item_id, size_id):
        self.order_service.remove_from_basket(db, order_id, user_id, item_id, size_id)
        db.commit()
        order = self.order_service.get_order_by_id(db, order_id)
        db.expire(order, ["items"])
        socketio.emit(
            "be_order_update",
            {"basket": self.order_service.get_order_items(order, db=db)},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        menus = VendorService(self.order_service).get_menu_items(
            db, order.vendor_id, str(order.open_from)
        )
        socketio.emit(
            "be_menu_update",
            {"menus": menus},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"msg": "OK"}, 204

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_clear_user_basket(self, db, order_id, user_id):
        self.user_basket_service.clear_items(db, user_id, order_id)
        db.commit()
        order = self.order_service.get_order_by_id(db, order_id)
        db.expire(order, ["items"])
        socketio.emit(
            "be_order_update",
            {"basket": self.order_service.get_order_items(order, db=db)},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        menus = VendorService(self.order_service).get_menu_items(
            db, order.vendor_id, str(order.open_from)
        )
        socketio.emit(
            "be_menu_update",
            {"menus": menus},
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"msg": "OK"}, 204

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_close_order(self, db, order_id):
        order = self.order_service.close_order(db, order_id)
        db.flush()
        db.expire(order)
        socketio.emit(
            "be_order_update",
            {
                "order": order.serialized,
                "basket": OrderService.get_order_items(order, db=db),
            },
            to=f"{order.vendor_id}@{order.open_from}",
        )
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete_order(self, db, order_id):
        self.order_service.delete_order(db, order_id)
        return {"msg": "OK"}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_manual_email_order(self, db, order_id):
        self.order_service.email_order(db, order_id)
        return {"msg": "Email sent and order closed manually"}, 200


@socketio.on("fe_date_selection")
def handle_date_selection_change(data):
    new_date = data["new_selected_date"]
    vendor_id = data["vendor_id"]

    sid = request.sid
    for room in rooms(sid):
        if room != sid:
            leave_room(room, sid=sid)

    with get_session() as db:
        order_repo = OrderRepository(db)
        vendor = VendorRepository(db).get_by_id(vendor_id)
        order = order_repo.find_order_by_date_for_a_vendor(vendor_id, new_date)

        if not order:
            from datetime import timedelta
            ref_date = date.fromisoformat(new_date) if isinstance(new_date, str) else new_date
            if bool(VendorService.get_setting_value(vendor, "auto_order_creation")):
                order_duration_days = int(VendorService.get_setting_value(vendor, "order_duration_days") or 1)
                open_until = ref_date + timedelta(days=order_duration_days - 1) if order_duration_days > 1 else None
                effective_until = open_until or ref_date
                if not order_repo.has_overlapping_open_order(vendor.id, ref_date, effective_until):
                    order = order_repo.save(
                        Order(
                            vendor_id=vendor.id,
                            open_from=ref_date,
                            open_until=open_until,
                            order_fee=VendorService.get_setting_value(vendor, "transport_price"),
                        )
                    )

        if not order:
            join_room(f"{vendor_id}@{new_date}")
            socketio.emit(
                "be_order_update",
                {"order": {}, "basket": {}},
                to=request.sid,
            )
            socketio.emit(
                "be_menu_update",
                {"menus": VendorService.get_menu_items(db, vendor_id, new_date)},
                to=request.sid,
            )
            return {"ok": True}

        join_room(f"{vendor_id}@{order.open_from}")

        socketio.emit(
            "be_order_update",
            {"order": order.serialized, "basket": OrderService.get_order_items(order, db=db)},
            to=request.sid,
        )
        socketio.emit(
            "be_menu_update",
            {"menus": VendorService.get_menu_items(db, vendor_id, str(order.open_from))},
            to=request.sid,
        )
        return {"ok": True}
