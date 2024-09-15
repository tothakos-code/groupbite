from flask import Blueprint, request
from flask_socketio import rooms
from sqlalchemy import func, cast, update
from datetime import datetime
import logging

from app.controllers import user_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities import Session
from app.entities.user import User
from app.entities.order import Order
from app.entities.user_basket import UserBasket
from app.utils.decorators import validate_url_params
from app.utils.validators import IDSchema


socketio = SocketioSingleton.get_instance()

@user_blueprint.route("/login", methods=["POST"])
def handle_user_login():
    username = request.json["username"]
    user_to_login = User.get_one_by_username(username)

    if not user_to_login:
        logging.error(f"Error during login: {username} user does not excist, cannot log in.")
        return { "error": f"{username} felhasználó nem létezik!" }

    logging.info(f"User {user_to_login.username} logged in!")
    return { "data": user_to_login.serialized }, 200


@user_blueprint.route("/checkSession", methods=["POST"])
def handle_user_check_session():
    user_id = request.json["session"]
    user_to_login = User.get_one_by_id(user_id)

    if not user_to_login:
        # user not found error
        logging.error(f"Error during login: {user_id} user id does not excist, cannot log in.")
        return { "error": f"{user_id} felhasználó nem létezik!" }

    logging.info(f"User {user_to_login.username} logged in!")
    return { "data":user_to_login.serialized }, 200


@user_blueprint.route("/register", methods=["POST"])
def handle_user_register():
    username = request.json["username"]
    email = request.json["email"]

    is_username_valid, username_error = User.is_username_valid(username)
    is_email_valid, email_error = User.is_email_valid(email)

    if not is_username_valid:
        return { "error": username_error }

    if not is_email_valid:
        return { "error": email_error }

    ok, user_to_register = User.create_user(User(username=username, email=email, settings={}))
    if ok:
        logging.info(f"User {user_to_register.username} created!")
        return { "data": user_to_register.serialized }, 201
    else:
        return { "error": "Failed to register, something wrong with the data you provided" }, 400


@user_blueprint.route("/<user_id>", methods=["PUT"])
@validate_url_params(IDSchema())
def handle_user_update(user_id):
    user = request.json["data"]

    user_to_update = User.get_one_by_id(user_id)

    if "username" in user:
        is_username_valid, error = User.is_username_valid(user["username"])
        if is_username_valid:
            user_to_update.update_user(user)
            logging.info("Updated User: " + str(user["id"]))
        else:
            logging.info("Invalid user update: " + error)
            return { "error": error }

    if "username" in user:
        logging.info("Updating username in rooms")
        # Updating the username in every basket(room) a user is in
        for room_name,room in socketio.server.manager.rooms["/"].items():
            if room_name != None and "@" in room_name:

                vendor, date = room_name.split("@")
                # TODO: check if user has items in that oreder, and only update them
                order = Order.find_order_by_date_for_a_vendor(vendor, date)
                socketio.emit(
                    "be_order_update", {
                        "basket": UserBasket.get_basket_group_by_user(order.id)
                    },
                    to=room_name
                )

    return { "data": user_to_update.serialized }, 200

# TODO: add a limit and a pager option, move to user controller
@user_blueprint.route("/<user_id>/orders", methods=["GET"])
@validate_url_params(IDSchema())
def handle_user_order_history(user_id):

    result = {}
    for item in UserBasket.find_user_orders(user_id):
        date = item.order.date_of_order.strftime("%Y-%m-%d")
        vendor = item.order.vendor.name
        key_format = f"{vendor}-{date}"
        if key_format not in result:
            result[key_format] = {}

        if "items" not in result[key_format]:
            result[key_format]["items"] = []

        result[key_format]["items"].append(item.basket_format)
        result[key_format]["vendor"] = vendor
        result[key_format]["date"] = date
        result[key_format]["fee"] = item.order.order_fee/UserBasket.user_count(item.order.id)

    return { "data": result }, 200
