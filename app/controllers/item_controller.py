from flask import Blueprint

from app.entities.menu_item import (
    BaseItemSchema,
    BulkDeleteItemsSchema,
    BulkEditItemsSchema,
    BulkUpdateItemSchema,
    MenuItem,
    UpdateItemSchema,
)
from app.repositories.menu_item_repository import MenuItemRepository
from app.services.category_service import CategoryService
from app.services.menu_item_service import MenuItemService
from app.services.vendor_service import VendorService
from app.socketio_singleton import SocketioSingleton
from app.utils.decorators import (
    handle_request,
    require_auth,
    require_vendor_manager,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema
from app.utils.vendor_resolvers import (
    vendor_from_body,
    vendor_from_body_item_list,
    vendor_from_body_items_or_menu,
    vendor_from_menu_item,
)

socketio = SocketioSingleton.get_instance()


class MenuItemController:
    def __init__(self, menu_item_service: MenuItemService) -> None:
        self.menu_item_service = menu_item_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("item_controller", __name__, url_prefix="/api/item")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("", view_func=self.handle_menu_item_add, methods=["POST"])
        bp.add_url_rule(
            "<item_id>", view_func=self.handle_menu_item_update, methods=["PUT"]
        )
        bp.add_url_rule(
            "<item_id>", view_func=self.handle_menu_item_delete, methods=["DELETE"]
        )
        bp.add_url_rule(
            "/reorder", view_func=self.handle_bulk_update_indices, methods=["PUT"]
        )
        bp.add_url_rule("/bulk", view_func=self.handle_bulk_edit, methods=["PATCH"])
        bp.add_url_rule("/bulk", view_func=self.handle_bulk_delete, methods=["DELETE"])

    @validate_data(BaseItemSchema())
    @require_auth
    @require_vendor_manager(vendor_from_body())
    @handle_request
    def handle_menu_item_add(self, db, data):
        category = CategoryService.get_or_create(db, data["vendor_id"], data.get("category") or "")
        item = self.menu_item_service.add_item(
            db,
            data["vendor_id"],
            MenuItem(
                menu_id=data["menu_id"],
                name=data["name"],
                description=data["description"],
                category_id=category.id,
            ),
        )

        return {"msg": "OK", "data": item.serialized}, 201

    @validate_url_params(IDSchema())
    @validate_data(UpdateItemSchema())
    @require_auth
    @require_vendor_manager(vendor_from_body())
    @handle_request
    def handle_menu_item_update(self, db, data, item_id):
        menu_item = MenuItemRepository(db).get_by_id(item_id)
        self.menu_item_service.update_item(db, data["vendor_id"], menu_item, data)

        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_vendor_manager(vendor_from_menu_item())
    @handle_request
    def handle_menu_item_delete(self, db, item_id):
        menu_item = MenuItemRepository(db).get_by_id(item_id)
        self.menu_item_service.delete_item(db, menu_item)
        return {"msg": "OK"}, 204

    @validate_data(BulkUpdateItemSchema())
    @require_auth
    @require_vendor_manager(vendor_from_body_item_list(field="items"))
    @handle_request
    def handle_bulk_update_indices(self, db, data):
        items_to_update = self.menu_item_service.bulk_update_indices(db, data)
        return {
            "msg": "Indices updated successfully",
            "updated_count": len(items_to_update),
        }, 200

    @validate_data(BulkEditItemsSchema())
    @require_auth
    @require_vendor_manager(vendor_from_body_items_or_menu())
    @handle_request
    def handle_bulk_edit(self, db, data):
        items = self.menu_item_service.bulk_edit(db, data)
        socketio.emit("be_vendors_update", [v.serialized for v in VendorService.find_all_active(db)])
        return {"data": [item.serialized for item in items]}, 200

    @validate_data(BulkDeleteItemsSchema())
    @require_auth
    @require_vendor_manager(vendor_from_body_items_or_menu())
    @handle_request
    def handle_bulk_delete(self, db, data):
        deleted_count = self.menu_item_service.bulk_delete(db, data)
        socketio.emit("be_vendors_update", [v.serialized for v in VendorService.find_all_active(db)])
        return {"msg": "OK", "deleted_count": deleted_count}, 200
