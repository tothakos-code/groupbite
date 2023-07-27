from flask import Blueprint, request
from entities.order import Order, OrderSchema, order_state_type
from collections import Counter

import requests, json, re
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
from entities.entity import Session
from __main__ import socketio

sidfdpattern = r"\/sidfd-[0-9]+\/"

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


@order_controller.route('/get-order-state')
def handle_request_order_state():
    return json.dumps({"order_state":get_order_state()})


@socketio.on('Server Basket Update')
def handle_basket_update(data):
    order_state = get_order_state()
    if order_state == str(order_state_type.closed):
        socketio.emit('Client Basket Update', {'basket': get_today_basket() })
        socketio.emit("Order state changed", order_state, room=request.sid)
        return
    user = list(data.keys())[0]
    currentBasket = get_today_basket()
    if data[user]:
        # basket is not empty, save new basket
        currentBasket[user] = data[user]
    elif user in currentBasket:
        # basket is empty, delete key
        del currentBasket[user]

    socketio.emit('Client Basket Update', {'basket': set_today_basket(currentBasket) })


def get_today_basket():
    session = Session()
    today_basket = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()
    session.close()

    if not today_basket:
        return {}
    return today_basket.basket


def set_today_basket(basket):
    session = Session()
    today_basket = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()

    if not today_basket:
        # insert
        session.add(Order(date.today().strftime('%Y-%m-%d'), basket))
        logging.info("Created today's basket row")
    else:
        # update
        today_basket.basket = basket
        logging.info("Updated today's basket row")

    session.commit()

    return get_today_basket()


@socketio.on('Ordered and Payed')
def handle_payed():
    session = Session()
    order_state = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()
    order_state.order_state = order_state_type.closed
    session.commit()
    socketio.emit("Order state changed", str(order_state_type.closed))


def get_order_state():
    """Returns to current order state value
    Parameters
    ----------
    none

    Returns
    -------
    String
        A order_state_type value.
    """
    session = Session()
    order_state = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()
    session.close()
    if not order_state:
        return str(order_state_type.collect)

    return str(order_state.order_state)


def set_order_state(new_state):
    """Setter for today's order state
    Parameters
    ----------
    new_state: An order_state_type object to sot the order_state to.

    Returns
    -------
    order_state_type
        An order_state_type object.
    """
    session = Session()
    today_order = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()
    if not today_order:
        session.close()
        return str(order_state_type.collect)

    today_order.order_state = new_state
    session.commit()
    return str(today_order.order_state)


@order_controller.route('/transferBasket', methods=['POST'])
def call_transfer_basket():
    PHPSESSIONID = request.json['psid']

    orders = get_today_basket()

    set_order_state(order_state_type.order)
    logging.info("Order status changet to 'order'")
    socketio.emit("Order state changed", "order")


    if orders == {}:
        logging.warning("Error: basket is empty or could not get basket from database.")
        return "Error: basket empty or could not get basket from database."

    # Create the list of item links
    orderList = []
    for person, basket in orders.items():
        # ToDo: prevent None
        if basket == None:
            continue
        for foodItem in basket.values():
            for quantity in range(0,foodItem['quantity']):
                orderList.append(foodItem['link'])


    requests_header={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Host": "falusitekercsgyorsetterem.pgg.hu"
        }

    # Loop the links and make the requests
    for link,count in Counter(orderList).items():
        sizeid = re.search(sidfdpattern, link).group().replace('/','').split('-')[1]

        requests_data={
            "item_cnt": count,
            "item_size_ref": sizeid,
            "plusmenu[]": "112",
            "menu_a[]": "0",
            "plus0[]": "112",
            "act": "add",
            "compAll": ""
            }

        # r = requests.post(
        #     link,
        #     headers=requests_header,
        #     data=requests_data,
        #     cookies={"PHPSESSID":PHPSESSIONID}
        # )
    return 'OK'
