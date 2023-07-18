from flask import Blueprint, request
from entities.user import User, UserSchema
from entities.entity import Session
from sqlalchemy import func, cast
import logging
from __main__ import socketio

user_controller = Blueprint('user_controller', __name__, url_prefix='/user')

@socketio.on('User Login')
def handle_user_login(user):
    session = Session()
    user_to_login = session.query(User).filter(User.username == user['username']).first()

    if not user_to_login:
        # register
        user_to_login = session.add(User(user['username']))

    # login after all
    session.commit()
    return user_to_login.serialized

@socketio.on('User Update')
def handle_user_update(user):
    logging.info("Updated User" + user['username'])

    session = Session()
    user_to_update = session.query(User).filter(User.username == user['username']).first()

    user_to_update.subscribed = user['subscribed']

    session.commit()

    emit_user_ds_state()
    return user_to_update.serialized


@user_controller.route("/cron/clear_users_temp_state")
def cron_clear_users_temp_state():
    db.run_sql(sql_user_clear_temp_state)
    session = Session()
    User.query.update({User.daily_state: 'none'})
    session.commit()

    emit_user_ds_state()
    return "OK", 200


@socketio.on('User Daily State Change')
def handle_user_ds_change(user):
    session = Session()
    user_to_update = session.query(User).filter(User.username == user['username']).first()

    user_to_update.daily_state = user['new_state']

    session.commit()

    emit_user_ds_state()
    return user_to_update.serialized

def emit_user_ds_state():
    session = Session()
    user_list = session.query(User).all()
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
