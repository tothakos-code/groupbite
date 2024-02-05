from datetime import date
from flask import Blueprint, request
import logging
import json
import requests

from app.controllers import main_blueprint
from flask_socketio import join_room
from app.socketio_singleton import SocketioSingleton
from app.services.order_service import OrderService


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