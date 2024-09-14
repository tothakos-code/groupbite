from flask import Blueprint, request
import json
import logging

from app.entities.menu_item import MenuItem
from app.entities.size import Size, BaseSizeSchema, UpdateSizeSchema
from app.controllers import size_blueprint
from app.utils.decorators import validate_data


@size_blueprint.route("/add", methods=["POST"])
@validate_data(BaseSizeSchema())
def handle_menu_item_size_add(data):
    if not MenuItem.find_by_id(data["menu_item_id"]):
        logging.warning("MenuItem not found")
        return {"error": "MenuItem not found"}, 400

    if not Size.add(Size(
        menu_item_id = data["menu_item_id"],
        link         = data["link"] if "link" in data else "",
        name         = data["name"],
        price        = data["price"],
        quantity     = data["quantity"])):
        return {"error": "Bad request"}, 400

    return {"msg": "OK"}, 201


@size_blueprint.route("/update", methods=["POST"])
@validate_data(UpdateSizeSchema())
def handle_menu_item_size_update(data):
    size_db = Size.find_by_id(data["id"])
    if size_db:
        size_db.update(
            data["name"],
            data["price"],
            data["quantity"],
            data["index"])
    else:
        menu_item = MenuItem.find_by_id(data["menu_item_id"])

        if not menu_item:
            logging.warning("MenuItem not found")
            return {"error": "MenuItem not found"}, 400

        size_db = Size(
            menu_item_id = data["menu_item_id"],
            link         = data["link"] if "link" in data else "",
            name         = data["name"],
            price        = data["price"],
            quantity     = data["quantity"],
            index        = data["index"])

        if not Size.add(size_db):
            return {"error": "Bad request"}, 400

    return json.dumps(size_db.serialized), 200


@size_blueprint.route("/delete", methods=["POST"])
@validate_data(UpdateSizeSchema())
def handle_menu_item_size_delete(data):
    if not Size.find_by_id(data["id"]).delete():
        return {"error": "IntegrityError"}, 400
    return {"msg": "OK"}, 200
