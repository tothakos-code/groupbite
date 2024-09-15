from flask import Blueprint, request
from datetime import date, timedelta, datetime
import json
import logging

from app.controllers import menu_blueprint
from app.entities.menu import Menu, BaseMenuSchema, UpdateMenuSchema
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.services.vendor_service import VendorService
from app.vendor_factory import VendorFactory
from app.base_vendor import BaseVendor
from app.utils.decorators import validate_data


    if not Menu.find_by_id(menu_id):
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    items = MenuItem.find_all_by_menu(menu_id)
    result = []

    for i in items:
        result.append(i.serialized)

    return json.dumps(result), 200


@menu_blueprint.route("/<vendor_id>/menu-get", methods=["GET"])
def handle_menu_get(vendor_id):
    menus = Menu.find_all_by_vendor(vendor_id)
    result = []
    for m in menus:
        result.append(m.serialized)
    return json.dumps(result), 200


@menu_blueprint.route("/<menu_id>/update", methods=["POST"])
@validate_data(UpdateMenuSchema())
def handle_menu_update(data, menu_id):
    menu_db = Menu.find_by_id(menu_id)
    if not menu_db:
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    if not menu_db.update(data["name"], data["date"]):
        return {"error": "Bad request"}, 400

    return json.dumps(menu_db.serialized), 200


@menu_blueprint.route("/<menu_id>/delete", methods=["POST"])
@validate_data(UpdateMenuSchema())
def handle_menu_delete(data, menu_id):
    if not menu_id.isnumeric():
        return {"error": "Bad request"}, 400

    if not Menu.find_by_id(menu_id):
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    if not Menu.find_by_id(menu_id).delete():
        return {"error": "IntegrityError"}, 400
    return {"msg": "OK"}, 200


@menu_blueprint.route("/<menu_id>/duplicate", methods=["POST"])
@validate_data(UpdateMenuSchema())
def handle_menu_duplicate(data, menu_id):
    original_menu = Menu.find_by_id(data["id"])

    menu_db = Menu(
        name=original_menu.name+"-copy",
        vendor_id=original_menu.vendor_id,
        freq_id=original_menu.freq_id,
        date=date.today().strftime("%Y-%m-%d"),
        active=False
    )

    for item in original_menu.items:
        menu_item = MenuItem(
            name=item.name,
            category=item.category,
            index=item.index
        )

        for size in item.sizes:
            menu_item.sizes.append(Size(
                link=size.link,
                name=size.name,
                price=size.price,
                index=size.index,
                quantity=size.quantity
            ))


        menu_db.items.append(menu_item)
    if not Menu.add(menu_db):
        return {"error": "Bad request"}, 400
    return {"msg": "OK"}, 200


@menu_blueprint.route("/<menu_id>/add", methods=["POST"])
@validate_data(BaseMenuSchema())
def handle_menu_add(data, menu_id):
    if not Menu.add(Menu(name=data["name"], vendor_id=data["vendor_id"], freq_id=data["freq"])):
        return {"error": "Bad request"}, 400
    return {"msg": "OK"}, 201


@menu_blueprint.route("/<menu_id>/activate", methods=["GET"])
def handle_activation(menu_id):
    if not menu_id:
        return "Menu not found", 404

    menu = Menu.find_by_id(menu_id)
    if not menu:
        return "Menu not found", 404

    menu.activate()
    logging.info(menu_id + " vendor got activated")
    return "OK", 200


@menu_blueprint.route("/<menu_id>/deactivate", methods=["GET"])
def handle_deactivation(menu_id):
    if not menu_id:
        return "Menu not found", 404

    menu = Menu.find_by_id(menu_id)
    if not menu:
        return "Menu not found", 404

    menu.deactivate()
    logging.info(menu_id + " vendor got deactivated")

    return "OK", 200
