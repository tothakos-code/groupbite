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
from app.entities.vendor import Vendor


socketio = SocketioSingleton.get_instance()

@main_blueprint.route('/', defaults={'path': ''})
@main_blueprint.route('/<path:path>')
def catch_all(path):
    logging.info('Redirecting to Frontned...')
    if True:
        # This is for developer mode only
        return requests.get('http://127.0.0.1:8080/{0}'.format(path)).text
    return render_template('../../frontend/dist/index.html')

@main_blueprint.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "Refreshed", 200

@socketio.on('connect')
def handle_connect(auth=None):
    socketio.emit('be_vendors_update', VendorService.find_all_active())

    # socketio.emit('Client Basket Update', OrderService.get_formated_full_basket(order_id), to=request.sid)
    # today = date.today().strftime('%Y-%m-%d')
    # join_room(today)
    pass
