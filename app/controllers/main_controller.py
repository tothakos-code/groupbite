from datetime import date
from flask import Blueprint, request, send_from_directory, render_template
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

from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
APP_ENV = getenv('APP_ENV')

socketio = SocketioSingleton.get_instance()

@main_blueprint.route('/')
def index():
    if APP_ENV == "development":
        # This is for developer mode only
        return requests.get('http://127.0.0.1:8080/').text
    return render_template('index.html')


@main_blueprint.route('/', defaults={'path': ''})
@main_blueprint.route('/<path:path>')
def catch_all(path):
    logging.info('Redirecting to Frontned...')
    if APP_ENV == "development":
        # This is for developer mode only
        return requests.get('http://127.0.0.1:8080/{0}'.format(path)).text
    return send_from_directory(main_blueprint.static_folder, path)

@main_blueprint.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "Refreshed", 200

@socketio.on('connect')
def handle_connect(auth=None):
    socketio.emit('be_vendors_update', VendorService.find_all_active())
    pass
