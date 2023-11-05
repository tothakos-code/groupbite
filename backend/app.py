# MIT License
#
# Copyright (c) 2023 Akos Toth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask
from flask import request
from flask_socketio import SocketIO, join_room
import logging
from sqlalchemy.exc import IntegrityError
from datetime import date

app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True, cors_allowed_origins="*")
app.config['SECRET_KEY'] = 'secret!'

from controllers.menu_controller import menu_controller
from controllers.order_controller import order_controller
from controllers.user_controller import user_controller, emit_user_ds_state
from services.order_service import OrderService

app.register_blueprint(menu_controller)
app.register_blueprint(order_controller)
app.register_blueprint(user_controller)


@app.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "Refreshed", 200

@app.route('/')
def call_hello():
    return "Welcome to this api on a pi!"

@app.route('/clearclientsbasket')
def call_clear_clients_basket():
    socketio.emit('Clear Local Basket')
    return "OK"


@socketio.on('connect')
def handle_connect():
    today = date.today().strftime('%Y-%m-%d')
    socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(today) }, to=request.sid)
    join_room(today)
    emit_user_ds_state()


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
