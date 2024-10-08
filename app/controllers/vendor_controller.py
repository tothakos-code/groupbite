from datetime import date
from flask import Blueprint, request
import logging
import json
import requests

from app.base_vendor import BaseVendor

from app.controllers import vendor_blueprint
from app.vendor_factory import VendorFactory

from app.socketio_singleton import SocketioSingleton

from app.services.vendor_service import VendorService
from app.entities.vendor import Vendor, BaseVendorSchema
from app.entities.menu import Menu
from app.utils.decorators import validate_data, validate_url_params
from app.utils.validators import IDSchema

socketio = SocketioSingleton.get_instance()

@vendor_blueprint.route("", methods=["GET"])
def handle_get_all_vendors():
    result = []
    for a in Vendor.find_all():
        result.append(a.serialized)
    return {"data": result}, 200

@vendor_blueprint.route("/<vendor_id>/activate", methods=["PUT"])
@validate_url_params(IDSchema())
def handle_activation(vendor_id):
    Vendor.find_by_id(vendor_id).activate()
    logging.info(vendor_id + " vendor got activated")

    socketio.emit("be_vendors_update", VendorService.find_all_active())
    return { "msg": "OK" }, 200

@vendor_blueprint.route("/<vendor_id>/deactivate", methods=["PUT"])
@validate_url_params(IDSchema())
def handle_deactivation(vendor_id):
    Vendor.find_by_id(vendor_id).deactivate()
    logging.info(vendor_id + " vendor got deactivated")

    socketio.emit("be_vendors_update", VendorService.find_all_active())
    return { "msg": "OK" }, 200


@vendor_blueprint.route("", methods=["POST"])
@validate_data(BaseVendorSchema())
def handle_create(data):
    vendor_json = request.json["data"]
    logging.debug(vendor_json)

    vendor_obj = BaseVendor(
        vendor_json["name"],
        settings=vendor_json["settings"]
        )

    VendorFactory.register(vendor_obj)

    vendor_db = Vendor.find_by_id(vendor_obj.id)
    return { "data": vendor_db.serialized }, 200


@vendor_blueprint.route("/<vendor_id>/scan", methods=["GET"])
@validate_url_params(IDSchema())
def handle_run_scan(vendor_id):
    vendor = VendorFactory.get_one_vendor_object(vendor_id)
    try:
        vendor.scan()
    except NotImplementedError as e:
        return { "error": f"Vendor {vendor_id} does not support automatic menu filling" }, 405
    return { "msg": f"Vendor scan ran for {vendor_id} id" }, 201


@vendor_blueprint.route("/<vendor_id>", methods=["GET"])
@validate_url_params(IDSchema())
def handle_get_settings(vendor_id):
    vendor = Vendor.find_by_id(vendor_id)

    return { "data": vendor.serialized }, 200

# TODO: data validation
@vendor_blueprint.route("/<vendor_id>/settings", methods=["PUT"])
@validate_url_params(IDSchema())
def handle_save_settings(vendor_id):
    settings = request.json["data"]
    vendor = Vendor.find_by_id(vendor_id)
    vendor.update_settings(settings)
    socketio.emit("be_vendors_update", VendorService.find_all_active())

    return { "data": vendor.settings }, 200


@vendor_blueprint.route("/<vendor_id>/menus", methods=["GET"])
@validate_url_params(IDSchema())
def handle_menu_get(vendor_id):
    menus = Menu.find_all_by_vendor(vendor_id)
    result = []
    for m in menus:
        result.append(m.serialized)

    return { "data": result }, 200

@vendor_blueprint.route("/<vendor_id>/menus/date/<menu_date>", methods=["GET"])
@validate_url_params(IDSchema())
def get_requested_menu(vendor_id, menu_date):
    filter = request.args.getlist('filter[]')

    vendor = VendorFactory.get_one_vendor_object(str(vendor_id))

    return { "data": vendor.get_menu(menu_date, filter) }, 200

@vendor_blueprint.route("/<vendor_id>/menus/import", methods=["POST"])
@validate_url_params(IDSchema())
def import_menu(vendor_id):
    if "file" not in request.files:
        return { "error": "No file part in the request" }, 400

    json_file = request.files["file"]

    if json_file.filename == "":
        return { "error": "No file selected for uploading" }, 400

    try:
        file_content = json.loads(json_file.read())
        for menu in file_content["menus"]:
            menu_db = Menu(
                name=menu["name"] if "name" in menu else "imported-" + datetime.now().strftime("%Y-%m-%d-%H:%M"),
                vendor_id=vendor_id,
                freq_id=menu["freq"] if "freq" in menu else "DAILY",
                date=menu["date"] if "date" in menu else date.today().strftime("%Y-%m-%d")
            )

            item_index = 0
            for item in menu["items"]:
                menu_item = MenuItem(
                    name=item["name"],
                    category=item["category"] if "category" in item else "",
                    index=item["index"] if "index" in item else item_index
                )
                if "index" not in item:
                    item_index+= 1

                size_index=0
                for size in item["sizes"]:
                    menu_item.sizes.append(Size(
                        link="",
                        name=size["name"],
                        price=size["price"],
                        index=size["index"] if "index" in size else size_index,
                        quantity=size["quantity"] if "quantity" in size else -1,
                    ))
                    if "index" not in size:
                        size_index+= 1

                menu_db.items.append(menu_item)
            Menu.add(menu_db)

    except Exception as e:
        return { "error": "Failed to parse JSON file" }, 400
    return { "msg": "OK" }, 201
