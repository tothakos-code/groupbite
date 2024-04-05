from datetime import date
from flask import Blueprint, request
import logging
import json
import requests

from app.controllers import vendor_blueprint
from app.vendor_factory import VendorFactory

from app.socketio_singleton import SocketioSingleton

from app.services.vendor_service import VendorService
from app.entities.vendor import Vendor

socketio = SocketioSingleton.get_instance()

@vendor_blueprint.route('/find-all-active')
def handle_get_active_vendors():
    socketio.emit('be_vendors_update', VendorService.find_all_active())
    return "OK"

@vendor_blueprint.route('/find-all')
def handle_get_all_vendors():
    result = []
    for a in Vendor.find_all():
        result.append(a.serialized)
    return json.dumps(result)

@vendor_blueprint.route('/<vendor_id>/<cmd>', methods=['POST'])
def handle_activation(vendor_id, cmd):
    if not vendor_id:
        return "Vendor not found", 404
    match cmd:
        case "activate":
            Vendor.find_by_id(vendor_id).activate()
            logging.info(vendor_id + " vendor got activated")
        case "deactivate":
            Vendor.find_by_id(vendor_id).deactivate()
            logging.info(vendor_id + " vendor got deactivated")
        case _:
            return "Command not found", 404
    socketio.emit('be_vendors_update', VendorService.find_all_active())
    return "OK", 200


@vendor_blueprint.route('/get_vendors_obj')
def handle_get_vendors_obj():
    string = str(len(VendorFactory.get_vendor_objects())) + "//"
    for key,value in VendorFactory.get_vendor_objects().items():
        string += str(value.id)
        string += "-"
        string += value.code_name
        string += ',\n'
    return string

@vendor_blueprint.route('/<vendor_id>/scan')
def handle_run_scan(vendor_id):
    vendor = VendorFactory.get_one_vendor_object(str(vendor_id))
    if vendor is None:
        return "No vendor found"
    vendor.scan()
    return "OK"

@vendor_blueprint.route('/<vendor_id>/settings/get')
def handle_get_settings(vendor_id):
    vendor = Vendor.find_by_id(str(vendor_id))
    if vendor is None:
        return "No vendor found"
    return vendor.settings

@vendor_blueprint.route('/<vendor_id>/settings/save', methods=['POST'])
def handle_save_settings(vendor_id):
    settings = request.json['data']
    vendor = Vendor.find_by_id(vendor_id)
    if vendor is None:
        return "No vendor found"
    vendor.update_settings(settings)
    return vendor.settings
