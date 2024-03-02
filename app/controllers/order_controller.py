from flask import Blueprint, request
from flask_socketio import join_room, leave_room
from collections import Counter
import requests, json, re
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast

from app.controllers import order_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities.order import Order, OrderState
from app.entities.user_basket import UserBasket
from app.entities import Session
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.services.menu_service import MenuService

sidfdpattern = r"\/sidfd-[0-9]+\/"
socketio = SocketioSingleton.get_instance()

@order_blueprint.route('/history/<requested_date>')
@order_blueprint.route('/history', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
def handle_order_history(requested_date):
    session = Session()
    order_history = session.query(Order).filter(Order.order_date == requested_date).first()
    session.close()
    if not order_history:
        return {}
    OrderService.migrate_to_userid_based_order(requested_date)
    return OrderService.replace_userid_with_username(requested_date)

# TODO: implement this
# @order_blueprint.route('/get-order-state')
def handle_get_order_state():
    return json.dumps({"order_state":OrderService.get_order_state()})

# TODO: Find all order with orderd state
@order_blueprint.route('/get-all-order-date')
def handle_get_all_order_date():
    session = Session()
    order_dates = session.query(Order.order_date).filter(Order.basket != {}).all()
    session.close()
    return [str(order[0]) for order in order_dates]

@order_blueprint.route('/<order_id>/get-basket', methods=['GET'])
def handle_get_basket(order_id):
    result = []
    for basket_entry in UserBasket.find_items_by_order(order_id):
        result.append(basket_entry.basket_format)
    return json.dumps(result)

# TODO: implement this, was there an order for a user
@order_blueprint.route('/get-user-basket-between', methods=['POST'])
def handle_get_user_basket_between():
    USER = request.json['user']
    DATE_FROM = request.json['date_from']
    DATE_TO = request.json['date_to']
    return OrderService.get_user_basket_between(UserService.username_to_id(USER), DATE_FROM, DATE_TO)

# TODO: Delet this
@order_blueprint.route('/migrate-basket', methods=['GET'])
def handle_basket_migration():
    return str(OrderService.migrate_to_userid_based_order(date.today().strftime('%Y-%m-%d')))

# TODO: Upgrade this
# @socketio.on('Client Date Selection Change')
def handle_date_selection_change(data):
    new_date = data['selected_date']
    old_date = data['old_selected_date']
    leave_room(old_date)
    join_room(new_date)
    socketio.emit('Client Basket Update', {'basket': OrderService.get_formated_full_basket(order_id) }, to=request.sid)
    socketio.emit("Order state changed", OrderService.get_order_state(new_date), room=request.sid)

# TODO: Turn to GET request
@order_blueprint.route('/get-order/', methods=['POST'])
def handle_get_order_by_vendor_and_date():
    VENDOR_ID = request.json['vendor_id']
    DATE = request.json['date']
    order = Order.find_open_order_by_date_for_a_vendor(VENDOR_ID, DATE)
    if not order:
        order = Order.create_order(VENDOR_ID, DATE)
    return order.serialized

@order_blueprint.route('/<order_id>/add', methods=['POST'])
def handle_add_to_basket(order_id):
    USER = request.json['user_id']
    MI_ID = request.json['menu_item_id']

    if UserBasket.add_item(USER, MI_ID, order_id):
        socketio.emit('Client Basket Update', OrderService.get_formated_full_basket(order_id))
        return "OK", 201
    return "Error, something went wrong.", 500

@order_blueprint.route('/<order_id>/remove', methods=['POST'])
def handle_remove_from_basket(order_id):
    USER = request.json['user_id']
    MI_ID = request.json['menu_item_id']

    if UserBasket.remove_item(USER, MI_ID, order_id):
        socketio.emit('Client Basket Update', OrderService.get_formated_full_basket(order_id))
        return "OK", 201
    return "Error, something went wrong.", 500

@order_blueprint.route('/<order_id>/clear', methods=['POST'])
def handle_clear_user_basket(order_id):
    USER = request.json['user_id']

    if UserBasket.clear_items(USER, order_id):
        socketio.emit('Client Basket Update', OrderService.get_formated_full_basket(order_id))
        return "OK", 201
    return "Error, something went wrong.", 500


@socketio.on('Ordered and Payed')
def handle_payed(data):
    order_date = str(data['date'])
    session = Session()
    order_state = session.query(Order).filter(Order.order_date == order_date).first()
    order_state.order_state = OrderState.CLOSED
    session.commit()
    session.close()
    socketio.emit("Order state changed", str(OrderState.CLOSED))

# TODO: Move to plugin
@order_blueprint.route('/transferBasket', methods=['POST'])
def call_transfer_basket():
    PHPSESSIONID = request.json['psid']
    ORDER_DATE = request.json['order_date']

    orders = OrderService.get_basket(ORDER_DATE)
    links = MenuService.get_all_fdid_with_link()


    OrderService.set_order_state(OrderState.ORDER, ORDER_DATE)
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
