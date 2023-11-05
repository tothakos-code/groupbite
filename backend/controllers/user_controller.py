from flask import Blueprint, request
from entities.user import User, UserSchema, subscribe_type
from entities.entity import Session
from sqlalchemy import func, cast, update
import logging
from __main__ import socketio
from flask_socketio import rooms
from services.user_service import UserService
from services.order_service import OrderService
from datetime import datetime


user_controller = Blueprint('user_controller', __name__, url_prefix='/user')

@socketio.on('User Login')
def handle_user_login(user):
    session = Session()
    user_to_login = session.query(User).filter(User.username == user['username']).first()

    if not user_to_login:
        # register
        new_user = User(user['username'])
        session.add(new_user)
        user_to_login = new_user

    # login after all
    session.commit()
    return user_to_login.serialized

@socketio.on('User Update')
def handle_user_update(user):
    logging.info("Updated User" + str(user['id']))

    session = Session()
    user_to_update = session.query(User).filter(User.id == user['id']).first()

    if 'subscribed' in user:
        if user['subscribed'] == 'none':
            user_to_update.subscribed = subscribe_type.none
        if user['subscribed'] == 'full':
            user_to_update.subscribed = subscribe_type.full

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


@user_controller.route("/cron/clear_users_temp_state")
def cron_clear_users_temp_state():
    session = Session()
    session.query(User).update({User.daily_state: str(subscribe_type.none)})
    session.commit()
    session.close()
    emit_user_ds_state()
    return "OK", 200

@user_controller.route("/get/<id>")
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
