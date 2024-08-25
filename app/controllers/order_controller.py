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


sidfdpattern = r"\/sidfd-[0-9]+\/"
socketio = SocketioSingleton.get_instance()

@order_blueprint.route("/history", methods=["POST"])
def handle_order_history():
    DATE_FROM = request.json["date_from"]
    DATE_TO = request.json["date_to"]
    USER_ID = None
    if "user_id" in request.json:
        USER_ID = request.json["user_id"]

    result = {}
    for value in UserBasket.find_orders_between_dates(DATE_FROM, DATE_TO):
        order = Order.get_by_id(value[0])
        date = value[1].strftime("%Y-%m-%d")
        if date not in result:
            result[date] = {}

        result[date][value[0]] = order.serialized
        result[date][value[0]]["vendor"] = order.vendor.name

        sum = 0
        for item in order.items:
            sum += item.size.price * item.count
        result[date][value[0]]["sum"] = sum

    if USER_ID != None:
        for value in UserBasket.find_user_order_dates_between(USER_ID, DATE_FROM, DATE_TO):
            date = value[1].strftime("%Y-%m-%d")
            order_id = value[0]
            result[date][order_id]["ordered"] = True

    return json.dumps(result)

    # TODO: add a limit and a pager option
@order_blueprint.route("/history/<user_id>", methods=["GET"])
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

    return json.dumps(result)


# TODO: Find all order with orderd state
@order_blueprint.route("/get-all-order-date")
def handle_get_all_order_date():
    session = Session()
    order_dates = session.query(Order.order_date).filter(Order.basket != {}).all()

    return [str(order[0]) for order in order_dates]

@order_blueprint.route("/<order_id>/get-basket", methods=["GET"])
def handle_get_basket(order_id):
    return UserBasket.get_basket_group_by_user(order_id)

# TODO: implement this, was there an order for a user
@order_blueprint.route("/get-user-basket-between", methods=["POST"])
def handle_get_user_basket_between():
    USER_ID = request.json["user_id"]
    DATE_FROM = request.json["date_from"]
    DATE_TO = request.json["date_to"]
    result = []
    for value in UserBasket.find_user_order_dates_between(USER_ID, DATE_FROM, DATE_TO):
        result.append({
            "order_id": value[0],
            "date": value[1].strftime("%Y-%m-%d"),
        })
    return json.dumps(result)

# TODO: Upgrade this
@socketio.on("fe_date_selection")
def handle_date_selection_change(data):
    new_date = data["new_selected_date"]
    vendor_id = data["vendor_id"]

    if "old_selected_date" in data:
        old_date = data["old_selected_date"]
        leave_room(f"{vendor_id}_{old_date}")

    join_room(f"{vendor_id}_{new_date}")

    order = Order.find_order_by_date_for_a_vendor(vendor_id, new_date)

    if not order:
        order = Order.create_order(vendor_id, new_date)

    socketio.emit(
        "be_order_update", {
            "order": order.serialized,
            "basket": UserBasket.get_basket_group_by_user(order.id)
        },
        to=request.sid
        )

@order_blueprint.route("/<order_id>/add", methods=["POST"])
def handle_add_to_basket(order_id):
    order = Order.get_by_id(order_id)
    request.json["order_id"] = order_id

    from app.event_manager import event_manager
    event_manager.trigger_event("beforeAdd@" + order.vendor.name, request.json)

    result, error = UserBasket.add_item(
        request.json["user_id"],
        request.json["menu_item_id"],
        request.json["size_id"],
        order_id
    )

    event_manager.trigger_event("afterAdd@" + order.vendor.name, request.json)

    if result:
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        })
        return "OK", 201
    else:
        return {"error":"Item out of stock"}, 200
    return "Error, something went wrong.", 500

@order_blueprint.route("/<order_id>/copy", methods=["POST"])
def handle_copy_basket(order_id):
    # who wants to copy
    USER = request.json["user_id"]
    # user he want to copy from
    COPY_USER = request.json["copy_user_id"]

    UserBasket.clear_items(USER, order_id)
    for item in UserBasket.find_user_basket(COPY_USER, order_id):
        for i in range(0,item.count):
            UserBasket.add_item(USER, str(item.menu_item_id), item.size_id, order_id)

    socketio.emit("be_order_update", {
        "basket": UserBasket.get_basket_group_by_user(order_id)
    })
    return "OK", 201

@order_blueprint.route("/<order_id>/remove", methods=["POST"])
def handle_remove_from_basket(order_id):
    order = Order.get_by_id(order_id)
    request.json["order_id"] = order_id

    from app.event_manager import event_manager
    event_manager.trigger_event("beforeRemove@" + order.vendor.name, request.json)

    result = UserBasket.remove_item(
        request.json["user_id"],
        request.json["menu_item_id"],
        request.json["size_id"],
        order_id
    )

    event_manager.trigger_event("afterRemove@" + order.vendor.name, request.json)

    if result:
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        })
        return "OK", 201
    return "Error, something went wrong.", 500

@order_blueprint.route("/<order_id>/clear", methods=["POST"])
def handle_clear_user_basket(order_id):
    USER = request.json["user_id"]

    if UserBasket.clear_items(USER, order_id):
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        })
        return "OK", 201
    return "Error, something went wrong.", 500


@socketio.on("fe_order_closed")
def handle_close_order(data):
    order_date = str(data["date"])
    user_id = str(data["user_id"])
    vendor_id = str(data["vendor_id"])

    order = Order.find_open_order_by_date_for_a_vendor(vendor_id, order_date)
    order.change_state(OrderState.CLOSED, user_id)

    socketio.emit("be_order_update", {
        "order": order.serialized
    })

# TODO: Move to plugin
@order_blueprint.route("/transferBasket", methods=["POST"])
def call_transfer_basket():
    PHPSESSIONID = request.json["psid"]
    ORDER_DATE = request.json["order_date"]

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
            food_item_link = links[food_item["id"] + "-" + food_item["size"]]
            for quantity in range(0,food_item["quantity"]):
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
        sizeid = re.search(sidfdpattern, link).group().replace("/","").split("-")[1]

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
    return "OK"
