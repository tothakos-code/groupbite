from flask import Blueprint, request
import json
import logging

from app.entities.menu_item import MenuItem, BaseItemSchema, UpdateItemSchema
from app.entities.menu import Menu
from app.controllers import item_blueprint
from app.utils.decorators import validate_data, validate_url_params
from app.utils.validators import IDSchema


@item_blueprint.route("", methods=["POST"])
@validate_data(BaseItemSchema())
def handle_menu_item_add(data):
    if not Menu.find_by_id(data["menu_id"]):
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    ok, item = MenuItem.add(MenuItem(
        menu_id  = data["menu_id"],
        name     = data["name"],
        description     = data["description"],
        category = data["category"]))

    if not ok:
        return { "error": "Bad request" }, 400

    return { "msg": "OK", "data": item.serialized }, 201


@item_blueprint.route("/<item_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@validate_data(UpdateItemSchema())
def handle_menu_item_update(data, item_id):
    menu_item = MenuItem.find_by_id(item_id)

    if not menu_item.update(
        data["name"],
        data["description"],
        data["index"],
        data["category"]):
        return { "error": "Bad request" }, 400

    return { "msg": "OK" }, 200


@item_blueprint.route("/<item_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
def handle_menu_item_delete(item_id):
    if not MenuItem.find_by_id(item_id).delete():
        return { "error": "IntegrityError" }, 400
    return { "msg": "OK" }, 200
