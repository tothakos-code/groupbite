from flask import Blueprint, request
from entities.order import Order, OrderSchema

import requests, json, re
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
from entities.entity import Session
from __main__ import socketio

order_controller = Blueprint('order_controller', __name__, url_prefix='/order')

@order_controller.route('/history/', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@order_controller.route('/history/<requested_date>')
def handle_order_history(requested_date):
    session = Session()
    order_history = session.query(Order).filter(Order.order_date == requested_date).first()
    session.close()
    if not order_history:
        return {}
    return order_history.serialized['basket']
