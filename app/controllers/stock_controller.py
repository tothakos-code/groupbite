from datetime import date

from flask import Blueprint, request, session

from app.repositories.order_repository import OrderRepository
from app.repositories.size_repository import SizeRepository
from app.services.stock_service import StockService
from app.services.vendor_service import VendorService
from app.socketio_singleton import SocketioSingleton
from app.utils.decorators import handle_request, require_admin, require_auth, validate_url_params
from app.utils.validators import IDSchema

socketio = SocketioSingleton.get_instance()


class StockController:
    def __init__(self):
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("stock_controller", __name__, url_prefix="/api")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/size/<size_id>/topup",
            view_func=self.handle_topup,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/vendor/<vendor_id>/stock",
            view_func=self.handle_get_stock_levels,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/size/<size_id>/stock/history",
            view_func=self.handle_get_stock_history,
            methods=["GET"],
        )

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_topup(self, db, size_id):
        body = request.get_json(silent=True, force=True) or {}
        quantity = body.get("quantity")
        note = body.get("note", "")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")

        size, entry = StockService.top_up_stock(
            db, size_id, quantity, note, admin_user_id=session.get("user_id")
        )

        self._broadcast_menu_update(db, size)

        return {"size": size.serialized, "history_entry": entry.serialized}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_get_stock_levels(self, db, vendor_id):
        category_id = request.args.get("category_id", type=int)
        items = StockService.get_stock_levels(db, vendor_id, category_id)
        return {"data": {"items": items}}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_get_stock_history(self, db, size_id):
        from_date = _parse_date(request.args.get("from"))
        to_date = _parse_date(request.args.get("to"))
        result = StockService.get_stock_history(db, size_id, from_date, to_date)
        return {"data": result}, 200

    def _broadcast_menu_update(self, db, size):
        menu_item = size.menu_item
        if menu_item is None:
            return
        menu = menu_item.menu
        if menu is None:
            return
        vendor_id = menu.vendor_id
        orders = OrderRepository(db).find_all_open_for_vendor(vendor_id)
        for order in orders:
            menus = VendorService.get_menu_items(db, vendor_id, str(order.open_from))
            socketio.emit(
                "be_menu_update",
                {"menus": menus},
                to=f"{vendor_id}@{order.open_from}",
            )


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
