from datetime import date, datetime
from flask import Blueprint, request, session
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
from app.entities.user import User
from app.entities.notification import Notification, NotificationType
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema

socketio = SocketioSingleton.get_instance()

@vendor_blueprint.route("", methods=["GET"])
@require_auth
@require_admin
def handle_get_all_vendors():
    result = []
    for a in Vendor.find_all():
        result.append(a.serialized)
    return {"data": result}, 200

@vendor_blueprint.route("/<vendor_id>/activate", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_activation(vendor_id):
    Vendor.find_by_id(vendor_id).activate()
    logging.info(vendor_id + " vendor got activated")

    socketio.emit("be_vendors_update", VendorService.find_all_active())
    return { "msg": "OK" }, 200

@vendor_blueprint.route("/<vendor_id>/deactivate", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_deactivation(vendor_id):
    Vendor.find_by_id(vendor_id).deactivate()
    logging.info(vendor_id + " vendor got deactivated")

    socketio.emit("be_vendors_update", VendorService.find_all_active())
    return { "msg": "OK" }, 200

@vendor_blueprint.route("/<vendor_id>/notifications/<notification_type>/subscribe", methods=["POST"])
@validate_url_params(IDSchema())
@require_auth
def handle_notification_subscribe(vendor_id, notification_type):
    user_id = session.get('user_id')
    notification_json = request.json["data"]
    Notification.add(Notification(
        vendor_id=vendor_id,
        user_id=user_id,
        notification_type=NotificationType(notification_type),
        endpoint=notification_json["endpoint"],
        p256dh=notification_json["keys"]["p256dh"],
        auth=notification_json["keys"]["auth"]

    ))
    socketio.emit("be_user_update", User.get_one_by_id(user_id).serialized)

    return { "msg": "OK" }, 200

@vendor_blueprint.route("/<vendor_id>/notifications/<notification_type>/unsubscribe", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
def handle_notification_unsubscribe(vendor_id, notification_type):
    user_id = session.get('user_id')
    notifications = Notification.find_by_vendor_id_user_id(vendor_id, user_id, NotificationType(notification_type))
    for noti in notifications:
        if noti.delete():
            socketio.emit("be_user_update", User.get_one_by_id(user_id).serialized)
            return { "msg": "OK" }, 200
        else:
            return { "error": "Someting went wrong" }, 500


@vendor_blueprint.route("/<vendor_id>/notifications/<notification_type>", methods=["GET"])
@validate_url_params(IDSchema())
def handle_notification_status(vendor_id, notification_type):
    user_id = session.get('user_id')
    if not user_id:
        return {
            "data": {
                 "status": False
            }
        }, 200
    notification = Notification.find_by_pk(vendor_id, user_id, notification_type)
    if notification:
        return {
            "data": {
                 "status": True
            }
        }, 200
    else:
        return {
            "data": {
                 "status": False
            }
        }, 200




@vendor_blueprint.route("", methods=["POST"])
@validate_data(BaseVendorSchema())
@require_auth
@require_admin
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
    menu_date = request.args.get('menu_date')
    try:
        datetime.strptime(menu_date, '%Y-%m-%d')
    except ValueError as e:
        menu_date = None
    logging.info(menu_date)

    vendor = VendorFactory.get_one_vendor_object(vendor_id)
    try:
        if menu_date != None:
            vendor.scan(menu_date=menu_date)
        else:
            vendor.scan()
    except NotImplementedError as e:
        return { "error": f"Vendor {vendor_id} does not support automatic menu filling" }, 405
    return { "msg": f"Vendor scan ran for {vendor_id} id" }, 201


@vendor_blueprint.route("/<vendor_id>", methods=["GET"])
@validate_url_params(IDSchema())
def handle_get_settings(vendor_id):
    vendor = Vendor.find_by_id(vendor_id)

    return { "data": vendor.serialized }, 200


@vendor_blueprint.route("/<vendor_id>/settings", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_save_settings(vendor_id):
    settings = request.json["data"]
    vendor = Vendor.find_by_id(vendor_id)
    vendor.update_settings(settings)
    socketio.emit("be_vendors_update", VendorService.find_all_active())

    return { "data": vendor.settings }, 200


@vendor_blueprint.route("/<vendor_id>/menus", methods=["GET"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_get(vendor_id):
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
    menus = Menu.find_all_by_vendor(vendor_id, search, limit, offset)
    total_count = Menu.count_by_vendor_id(vendor_id)
    result = []
    for m in menus:
        result.append(m.serialized)

    return { "data": {
        "menus": result,
        "page": page,
        "limit": limit,
        "total_count": total_count
        }
    }, 200

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
                from_date=menu["from_date"] if "from_date" in menu else date.today().strftime("%Y-%m-%d"),
                to_date=menu["to_date"] if "to_date" in menu else date.today().strftime("%Y-%m-%d")
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
