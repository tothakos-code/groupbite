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
from app.services.user_service import UserService
from app.services.order_service import OrderService

socketio = SocketioSingleton.get_instance()

@user_blueprint.route("/login", methods=['POST'])
def handle_user_login():
    username = request.json['username']
    user_to_login = User.get_one_user(username)

    if not user_to_login:
        # register
        user_to_login = User.create_user(User(username=username))
        logging.info(f"User {user_to_login.username} created!")

    logging.info(f"User {user_to_login.username} logged in!")
    return user_to_login.serialized

@socketio.on('User Update')
def handle_user_update(user):
    logging.info("Updated User" + str(user['id']))

    session = Session()
    user_to_update = session.query(User).filter(User.id == user['id']).first()

    if 'subscribed' in user:
        # if user['subscribed'] == 'none':
        #     user_to_update.subscribed = SubscriptionType.none
        if user['subscribed'] == 'full':
            user_to_update.subscribed = SubscriptionType.SUB

    if 'username' in user:
        is_username_valid, error = UserService.is_username_valid(user['username'])
        if is_username_valid:
            user_to_update.username = user['username']

        else:
            session.close()
            return {"error": error}

    if 'ui_color' in user:
        user_to_update.ui_color = user['ui_color']

    if 'ui_theme' in user:
        user_to_update.ui_theme = user['ui_theme']

    session.commit()
    json_to_return = user_to_update.serialized
    session.close()
    if 'username' in user:
        # Updating the username in every basket(room) a user is in
        for room in rooms():
            try:
                socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(datetime.strptime(room, "%Y-%m-%d"))}, to=room)
            except ValueError:
                pass

    emit_user_ds_state()
    return json_to_return


@user_blueprint.route("/cron/clear_users_temp_state")
def cron_clear_users_temp_state():
    # session = Session()
    # # session.query(User).update({User.daily_state: str(SubscriptionType.none)})
    # session.commit()
    # session.close()
    emit_user_ds_state()
    return "OK", 200

@user_blueprint.route("/get/<id>")
def handle_get_user_by_id(id):
    user = UserService.get_user_by_id(id)
    if not user:
        return {}
    return user.serialized


@socketio.on('User Daily State Change')
def handle_user_ds_change(user):
    session = Session()
    user_to_update = session.query(User).filter(User.id == user['id']).first()

    user_to_update.daily_state = user['new_state']

    session.commit()
    user_result = user_to_update.serialized
    session.close()
    emit_user_ds_state()
    return user_result

def emit_user_ds_state():
    session = Session()
    user_list = session.query(User).all()
    session.close()
    result = {}
    # TODO: switct to enum reference
    for user in user_list:
        result_state = 'none'
        if str(user.subscribed) == 'full':
            result_state = 'sub'
        if str(user.daily_state) == 'video':
            result_state = 'video'
        if str(user.daily_state) == 'skip':
            result_state = 'skip'
        result[user.username] = result_state

    socketio.emit('Waiting Update', result)
