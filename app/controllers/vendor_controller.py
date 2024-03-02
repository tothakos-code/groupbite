from datetime import date
from flask import Blueprint, request
import logging
import json
import requests

from app.controllers import vendor_blueprint
from app.vendor_factory import VendorFactory

from app.services.vendor_service import VendorService
from app.entities.vendor import Vendor


@vendor_blueprint.route('/find-all-active')
def handle_get_active_vendors():
    result = []
    for a in Vendor.find_all_active():
        result.append(a.serialized)
    return json.dumps(result)

@vendor_blueprint.route('/find-all')
def handle_get_all_vendors():
    result = []
    for a in Vendor.find_all():
        result.append(a.serialized)
    return json.dumps(result)
@vendor_blueprint.route('/get_vendors_obj')
def handle_get_vendors_obj():
    string = str(len(VendorFactory.get_vendor_objects())) + "//"
    for key,value in VendorFactory.get_vendor_objects().items():
        string += str(value.id)
        string += "-"
        string += value.code_name
        string += ',\n'
    return string

