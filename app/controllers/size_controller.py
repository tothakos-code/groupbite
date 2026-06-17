from flask import Blueprint, session

from app.entities.size import BaseSizeSchema, BulkSizePriceByItemsSchema, BulkUpdateSizeSchema, Size, UpdateSizeSchema
from app.repositories.size_repository import SizeRepository
from app.services.size_service import SizeService
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


class SizeController:
    def __init__(self, size_service: SizeService) -> None:
        self.size_service = size_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("size_controller", __name__, url_prefix="/api/size")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("", view_func=self.handle_menu_item_size_add, methods=["POST"])
        bp.add_url_rule(
            "<size_id>", view_func=self.handle_menu_item_size_update, methods=["PUT"]
        )
        bp.add_url_rule(
            "<size_id>", view_func=self.handle_menu_item_size_delete, methods=["DELETE"]
        )
        bp.add_url_rule(
            "/bulk", view_func=self.handle_bulk_update_sizes, methods=["PUT"]
        )
        bp.add_url_rule(
            "/bulk-price-by-items", view_func=self.handle_bulk_price_by_items, methods=["PATCH"]
        )

    @validate_data(BaseSizeSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_size_add(self, db, data):
        self.size_service.add_size(
            db,
            Size(
                menu_item_id=data["menu_item_id"],
                link=data.get("link", ""),
                name=data["name"],
                price=data["price"],
                quantity=data["quantity"],
                unlimited=data["unlimited"],
            ),
        )
        return {"msg": "OK"}, 201

    @validate_url_params(IDSchema())
    @validate_data(UpdateSizeSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_size_update(self, db, data, size_id):
        size = SizeRepository(db).get_by_id(size_id)
        size = self.size_service.update_size(db, size, data, admin_user_id=session.get("user_id"))
        return {"data": size.serialized}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_size_delete(self, db, size_id):
        size = SizeRepository(db).get_by_id(size_id)
        size = self.size_service.delete_size(db, size)
        return {"msg": "OK"}, 200

    @validate_data(BulkUpdateSizeSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_bulk_update_sizes(self, db, data):
        updated = self.size_service.bulk_update_sizes(db, data, admin_user_id=session.get("user_id"))
        return {"msg": "OK", "updated_count": len(updated)}, 200

    @validate_data(BulkSizePriceByItemsSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_bulk_price_by_items(self, db, data):
        sizes = self.size_service.bulk_edit_prices_by_items(db, data)
        socketio.emit("be_vendors_update", [v.serialized for v in VendorService.find_all_active(db)])
        return {"data": [size.serialized for size in sizes]}, 200
