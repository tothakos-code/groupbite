from flask import Blueprint, request
import json
import logging

from app.entities.menu_item import MenuItem, BaseItemSchema, UpdateItemSchema
from app.entities.menu import Menu
from app.controllers import item_blueprint
from app.utils.decorators import validate_data



@item_blueprint.route("/add", methods=["POST"])
@validate_data(BaseItemSchema())
def handle_menu_item_add(data):
    if not Menu.find_by_id(data["menu_id"]):
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    ok, item = MenuItem.add(MenuItem(
        menu_id  = data["menu_id"],
        name     = data["name"],
        category = data["category"]))

    if not ok:
        return {"error": "Bad request"}, 400

    return {"msg": "OK", "item": item.serialized}, 201


@item_blueprint.route("/update", methods=["POST"])
@validate_data(UpdateItemSchema())
def handle_menu_item_update(data):
    menu_item = MenuItem.find_by_id(data["id"])

    if not menu_item:
        logging.warning("MenuItem not found")
        return {"error": "MenuItem not found"}, 400

    if not menu_item.update(
        data["name"],
        data["index"],
        data["category"]):
        return {"error": "Bad request"}, 400

    return {"msg": "OK"}, 200


@item_blueprint.route("/delete", methods=["POST"])
@validate_data(UpdateItemSchema())
def handle_menu_item_delete(data):
    if not MenuItem.find_by_id(data["id"]).delete():
        return {"error": "IntegrityError"}, 400
    return {"msg": "OK"}, 200
