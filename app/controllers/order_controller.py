from flask import Blueprint, request
from flask_socketio import join_room, leave_room
import json
import logging
from datetime import date, timedelta, datetime

from app.controllers import order_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities.order import Order, OrderState
from app.entities.user_basket import UserBasket
from app.entities import Session
from app.utils.decorators import validate_url_params, require_auth
from app.utils.validators import IDSchema


socketio = SocketioSingleton.get_instance()

# TODO: chage to GET and use query params
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
        sum += order.order_fee
        result[date][value[0]]["sum"] = sum

    if USER_ID != None:
        for value in UserBasket.find_user_order_dates_between(USER_ID, DATE_FROM, DATE_TO):
            date = value[1].strftime("%Y-%m-%d")
            order_id = value[0]
            result[date][order_id]["ordered"] = True

    return { "data": result }, 200


@order_blueprint.route("/<order_id>", methods=["GET"])
@validate_url_params(IDSchema())
def handle_get_basket(order_id):
    order = Order.get_by_id(order_id)
    return_obj = order.serialized
    return_obj["basket"] = UserBasket.get_basket_group_by_user(order.id)
    return { "data": return_obj }, 200


@order_blueprint.route("/statistics", methods=["GET"])
def handle_get_statistics():
    year_result, year_labels = Order.last_12_month_statistics()
    week_result, week_labels = Order.last_7_days_statistics()
    return {
        "data": {
            "year_data": {
                "data": year_result,
                "labels": year_labels
            },
            "week_data": {
                "data": week_result,
                "labels": week_labels
            }
        }
    }, 200


@order_blueprint.route("/", methods=["GET"])
def handle_get_orders():
    orders = Order.find_all()
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
    orders = Order.find_all(limit, offset)
    total_count = len(Order.find_all())
    result = []
    for order in orders:
        result.append(order.serialized)
    return { "data": {
                "items": result,
                "page": page,
                "limit": limit,
                "total_count": total_count
            }
        }, 200

@order_blueprint.route("/<order_id>/order_fee", methods=["PUT"])
@require_auth
@validate_url_params(IDSchema())
def handle_update_order_fee(order_id):
    order = Order.get_by_id(order_id)
    if order.set_order_fee(request.json["data"]["order_fee"]):
        socketio.emit(
            "be_order_update", {
                "order": order.serialized,
            }
            )
        return { "msg": "OK" }, 200
    else:
        return { "error": "Someting went wrong" }, 500



# TODO: Upgrade this
@socketio.on("fe_date_selection")
def handle_date_selection_change(data):
    new_date = data["new_selected_date"]
    vendor_id = data["vendor_id"]


    if "old_selected_date" in data:
        old_date = data["old_selected_date"]
        leave_room(f"{vendor_id}@{old_date}")

    join_room(f"{vendor_id}@{new_date}")

    order = Order.find_order_by_date_for_a_vendor(vendor_id, new_date)

    if not order:
        ok, order = Order.create_order(vendor_id, new_date)
        if not ok:
            logging.error("Cannot create order")
            return


    socketio.emit(
        "be_order_update", {
            "order": order.serialized,
            "basket": UserBasket.get_basket_group_by_user(order.id)
        },
        to=request.sid
        )


@order_blueprint.route("/<order_id>/user/<user_id>/copy-from/<src_user_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
def handle_copy_basket(order_id, user_id, src_user_id):

    UserBasket.clear_items(user_id, order_id)
    for item in UserBasket.find_user_basket(src_user_id, order_id):
        for i in range(0,item.count):
            UserBasket.add_item(user_id, str(item.menu_item_id), item.size_id, order_id)

    order = Order.get_by_id(order_id)


    socketio.emit("be_order_update", {
        "basket": UserBasket.get_basket_group_by_user(order_id),
        },
        to=f"{order.vendor_id}@{order.date_of_order}"
        )
    return { "msg": "OK" }, 201


@order_blueprint.route("/<order_id>/user/<user_id>/item/<item_id>/size/<size_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
def handle_add_to_basket(order_id, user_id, item_id, size_id):
    order = Order.get_by_id(order_id)
    data = {
        "order_id": order_id,
        "user_id": user_id,
        "menu_item_id": item_id,
        "size_id": size_id
    }

    from app.event_manager import event_manager
    event_manager.trigger_event("beforeAdd@" + order.vendor.name, data)

    ok, result = UserBasket.add_item(
        user_id,
        item_id,
        size_id,
        order_id
    )

    event_manager.trigger_event("afterAdd@" + order.vendor.name, data)

    if ok:
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        },
        to=f"{order.vendor_id}@{order.date_of_order}"
        )
        return { "msg": "OK" }, 201
    else:
        return { "error":"Item out of stock" }, 400

    return { "error": "something went wrong." }, 500


@order_blueprint.route("/<order_id>/user/<user_id>/item/<item_id>/size/<size_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
def handle_remove_from_basket(order_id, user_id, item_id, size_id):
    order = Order.get_by_id(order_id)
    data = {}
    data["order_id"] = order_id
    data["user_id"] = user_id
    data["menu_item_id"] = item_id
    data["size_id"] = size_id

    from app.event_manager import event_manager
    event_manager.trigger_event("beforeRemove@" + order.vendor.name, data)

    ok = UserBasket.remove_item(
        user_id,
        item_id,
        size_id,
        order_id
    )

    event_manager.trigger_event("afterRemove@" + order.vendor.name, data)

    if ok:
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        },
        to=f"{order.vendor_id}@{order.date_of_order}"
        )
        return { "msg": "OK" }, 204
    return { "error": "something went wrong." }, 500


@order_blueprint.route("/<order_id>/user/<user_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
def handle_clear_user_basket(order_id, user_id):
    if UserBasket.clear_items(user_id, order_id):
        order = Order.get_by_id(order_id)
        socketio.emit("be_order_update", {
            "basket": UserBasket.get_basket_group_by_user(order_id)
        },
        to=f"{order.vendor_id}@{order.date_of_order}"
        )
        return { "msg": "OK" }, 204
    return { "error": "Order or User not found" }, 404


@order_blueprint.route("/<order_id>/state", methods=["PUT"])
@validate_url_params(IDSchema())
def handle_close_order(order_id):
    order = Order.get_by_id(order_id)
    data = {
        "order_id": order_id
    }
    from app.event_manager import event_manager
    event_manager.trigger_event("beforeClose@" + order.vendor.name, data)

    ok = order.change_state(OrderState.CLOSED)
    if not ok:
        logging.error(f"Order close error")

    if "order_fee" in data:
        ok = order.set_order_fee(data["order_fee"])
    else:
        ok = order.set_order_fee(order.vendor.settings["transport_price"]["value"])

    if not ok:
        logging.error(f"Order fee setting error")

    event_manager.trigger_event("afterClose@" + order.vendor.name, data)
    logging.info(f"Order closed succesfully")
    socketio.emit("be_order_update", {
        "order": order.serialized
        },
        to=f"{order.vendor_id}@{order.date_of_order}"
        )
    return { "msg": "OK" }, 200
