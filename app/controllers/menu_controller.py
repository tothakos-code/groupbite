import logging

from flask import request, Blueprint

from app.entities.menu import BaseMenuSchema, UpdateMenuSchema
from app.services.menu_service import MenuService
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_vendor_manager, handle_request
from app.utils.validators import IDSchema
from app.utils.vendor_resolvers import vendor_from_body, vendor_from_menu


class MenuController:

    def __init__(self, menu_service: MenuService):
        self.menu_service = menu_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("menu_controller", __name__, url_prefix="/api/menu")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("/<menu_id>", view_func=self.handle_menu_get_items, methods=["GET"])
        bp.add_url_rule("/<menu_id>", view_func=self.handle_menu_update, methods=["PUT"])
        bp.add_url_rule("/<int:menu_id>", view_func=self.handle_menu_delete, methods=["DELETE"])
        bp.add_url_rule("/<menu_id>/duplicate", view_func=self.handle_menu_duplicate, methods=["POST"])
        bp.add_url_rule("/", view_func=self.handle_menu_add, methods=["POST"])
        bp.add_url_rule("/<menu_id>/activate", view_func=self.handle_activation, methods=["GET"])
        bp.add_url_rule("/<menu_id>/deactivate", view_func=self.handle_deactivation, methods=["GET"])

    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_menu_get_items(self, db, menu_id):
        items = self.menu_service.get_menu_items(db, menu_id, request.args)
        return { "data": items }, 200

    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @validate_data(UpdateMenuSchema())
    @handle_request
    def handle_menu_update(self, db, data, menu_id):
        from_date = data["from_date"] if "from_date" in data else None
        to_date = data["to_date"] if "to_date" in data else None
        menu = self.menu_service.update_menu(db, menu_id, data["name"], from_date, to_date)

        return {"data": menu.serialized}, 200


    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_menu_delete(self, db, menu_id):
        self.menu_service.delete_menu(db, menu_id)
        return { "msg": "OK" }, 204


    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_menu_duplicate(self, db, menu_id):
        self.menu_service.duplicate_menu(db, menu_id)
        return { "msg": "OK" }, 200

    @require_auth
    @require_vendor_manager(vendor_from_body())
    @validate_data(BaseMenuSchema())
    @handle_request
    def handle_menu_add(self, db, data):
        self.menu_service.add_menu(db, name=data["name"], vendor_id=data["vendor_id"])
        return { "msg": "OK" }, 201

    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_activation(self, db, menu_id):
        menu = self.menu_service.activate_menu(db, menu_id)
        logging.info(str(menu.id) + " vendor got activated")
        return { "msg": "OK" }, 200

    @require_auth
    @require_vendor_manager(vendor_from_menu())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_deactivation(self, db, menu_id):
        menu = self.menu_service.deactivate_menu(db, menu_id)
        logging.info(str(menu.id) + " vendor got deactivated")
        return { "msg": "OK" }, 200
