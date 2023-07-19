from flask import Flask
from flask import request
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
from collections import Counter
import logging
import datetime
import db
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True)
app.config['SECRET_KEY'] = 'secret!'

from controllers.menu_controller import menu_controller
from controllers.order_controller import order_controller
from controllers.user_controller import user_controller, emit_user_ds_state
app.register_blueprint(menu_controller)
app.register_blueprint(order_controller)
app.register_blueprint(user_controller)

sidfdpattern = r"\/sidfd-[0-9]+\/"

sql_select = "SELECT basket FROM orders WHERE order_date = CURRENT_DATE"
sql_get_state = "SELECT order_state FROM orders WHERE order_date = CURRENT_DATE"
sql_set_state = "UPDATE orders SET order_state = %s WHERE order_date = CURRENT_DATE RETURNING order_state"
sql_insert = "INSERT INTO orders (basket) values (%s) RETURNING basket"
sql_update = "UPDATE orders SET basket = %s WHERE order_date = CURRENT_DATE RETURNING basket"


sql_order_select_by_date = "SELECT basket FROM orders WHERE order_date = %s"


@app.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit('Refresh!')
    return "OK", 200

@app.route('/')
def call_hello():
    return "Welcome to this api on a pi!"

@app.route('/clearclientsbasket')
def call_clear_clients_basket():
    socketio.emit('Clear Local Basket')
    return "OK"

@app.route('/transferBasket', methods=['POST'])
def call_transfer_basket():
    PHPSESSIONID = request.json['psid']
    orders = None

    orders = db.run_sql(sql_select, fetch='one')[0]

    db.run_sql(sql_set_state, ('order',))
    logging.info("Order status changet to 'order'")

    socketio.emit("Order state changed", "order")

    if orders is None:
        logging.warning("Error: basket empty or could not get basket from database.")
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
    logging.info(Counter(orderList))
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

        r = requests.post(
            link,
            headers=requests_header,
            data=requests_data,
            cookies={"PHPSESSID":PHPSESSIONID},
            verify=False
        )
    return 'OK'

@socketio.on('connect')
def handle_connect(data):
    socketio.emit('Client Basket Update', {'basket': get_today_basket() })
    emit_user_ds_state()

@socketio.on('Ordered and Payed')
def handle_payed():
    db.run_sql(sql_set_state, ('closed',))
    socketio.emit("Order state changed", "closed")

@socketio.on('Server Basket Update')
def handle_basket_update(data):
    order_state = get_order_state()
    if order_state == "closed":
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

def get_order_state():
    rowcount = db.get_row_count(sql_select)
    result = db.run_sql(sql_get_state, fetch='one')

    if rowcount == 0:
        # orderer not initialized yet, return the default value
        return 'collect'
    elif rowcount == 1:
        # return the state
        return result
    elif rowcount > 1:
        # this error is impossible
        logging.error("ERROR: There is more than one order, I dont know what to do! PANIC!")


def get_today_basket():
    rowcount = db.get_row_count(sql_select)

    if rowcount == 0:
        # return empty basket, there is not yet created
        return {}
    elif rowcount == 1:
        # return the basket
        return db.run_sql(sql_select, fetch='one')[0]
    elif rowcount > 1:
        # this error is impossible
        logging.error("ERROR: There is more than one order, I dont know what to do! PANIC!")

def set_today_basket(basket):
    rowcount = db.get_row_count(sql_select)

    result = None

    if rowcount == 0:
        # insert row
        result = db.run_sql(sql_insert, (json.dumps(basket),), fetch='one')[0]
        logging.info("Created today's basket row")
    elif rowcount == 1:
        # update row
        result = db.run_sql(sql_update, (json.dumps(basket),), fetch='one')[0]
        logging.info("Updated today's basket row")
    elif rowcount > 1:
        # this is impossible
        logging.error("ERROR: There is more than one order, I dont know what to do! PANIC!")

    return result

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
