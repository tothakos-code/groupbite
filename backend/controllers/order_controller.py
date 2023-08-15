from flask import Blueprint, request
from entities.order import Order, OrderSchema, order_state_type
from collections import Counter

import requests, json, re
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
from entities.entity import Session
from __main__ import socketio
from services.order_service import OrderService
from services.user_service import UserService
from services.menu_service import MenuService

sidfdpattern = r"\/sidfd-[0-9]+\/"

order_controller = Blueprint('order_controller', __name__, url_prefix='/order')

@order_controller.route('/history/<requested_date>')
@order_controller.route('/history', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
def handle_order_history(requested_date):
    session = Session()
    order_history = session.query(Order).filter(Order.order_date == requested_date).first()
    session.close()
    if not order_history:
        return {}
    OrderService.migrate_to_userid_based_order(requested_date)
    return OrderService.replace_userid_with_username(requested_date)


@order_controller.route('/get-order-state')
def handle_get_order_state():
    return json.dumps({"order_state":get_order_state()})


@order_controller.route('/get-all-order-date')
def handle_get_all_order_date():
    session = Session()
    order_dates = session.query(Order.order_date).filter(Order.basket != {}).all()
    session.close()
    return [str(order[0]) for order in order_dates]


@order_controller.route('/get-user-basket', methods=['POST'])
def handle_get_user_basket():
    USER = request.json['user']
    return OrderService.get_user_basket(USER)


@order_controller.route('/migrate-basket', methods=['GET'])
def handle_basket_migration():
    return OrderService.migrate_to_userid_based_order(date.today().strftime('%Y-%m-%d'))


@socketio.on('Server Basket Update')
def handle_basket_update(data):
    order_state = get_order_state()
    if order_state == str(order_state_type.closed):
        socketio.emit('Client Basket Update', {'basket': get_today_basket_with_usernames() })
        socketio.emit("Order state changed", order_state, room=request.sid)
        return
    userid = str(data['userid'])
    currentBasket = get_today_basket()
    if data['basket']:
        # basket is not empty, save new basket
        new_basket = OrderService.inject_label_and_price(data['basket'])
        currentBasket[userid] = new_basket
    elif userid in currentBasket:
        # basket is empty, delete key
        del currentBasket[userid]
    set_today_basket(currentBasket)
    socketio.emit('Client Basket Update', {'basket': get_today_basket_with_usernames() })


def get_today_basket():
    session = Session()
    today_basket = session.query(Order).filter(Order.order_date == date.today().strftime('%Y-%m-%d')).first()
    session.close()

    if not today_basket:
        return {}
    return today_basket.basket


def get_today_basket_with_usernames():
    return OrderService.replace_userid_with_username(date.today().strftime('%Y-%m-%d'))


def set_today_basket(basket):
    today_date = date.today().strftime('%Y-%m-%d')
    session = Session()
    today_basket = session.query(Order).filter(Order.order_date == today_date).first()

    if not today_basket:
        # insert
        session.add(Order(today_date, basket))
        logging.warning("Created today's basket row")
    else:
        # update
        today_basket.basket = basket
        logging.warning("Updated today's basket row")

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
    links = MenuService.get_all_fdid_with_link()


    set_order_state(order_state_type.order)
    logging.info("Order status changet to 'order'")
    socketio.emit("Order state changed", "order")


    if orders == {}:
        logging.warning("Error: basket is empty or could not get basket from database.")
        return "Error: basket empty or could not get basket from database."

    # Create the list of item links
    order_list = []
    for person, basket in orders.items():
        # ToDo: prevent None
        if basket == None:
            continue
        for food_item in basket.values():
            food_item_link = links[food_item['id']]
            for quantity in range(0,food_item['quantity']):
                order_list.append(food_item_link)


    requests_header={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Host": "falusitekercsgyorsetterem.pgg.hu"
        }
    logging.warning(Counter(order_list).items())
    # Loop the links and make the requests
    for link,count in Counter(order_list).items():
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
