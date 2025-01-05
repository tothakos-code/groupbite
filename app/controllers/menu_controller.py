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
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


@menu_blueprint.route("/<menu_id>", methods=["GET"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_get_items(menu_id):
    try:
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
    except ValueError as e:
        limit = 10
        page = 1
    except TypeError as e:
        limit = 10
        page = 1
    offset = 0 if page is None else limit * (page - 1)
    search = request.args.get('search')
    items = MenuItem.find_all_by_menu(menu_id, search, limit, offset)
    total_count = MenuItem.count_by_menu_id(menu_id)
    result = []

    for i in items:
        result.append(i.serialized)

    return { "data": {
        "items": result,
        "page": page,
        "limit": limit,
        "total_count": total_count
        }
    }, 200


@menu_blueprint.route("/<menu_id>", methods=["PUT"])
@validate_data(UpdateMenuSchema())
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_update(data, menu_id):
    menu_db = Menu.find_by_id(menu_id)

    if not menu_db.update(data["name"], data["date"]):
        return { "error": "Bad request" }, 400

    return { "data": json.dumps(menu_db.serialized) }, 200


@menu_blueprint.route("/<menu_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_delete(menu_id):
    if not Menu.find_by_id(menu_id).delete():
        return { "error": "IntegrityError" }, 400
    return { "msg": "OK" }, 200


@menu_blueprint.route("/<menu_id>/duplicate", methods=["POST"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_duplicate(menu_id):
    original_menu = Menu.find_by_id(menu_id)

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
            description=item.description,
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
        return { "error": "Bad request" }, 400
    return { "msg": "OK" }, 200


@menu_blueprint.route("", methods=["POST"])
@validate_data(BaseMenuSchema())
@require_auth
@require_admin
def handle_menu_add(data):
    if not Menu.add(Menu(name=data["name"], vendor_id=data["vendor_id"], freq_id=data["freq"])):
        return { "error": "Bad request" }, 400
    return { "msg": "OK" }, 201


@menu_blueprint.route("/<menu_id>/activate", methods=["GET"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_activation(menu_id):
    menu = Menu.find_by_id(menu_id)
    menu.activate()
    logging.info(menu_id + " vendor got activated")
    return { "msg": "OK" }, 200


@menu_blueprint.route("/<menu_id>/deactivate", methods=["GET"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_deactivation(menu_id):
    menu = Menu.find_by_id(menu_id)
    menu.deactivate()
    logging.info(menu_id + " vendor got deactivated")

    return { "msg": "OK" }, 200
