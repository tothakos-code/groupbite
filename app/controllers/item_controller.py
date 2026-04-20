from flask import Blueprint

from app.entities.menu_item import (
    BaseItemSchema,
    BulkUpdateItemSchema,
    MenuItem,
    UpdateItemSchema,
)
from app.repositories.menu_item_repository import MenuItemRepository
from app.services.menu_item_service import MenuItemService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema


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

    @validate_data(BaseItemSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_add(self, db, data):
        item = self.menu_item_service.add_item(
            db,
            MenuItem(
                menu_id=data["menu_id"],
                name=data["name"],
                description=data["description"],
                category=data["category"],
            ),
        )

        return {"msg": "OK", "data": item.serialized}, 201

    @validate_url_params(IDSchema())
    @validate_data(UpdateItemSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_update(self, db, data, item_id):
        menu_item = MenuItemRepository(db).get_by_id(item_id)
        self.menu_item_service.update_item(db, menu_item, data)

        return {"msg": "OK"}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_delete(self, db, item_id):
        menu_item = MenuItemRepository(db).get_by_id(item_id)
        self.menu_item_service.delete_item(db, menu_item)
        return {"msg": "OK"}, 204

    @validate_data(BulkUpdateItemSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_bulk_update_indices(self, db, data):
        items_to_update = self.menu_item_service.bulk_update_indices(db, data)
        return {
            "msg": "Indices updated successfully",
            "updated_count": len(items_to_update),
        }, 200
