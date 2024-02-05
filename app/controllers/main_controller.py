from datetime import date
from flask import Blueprint, request
import logging
import json
import requests

from app.controllers import main_blueprint
from app.vendor_factory import VendorFactory
from flask_socketio import join_room
from app.socketio_singleton import SocketioSingleton
from app.services.order_service import OrderService
from app.services.vendor_service import VendorService


socketio = SocketioSingleton.get_instance()

@main_blueprint.route('/', defaults={'path': ''},)
@main_blueprint.route('/<path:path>')
def catch_all(path):
    if True:
        return requests.get('http://127.0.0.1:8080/{}'.format(path)).text
    return render_template('../../frontend/dist/index.html')


@main_blueprint.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "Refreshed", 200

@main_blueprint.route('/get_vendors')
def handle_get_vendors():
    registered_vendors = VendorService.get_vendors()
    active_vendors = VendorFactory.get_vendor_objects()
    result_dict = {key: value for key, value in registered_vendors.items() if key in active_vendors}
    return json.dumps(result_dict)

@main_blueprint.route('/get_vendors_obj')
def handle_get_vendors_obj():
    string = str(len(VendorFactory.get_vendor_objects())) + "//"
    for key,value in VendorFactory.get_vendor_objects().items():
        string += str(value.id)
        string += "-"
        string += value.code_name
        string += ',\n'
    return string

@main_blueprint.route('/clearclientsbasket')
def call_clear_clients_basket():
    socketio.emit('Clear Local Basket')
    return "OK"


@socketio.on('connect')
def handle_connect():
    today = date.today().strftime('%Y-%m-%d')
    socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(today) }, to=request.sid)
    join_room(today)
    from app.controllers.user_controller import emit_user_ds_state
    emit_user_ds_state()
