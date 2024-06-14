from flask import Blueprint, request
from flask_socketio import rooms
from sqlalchemy import func, cast, update
from datetime import datetime
import logging

from app.controllers import user_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities import Session
from app.entities.subscribed import SubscriptionType
from app.entities.user import User
from app.entities.order import Order
from app.services.user_service import UserService
from app.services.order_service import OrderService

socketio = SocketioSingleton.get_instance()

@user_blueprint.route("/login", methods=['POST'])
def handle_user_login():
    user_id = request.json['user']
    user_to_login = User.get_one_by_id(user_id)

    if not user_to_login:
        # user not found error
        logging.error(f"Error during login: {user_id} user id does not excist, cannot log in.")

    logging.info(f"User {user_to_login.username} logged in!")
    return user_to_login.serialized

@user_blueprint.route("/register", methods=['POST'])
def handle_user_register():
    username = request.json['username']
    user_to_register = User.get_one_by_username(username)

    if user_to_register:
        logging.warn(f"Username elready taken: {username}")

    user_to_register = User.create_user(User(username=username, settings={}))
    logging.info(f"User {user_to_register.username} created!")

    return user_to_login.serialized

@user_blueprint.route("/update", methods=['POST'])
def handle_user_update():
    user = request.json['user']
    logging.info("Updated User: " + str(user['id']))

    user_to_update = User.get_one_by_id(user['id'])

    if 'username' in user:
        is_username_valid, error = User.is_username_valid(user['username'])
        if is_username_valid:
            user_to_update.update_user(user)

        else:
            return {"error": error}

    logging.info("Szobák:")
    logging.info(socketio.server.manager.rooms['/'])
    if 'username' in user:
        # Updating the username in every basket(room) a user is in
        for room_name,room in socketio.server.manager.rooms['/'].items():
            if room_name != None and '_' in room_name:
                logging.info(room_name)
                logging.info(room)
                vendor, date = room_name.split('_')
                # TODO: check if user has items in that oreder, and only update them
                order = Order.find_order_by_date_for_a_vendor(vendor, date)
                socketio.emit(
                    'be_order_update', {
                        'basket': OrderService.get_formated_full_basket_group_by_user(order.id)
                    },
                    to=room_name
                )

    return user_to_update.serialized


@user_blueprint.route("/get/<id>")
def handle_get_user_by_id(id):
    user = UserService.get_user_by_id(id)
    if not user:
        return {}
    return user.serialized
