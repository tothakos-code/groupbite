from flask import Blueprint, request
from marshmallow import Schema, fields

from app.services.option_group_service import OptionGroupService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_url_params,
)
from app.utils.validators import IDSchema


class OptionGroupSchema(Schema):
    name = fields.Str(required=True)
    min_choices = fields.Int(load_default=0)
    max_choices = fields.Int(load_default=1)
    required = fields.Bool(load_default=False)
    index = fields.Int(load_default=0)


class OptionChoiceSchema(Schema):
    name = fields.Str(required=True)
    price_delta = fields.Int(load_default=0)
    index = fields.Int(load_default=0)


class OptionGroupController:
    def __init__(self) -> None:
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("option_group_controller", __name__)

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups",
            view_func=self.handle_list,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups",
            view_func=self.handle_create,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups/<int:group_id>",
            view_func=self.handle_update,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups/<int:group_id>",
            view_func=self.handle_delete,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups/<int:group_id>/choices",
            view_func=self.handle_add_choice,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups/<int:group_id>/choices/<int:choice_id>",
            view_func=self.handle_update_choice,
            methods=["PUT"],
        )
        bp.add_url_rule(
            "/api/vendor/<vendor_id>/option-groups/<int:group_id>/choices/<int:choice_id>",
            view_func=self.handle_delete_choice,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/api/item/<int:item_id>/option-groups/<int:group_id>",
            view_func=self.handle_assign,
            methods=["POST"],
        )
        bp.add_url_rule(
            "/api/item/<int:item_id>/option-groups/<int:group_id>",
            view_func=self.handle_unassign,
            methods=["DELETE"],
        )

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_list(self, db, vendor_id):
        groups = OptionGroupService.get_by_vendor(db, vendor_id)
        return {"data": [g.serialized for g in groups]}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_create(self, db, vendor_id):
        data = OptionGroupSchema().load((request.json or {}).get("data", {}))
        group = OptionGroupService.create(
            db, vendor_id,
            name=data["name"],
            min_choices=data["min_choices"],
            max_choices=data["max_choices"],
            required=data["required"],
            index=data["index"],
        )
        return {"data": group.serialized}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_update(self, db, vendor_id, group_id):
        data = OptionGroupSchema().load((request.json or {}).get("data", {}))
        group = OptionGroupService.update(db, group_id, **data)
        return {"data": group.serialized}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete(self, db, vendor_id, group_id):
        OptionGroupService.delete(db, group_id)
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_choice(self, db, vendor_id, group_id):
        data = OptionChoiceSchema().load((request.json or {}).get("data", {}))
        choice = OptionGroupService.add_choice(
            db, group_id,
            name=data["name"],
            price_delta=data["price_delta"],
            index=data["index"],
        )
        return {"data": choice.serialized}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_update_choice(self, db, vendor_id, group_id, choice_id):
        data = OptionChoiceSchema().load((request.json or {}).get("data", {}))
        choice = OptionGroupService.update_choice(db, choice_id, **data)
        return {"data": choice.serialized}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete_choice(self, db, vendor_id, group_id, choice_id):
        OptionGroupService.soft_delete_choice(db, choice_id)
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @handle_request
    def handle_assign(self, db, item_id, group_id):
        index = (request.json or {}).get("index", 0)
        OptionGroupService.assign_to_item(db, group_id, item_id, index)
        return {"msg": "OK"}, 201

    @require_auth
    @require_admin
    @handle_request
    def handle_unassign(self, db, item_id, group_id):
        OptionGroupService.unassign_from_item(db, group_id, item_id)
        return {"msg": "OK"}, 200
