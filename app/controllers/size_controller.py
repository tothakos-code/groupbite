import json
import logging

from flask import Blueprint, request

from app.entities.menu_item import MenuItem
from app.entities.size import BaseSizeSchema, Size, UpdateSizeSchema
from app.repositories.size_repository import SizeRepository
from app.services.size_service import SizeService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema


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

    @validate_data(BaseSizeSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_size_add(self, db, data):
        self.size_service.add_size(
            db,
            Size(
                menu_item_id=data["menu_item_id"],
                link=data["link"] if "link" in data else "",
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
        size = self.size_service.update_size(db, size, data)
        return {"data": json.dumps(size.serialized)}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_menu_item_size_delete(self, db, size_id):
        size = SizeRepository(db).get_by_id(size_id)
        size = self.size_service.delete_size(db, size)
        return {"msg": "OK"}, 200
