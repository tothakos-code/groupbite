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

    if cmd == "activate":
        Vendor.find_by_id(vendor_id).activate()
        logging.info(vendor_id + " vendor got activated")
    elif cmd == "deactivate":
        Vendor.find_by_id(vendor_id).deactivate()
        logging.info(vendor_id + " vendor got deactivated")
    else:
        return "Command not found", 404
        
    socketio.emit('be_vendors_update', VendorService.find_all_active())
    return "OK", 200

@vendor_blueprint.route('/create', methods=['POST'])
def handle_create():
    vendor_json = request.json['data']
    logging.debug(vendor_json)

    vendor_obj = BaseVendor(
        vendor_json['name'],
        settings=vendor_json['settings']
        )

    VendorFactory.register(vendor_obj)

    vendor_db = Vendor.find_by_id(vendor_obj.id)
    return vendor_db.serialized

@vendor_blueprint.route('/<vendor_id>/scan')
def handle_run_scan(vendor_id):
    vendor = VendorFactory.get_one_vendor_object(vendor_id)
    if vendor is None:
        return "No vendor found"
    vendor.scan()
    return "OK"

@vendor_blueprint.route('/<vendor_id>/get')
def handle_get_settings(vendor_id):
    vendor = Vendor.find_by_id(vendor_id)
    if vendor is None:
        return "No vendor found"
    return vendor.serialized

@vendor_blueprint.route('/<vendor_id>/settings/save', methods=['POST'])
def handle_save_settings(vendor_id):
    settings = request.json['data']
    vendor = Vendor.find_by_id(vendor_id)
    if vendor is None:
        return "No vendor found"
    vendor.update_settings(settings)
    socketio.emit('be_vendors_update', VendorService.find_all_active())

    return vendor.settings
