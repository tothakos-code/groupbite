from flask import Blueprint, request
import json
import logging

from app.entities.menu_item import MenuItem
from app.entities.size import Size, BaseSizeSchema, UpdateSizeSchema
from app.controllers import size_blueprint
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


@size_blueprint.route("", methods=["POST"])
@validate_data(BaseSizeSchema())
@require_auth
@require_admin
def handle_menu_item_size_add(data):
    if not MenuItem.find_by_id(data["menu_item_id"]):
        logging.warning("MenuItem not found")
        return { "error": "MenuItem not found" }, 400

    if not Size.add(Size(
        menu_item_id = data["menu_item_id"],
        link         = data["link"] if "link" in data else "",
        name         = data["name"],
        price        = data["price"],
        quantity        = data["quantity"],
        unlimited     = data["unlimited"])):
        return { "error": "Bad request or somthing went wrong" }, 400

    return { "msg": "OK" }, 201


@size_blueprint.route("<size_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@validate_data(UpdateSizeSchema())
@require_auth
@require_admin
def handle_menu_item_size_update(data, size_id):
    size_db = Size.find_by_id(size_id)

    if not size_db.update(
        data["name"],
        data["price"],
        data["quantity"],
        data["unlimited"],
        data["index"]):
        return { "error": "Something went wrong" }, 400

    return { "data": json.dumps(size_db.serialized) }, 200


@size_blueprint.route("/<size_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_item_size_delete(size_id):
    if not Size.find_by_id(size_id).delete():
        return { "error": "IntegrityError" }, 400
    return { "msg": "OK" }, 200
