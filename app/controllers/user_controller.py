from flask import Blueprint, request, session, current_app
from flask_socketio import rooms
from sqlalchemy import func, cast, update
from datetime import datetime
import logging
import re
from app.controllers import user_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities import Session
from app.entities.user import User
from app.entities.order import Order
from app.entities.user_basket import UserBasket
from app.utils.decorators import validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


socketio = SocketioSingleton.get_instance()

@user_blueprint.route("/login", methods=["POST"])
def handle_user_login():
    user_id = session.get('user_id')
    if user_id:
        user_to_login = User.get_one_by_id(user_id)
        current_app.session_interface.regenerate(session)
        session.modified = True
        logging.info(f"User already {user_to_login.username} logged in!")
        return { "data": user_to_login.serialized }, 200

    username = request.json["username"]
    user_to_login = User.get_one_by_username(username)
    if not user_to_login:
        logging.error(f"Error during login: {username} user does not excist, cannot log in.")
        return { "error": f"{username} felhasználó nem létezik!" }


    session["user_id"] = user_to_login.id

    logging.info(f"User {user_to_login.username} logged in!")
    return { "data": user_to_login.serialized }, 200

@require_auth
@user_blueprint.route("/logout", methods=["POST"])
def handle_user_logout():
    user_id = session.get('user_id')
    if user_id:
        session.clear()
        return { "msg": "Logged out successfully" }, 200
    else:
        logging.warning("Logout attempt without a user logged in.")
        return { "error": "No user is logged in." }, 400


@user_blueprint.route("/checkSession", methods=["GET"])
def handle_user_check_session():
    user_id = session.get('user_id')
    if user_id:
        user_to_login = User.get_one_by_id(user_id)
        current_app.session_interface.regenerate(session)
        session.modified = True
        logging.info(f"User already {user_to_login.username} got a session!")
        return { "data": user_to_login.serialized }, 200
    else:
        return { "error": f"{user_id} nincs bejelentkezve!" }, 200

@user_blueprint.route("/reminder", methods=["GET"])
def handle_reminder():
    email = request.args.get('email')
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        return { "error": "Helytelen email formátum" }, 200

    user = User.get_one_by_email(email)
    if user:
        from app.services.mail_sender_service import send_mail
        email_body = f"""
Kedves felhasználó!<br>
Erre az email címre egy bejelentkezési név emlékeztetőt kértek.<br>
<br>
Felhasználóneved: {user.username}<br>
<br>
Ha ezt az emlékeztetőt nem te kérted akkor lépj kapcsolatba az oldal üzemeltetőjével!<br>
Üdv,<br>
Groubite
"""
        ok, msg = send_mail(user.email, "Groupbite: Bejelentkezési adat emlékeztető", email_body)
        if not ok:
            return { "error": "Email szolgáltatás nem elérhető, küldés sikertelen" }, 200

    return { "msg": "Email reminder sent" }, 200

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

    ok, user_to_register = User.create_user(User(username=username, email=email, settings={}, password=""))
    if ok:
        logging.info(f"User {user_to_register.username} created!")

        session["user_id"] = user_to_register.id
        session.permanent = True

        return { "data": user_to_register.serialized }, 201
    else:
        return { "error": "Failed to register, something wrong with the data you provided" }, 400


@user_blueprint.route("/<user_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
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


@user_blueprint.route("/<user_id>/orders", methods=["GET"])
@validate_url_params(IDSchema())
def handle_user_order_history(user_id):
    result = {}
    try:
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
    except ValueError as e:
        limit = 10
        page = 1
    except TypeError as e:
        limit = 10
        page = 1

    offset = 0 if page is None else limit * (page - 1)
    items = UserBasket.find_user_orders(user_id, limit, offset)
    all_items = UserBasket.find_user_orders(user_id)
    total_count = len(all_items)
    total_sum = 0
    set = []
    for item in all_items:
        total_sum += item.size.price * item.count
        if item.order not in set:
            total_sum += item.order.order_fee/len(Order.find_order_participants(item.order.id))
            set.append(item.order)

    for item in items:
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

    return { "data": {
        "items": result,
        "page": page,
        "limit": limit,
        "total_count": total_count,
        "total_sum": total_sum
        }
    }, 200


@user_blueprint.route("/", methods=["GET"])
@require_auth
@require_admin
def handle_get_users():
    try:
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
    except ValueError as e:
        limit = 10
        page = 1
    except TypeError as e:
        limit = 10
        page = 1
    offset = 0 if page is None else limit * (page - 1)
    users = User.find_all(limit, offset)
    total_count = len(User.find_all())
    result = []
    for user in users:
        result.append(user.serialized)
    return { "data": {
                "items": result,
                "page": page,
                "limit": limit,
                "total_count": total_count
            }
        }, 200
