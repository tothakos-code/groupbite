from flask import Flask
from flask import request
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
import logging
import datetime
import db
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True)
app.config['SECRET_KEY'] = 'secret!'

from controllers.menu_controller import menu_controller
from controllers.order_controller import order_controller, get_today_basket
from controllers.user_controller import user_controller, emit_user_ds_state
app.register_blueprint(menu_controller)
app.register_blueprint(order_controller)
app.register_blueprint(user_controller)


@app.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "OK", 200

@app.route('/')
def call_hello():
    return "Welcome to this api on a pi!"

@app.route('/clearclientsbasket')
def call_clear_clients_basket():
    socketio.emit('Clear Local Basket')
    return "OK"


@socketio.on('connect')
def handle_connect(data):
    socketio.emit('Client Basket Update', {'basket': get_today_basket() })
    emit_user_ds_state()


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
