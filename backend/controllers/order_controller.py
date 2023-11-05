from flask import Blueprint, request
from entities.order import Order, OrderSchema, order_state_type
from collections import Counter

import requests, json, re
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
from entities.entity import Session
from __main__ import socketio
from flask_socketio import join_room, leave_room
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
    return json.dumps({"order_state":OrderService.get_order_state()})


@order_controller.route('/get-all-order-date')
def handle_get_all_order_date():
    session = Session()
    order_dates = session.query(Order.order_date).filter(Order.basket != {}).all()
    session.close()
    return [str(order[0]) for order in order_dates]


@order_controller.route('/get-user-basket', methods=['POST'])
def handle_get_user_basket():
    USER = request.json['user']
    DATE = request.json['date']
    return OrderService.get_user_basket(USER,DATE)

@order_controller.route('/get-user-basket-between', methods=['POST'])
def handle_get_user_basket_between():
    USER = request.json['user']
    DATE_FROM = request.json['date_from']
    DATE_TO = request.json['date_to']
    return OrderService.get_user_basket_between(UserService.username_to_id(USER), DATE_FROM, DATE_TO)


@order_controller.route('/migrate-basket', methods=['GET'])
def handle_basket_migration():
    return str(OrderService.migrate_to_userid_based_order(date.today().strftime('%Y-%m-%d')))


@socketio.on('Client Date Selection Change')
def handle_date_selection_change(data):
    new_date = data['selected_date']
    old_date = data['old_selected_date']
    leave_room(old_date)
    join_room(new_date)
    socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(new_date) }, to=request.sid)
    socketio.emit("Order state changed", OrderService.get_order_state(new_date), room=request.sid)


@socketio.on('Server Basket Update')
def handle_basket_update(data):
    """Handling the basket modification event sent from a client."""
    basket_date = str(data['order_date'])
    userid = str(data['userid'])
    basket = data['basket']

    # Check if update is possible
    order_state = OrderService.get_order_state(basket_date)
    if order_state == str(order_state_type.closed):
        socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(basket_date) }, to=basket_date)
        socketio.emit("Order state changed", order_state, room=request.sid)
        return

    db_basket = OrderService.get_basket(basket_date)
    if basket:
        # basket is not empty, save new basket
        new_basket = OrderService.inject_label_and_price(basket)
        db_basket[userid] = new_basket
    elif userid in db_basket:
        # basket is empty, delete key
        del db_basket[userid]
    OrderService.set_basket(db_basket,basket_date)

    socketio.emit('Client Basket Update', {'basket': OrderService.replace_userid_with_username(basket_date)}, to=basket_date)


@socketio.on('Ordered and Payed')
def handle_payed(data):
    order_date = str(data['date'])
    session = Session()
    order_state = session.query(Order).filter(Order.order_date == order_date).first()
    order_state.order_state = order_state_type.closed
    session.commit()
    session.close()
    socketio.emit("Order state changed", str(order_state_type.closed))


@order_controller.route('/transferBasket', methods=['POST'])
def call_transfer_basket():
    PHPSESSIONID = request.json['psid']
    ORDER_DATE = request.json['order_date']

    orders = OrderService.get_basket(ORDER_DATE)
    links = MenuService.get_all_fdid_with_link()


    OrderService.set_order_state(order_state_type.order, ORDER_DATE)
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
            food_item_link = links[food_item['id'] + "-" + food_item['size']]
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
