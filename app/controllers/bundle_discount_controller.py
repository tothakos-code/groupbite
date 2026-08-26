from flask import Blueprint, request
from marshmallow import Schema, fields

from app.services.bundle_discount_service import BundleDiscountService
from app.utils.decorators import (
    handle_request,
    require_auth,
    require_vendor_manager,
    validate_url_params,
)
from app.utils.validators import IDSchema
from app.utils.vendor_resolvers import vendor_from_kwarg


class BundleDiscountSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(load_default=None, allow_none=True)


class BundleSlotSchema(Schema):
    slot_index = fields.Int(required=True)
    match_type = fields.Str(required=True)
    category_id = fields.Int(load_default=None, allow_none=True)
    menu_item_id = fields.Int(load_default=None, allow_none=True)
    price_override = fields.Int(load_default=None, allow_none=True)
    price_delta = fields.Int(load_default=None, allow_none=True)


class BundleDiscountController:
    def __init__(self) -> None:
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("bundle_discount_controller", __name__)

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles",
            view_func=self.handle_list,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles",
            view_func=self.handle_create,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles/<int:bundle_id>",
            view_func=self.handle_update,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles/<int:bundle_id>",
            view_func=self.handle_delete,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles/<int:bundle_id>/slots",
            view_func=self.handle_add_slot,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles/<int:bundle_id>/slots/<int:slot_id>",
            view_func=self.handle_update_slot,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/bundles/<int:bundle_id>/slots/<int:slot_id>",
            view_func=self.handle_delete_slot,
            methods=["DELETE"],
        )

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_list(self, db, vendor_id):
        bundles = BundleDiscountService.get_by_vendor(db, vendor_id)
        return {"data": [b.serialized for b in bundles]}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_create(self, db, vendor_id):
        data = BundleDiscountSchema().load((request.json or {}).get("data", {}))
        bundle = BundleDiscountService.create(
            db, vendor_id, name=data["name"], description=data["description"]
        )
        return {"data": bundle.serialized}, 201

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_update(self, db, vendor_id, bundle_id):
        data = BundleDiscountSchema().load((request.json or {}).get("data", {}))
        bundle = BundleDiscountService.update(db, bundle_id, **data)
        return {"data": bundle.serialized}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete(self, db, vendor_id, bundle_id):
        BundleDiscountService.delete(db, bundle_id)
        return {"msg": "OK"}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_slot(self, db, vendor_id, bundle_id):
        data = BundleSlotSchema().load((request.json or {}).get("data", {}))
        slot = BundleDiscountService.add_slot(
            db, bundle_id,
            slot_index=data["slot_index"],
            match_type=data["match_type"],
            category_id=data["category_id"],
            menu_item_id=data["menu_item_id"],
            price_override=data["price_override"],
            price_delta=data["price_delta"],
        )
        return {"data": slot.serialized}, 201

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_update_slot(self, db, vendor_id, bundle_id, slot_id):
        data = BundleSlotSchema().load((request.json or {}).get("data", {}))
        slot = BundleDiscountService.update_slot(db, slot_id, **data)
        return {"data": slot.serialized}, 200

    @require_auth
    @require_vendor_manager(vendor_from_kwarg())
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete_slot(self, db, vendor_id, bundle_id, slot_id):
        BundleDiscountService.delete_slot(db, slot_id)
        return {"msg": "OK"}, 200
