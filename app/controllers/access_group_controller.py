from flask import Blueprint, request, session
from marshmallow import Schema, fields

from app.services.access_group_service import AccessGroupService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_url_params,
)
from app.utils.validators import IDSchema


class AccessGroupSchema(Schema):
    name = fields.Str(required=True)


class AccessGroupController:
    """Manager-role groups (see docs/architecture.md).

    Admin-only for now: creation, membership, and vendor assignment are all
    superadmin-gated. This is the pilot for a future self-service groups feature —
    the data model (a group of users <-> a set of vendors) doesn't need to change when
    that ships, only who's allowed to call these endpoints.
    """

    def __init__(self) -> None:
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("access_group_controller", __name__, url_prefix="/api/access-groups")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("", view_func=self.handle_list, methods=["GET"])
        bp.add_url_rule("", view_func=self.handle_create, methods=["POST"])
        bp.add_url_rule("/<access_group_id>", view_func=self.handle_rename, methods=["PUT"])
        bp.add_url_rule("/<access_group_id>", view_func=self.handle_delete, methods=["DELETE"])
        bp.add_url_rule(
            "/<access_group_id>/members", view_func=self.handle_add_member, methods=["POST"]
        )
        bp.add_url_rule(
            "/<access_group_id>/members/<user_id>",
            view_func=self.handle_remove_member,
            methods=["DELETE"],
        )
        bp.add_url_rule(
            "/<access_group_id>/vendors", view_func=self.handle_add_vendor, methods=["POST"]
        )
        bp.add_url_rule(
            "/<access_group_id>/vendors/<vendor_id>",
            view_func=self.handle_remove_vendor,
            methods=["DELETE"],
        )

    @require_auth
    @require_admin
    @handle_request
    def handle_list(self, db):
        groups = AccessGroupService.get_all(db)
        return {"data": [g.serialized for g in groups]}, 200

    @require_auth
    @require_admin
    @handle_request
    def handle_create(self, db):
        data = AccessGroupSchema().load((request.json or {}).get("data", {}))
        group = AccessGroupService.create(db, data["name"], created_by=session.get("user_id"))
        return {"data": group.serialized}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_rename(self, db, access_group_id):
        data = AccessGroupSchema().load((request.json or {}).get("data", {}))
        group = AccessGroupService.rename(db, access_group_id, data["name"])
        return {"data": group.serialized}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_delete(self, db, access_group_id):
        AccessGroupService.delete(db, access_group_id)
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_member(self, db, access_group_id):
        user_id = (request.json or {}).get("data", {}).get("user_id")
        if not user_id:
            return {"error": "user_id required"}, 400
        AccessGroupService.add_member(db, access_group_id, user_id)
        return {"msg": "OK"}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_remove_member(self, db, access_group_id, user_id):
        AccessGroupService.remove_member(db, access_group_id, user_id)
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_vendor(self, db, access_group_id):
        vendor_id = (request.json or {}).get("data", {}).get("vendor_id")
        if not vendor_id:
            return {"error": "vendor_id required"}, 400
        AccessGroupService.add_vendor(db, access_group_id, vendor_id)
        return {"msg": "OK"}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_remove_vendor(self, db, access_group_id, vendor_id):
        AccessGroupService.remove_vendor(db, access_group_id, vendor_id)
        return {"msg": "OK"}, 200
