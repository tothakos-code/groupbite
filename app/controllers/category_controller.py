from flask import Blueprint
from marshmallow import Schema, fields

from app.services.category_service import CategoryService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema


class CategorySchema(Schema):
    name = fields.Str(required=True)
    default_packaging_fee = fields.Int(load_default=0)


class CategoryController:
    def __init__(self, category_service: CategoryService) -> None:
        self.category_service = category_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("category_controller", __name__, url_prefix="/api/vendor")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/<vendor_id>/categories",
            view_func=self.handle_list,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<vendor_id>/categories",
            view_func=self.handle_create,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/<vendor_id>/categories/<int:category_id>",
            view_func=self.handle_update,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/<vendor_id>/categories/<int:category_id>",
            view_func=self.handle_delete,
            methods=["DELETE"],
        )

    @validate_url_params(IDSchema())
    @require_auth
    @handle_request
    def handle_list(self, db, vendor_id):
        categories = self.category_service.get_all(db, vendor_id)
        return {"data": [c.serialized for c in categories]}, 200

    @validate_url_params(IDSchema())
    @validate_data(CategorySchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_create(self, db, data, vendor_id):
        category = self.category_service.get_or_create(db, vendor_id, data["name"])
        return {"data": category.serialized}, 201

    @validate_url_params(IDSchema())
    @validate_data(CategorySchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_update(self, db, data, vendor_id, category_id):
        category = self.category_service.update(db, category_id, data["name"], data.get("default_packaging_fee"))
        return {"data": category.serialized}, 200

    @validate_url_params(IDSchema())
    @require_auth
    @require_admin
    @handle_request
    def handle_delete(self, db, vendor_id, category_id):
        self.category_service.delete(db, category_id)
        return {"msg": "OK"}, 200
