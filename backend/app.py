from flask import Flask
from flask import request
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
from collections import Counter
import logging
import datetime
import db
from entities.entity import Session, engine, Base
from entities.menu import Menu, MenuSchema
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True)

app.config['SECRET_KEY'] = 'secret!'


napok = ["hetfoi","keddi", "szerdai","csutortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"
sidfdpattern = r"\/sidfd-[0-9]+\/"

sql_select = "SELECT basket FROM orders WHERE order_date = CURRENT_DATE"
sql_get_state = "SELECT order_state FROM orders WHERE order_date = CURRENT_DATE"
sql_set_state = "UPDATE orders SET order_state = %s WHERE order_date = CURRENT_DATE RETURNING order_state"
sql_insert = "INSERT INTO orders (basket) values (%s) RETURNING basket"
sql_update = "UPDATE orders SET basket = %s WHERE order_date = CURRENT_DATE RETURNING basket"

sql_user_select = "SELECT * FROM users WHERE username = %s"
sql_user_insert = "INSERT INTO users (username) values (%s) RETURNING *"
sql_user_sub_update = "UPDATE users SET subscribed = %s WHERE username = %s RETURNING *"
sql_user_name_update = "UPDATE users SET username = %s WHERE username = %s"

sql_user_subscribed = "SELECT username FROM users WHERE subscribed = 'full'"

sql_get_alluser_ds = "SELECT username,daily_state,subscribed FROM users;"
sql_user_set_ds = "UPDATE users SET daily_state = %s WHERE username = %s RETURNING *"

sql_user_clear_temp_state = "UPDATE users SET daily_state = 'none'"

sql_order_select_by_date = "SELECT basket FROM orders WHERE order_date = %s"

@app.route("/test/sqlalchemy")
def test_clear_users_temp_state():
    # fetching from the database
    session = Session()
    menu_objects = session.query(Menu).all()

    # transforming into JSON-serializable objects
    schema = MenuSchema(many=True)
    menus = schema.dump(menu_objects)

    # serializing as JSON
    session.close()
    return json.dumps(menus[0]['menu'][0], indent=4)

@app.route("/test/sqlalchemy/get")
def test_clear_users_temp_state_get():
     # mount exam object
    online_menu = get_etlap()

    menu = Menu(online_menu)

    try:
        # persist exam
        session = Session()
        session.add(menu)
        session.commit()
    except IntegrityError as e:
        return "Today Menu already exist", 200

    # return created exam
    new_menu = MenuSchema().dump(menu)
    session.close()
    return json.dumps(new_menu), 201

@app.route("/cron/clear_users_temp_state")
def cron_clear_users_temp_state():
    db.run_sql(sql_user_clear_temp_state)
    emit_user_ds_state()
    return "OK", 200

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

@app.route('/getorderstate')
def call_get_order_state():
    return get_order_state()

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


@app.route('/getmenu')
def get_etlap():
    # Requesting and parsing th HTML
    r = requests.get('https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/', verify=False)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Getting the current day
    requestedDay = request.args.get('day')
    if requestedDay is None or requestedDay == 'undefined':
        day = datetime.datetime.today().weekday()
    else:
        day = int(requestedDay) - 1

    logging.warning("Mai nap: " + str(day))
    dayString = napok[day]


    menu = []
    for li in soup.find_all('li', class_='foods_' + dayString + '-menu'):
        menuElement = {}
        menuElement['label'] = li.find('div',class_='fdr_name_img').find('div', class_='fooddrink_name').text.strip()

        menuSizes = []
        for size in li.find('div',id='food_params').find_all('div', class_='food_dring_size'):
            menuSizeElement = {}
            menuSizeElement['link'] = size.find('a', class_='billadd_link', href=True)['href']
            menuElement['id'] = re.search(fdidpattern, menuSizeElement['link']).group().replace('/','')

            orderbutton = size.find('a', class_='billadd_link')
            menuSizeElement['size'] = orderbutton.find('span', class_='size').text
            menuSizeElement['price'] = orderbutton.find('span', class_='price').text
            menuSizeElement['label'] = menuSizeElement['size'] + ' ' + menuSizeElement['price']

            menuSizes.append(menuSizeElement)


        menuElement['sizes'] = menuSizes
        menu.append(menuElement)
    return menu

@socketio.on('connect')
def handle_connect(data):
    socketio.emit('Client Basket Update', {'basket': get_today_basket() })
    emit_user_ds_state()

@socketio.on('Request order state')
def handle_request_order_state():
    return get_order_state()

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

def get_subscribed_users():
    result = db.run_sql(sql_user_subscribed)
    return [i[0] for i in result]

@socketio.on('User Login')
def handle_user_login(data):
    response = login_user(data)
    return {
        "id": response[0],
        "username": response[1],
        "subscribed": response[2],
        "theme": response[3]
    }

@socketio.on('Order History')
def handle_order_history(data):
    date = data['requestedDate']
    return db.run_sql(sql_order_select_by_date, (date,), fetch='one')

@socketio.on('User Update')
def handle_user_update(data):
    response = set_user(data)
    emit_user_ds_state()
    return {
        "id": response[0],
        "username": response[1],
        "subscribed": response[2],
        "theme": response[3]
    }

@socketio.on('User Daily State Change')
def handle_user_ds_change(data):
    db.run_sql(sql_user_set_ds, (data['new_state'], data['username']))
    emit_user_ds_state()

def emit_user_ds_state():
    user_list = db.run_sql(sql_get_alluser_ds)
    result = {}
    for (user,state,sub) in user_list:
        result_state = 'none'
        if sub == 'full':
            result_state = 'sub'
        if state == 'video':
            result_state = 'video'
        if state == 'skip':
            result_state = 'skip'
        result[user] = result_state

    socketio.emit('Waiting Update', result)

def login_user(user):
    rowcount = db.get_row_count(sql_user_select, (user['username'],))

    if rowcount == 0:
        # register then login
        return db.run_sql(sql_user_insert, (user['username'],), fetch='one')
    if rowcount == 1:
        # login
        return db.run_sql(sql_user_select, (user['username'],), fetch='one')
    if rowcount > 1:
        logging.error("ERROR: There is more than one user with same name, I dont know what to do! PANIC!")

def set_user(user):
    logging.info("Updated User" + user['username'])
    return db.run_sql(sql_user_sub_update, (user['subscribed'], user['username']), fetch='one')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
