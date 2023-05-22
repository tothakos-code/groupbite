from flask import Flask
from flask import request
import psycopg2
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
import logging
import datetime

app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True)

app.config['SECRET_KEY'] = 'secret!'


napok = ["hetfoi","keddi", "szerdai","csotortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"
sidfdpattern = r"\/sidfd-[0-9]+\/"

sql_select = "SELECT basket FROM orders WHERE order_date = CURRENT_DATE"
sql_insert = "INSERT INTO orders (basket) values (%s) RETURNING basket"
sql_update = "UPDATE orders SET basket = %s WHERE order_date = CURRENT_DATE RETURNING basket"



def db_connection():
    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(
    host="database",
    database="falusi",
    user="falusi",
    password="falusi")
    return conn

@app.route('/')
def hello():
    return "Welcome to this api on a pi!"

@app.route('/transferBasket', methods=['POST'])
def transfer_basket():
    PHPSESSIONID = request.json['psid']
    orders = None

    conn = None
    try:
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute(sql_select)
        orders = cur.fetchone()[0]
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
    finally:
        if conn is not None:
            conn.close()
            logging.error('Database connection closed.')

    if orders is None:
        return "Error: basket empty or could not get basket from database."

    # Create the list of item links
    orderList = []
    for person, basket in orders.items():
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
    for link in orderList:
        sizeid = re.search(sidfdpattern, link).group().replace('/','').split('-')[1]

        requests_data={
            "item_cnt": "1",
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
            cookies={"PHPSESSID":PHPSESSIONID}
        )
    return 'OK'


@app.route('/getetlap')
def get_etlap():
    # Requesting and parsing th HTML
    r = requests.get('https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Getting the current day
    day = datetime.datetime.today().weekday()
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
    logging.warning("Socket.IO connection established")

@socketio.on('Server Basket Update')
def handle_basket_update(data):
    conn = None
    try:
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()

        # Get the user
        user = list(data.keys())[0]

        # execute a statement
        cur.execute(sql_select)

        # display the PostgreSQL database server version
        if cur.rowcount == 0:
            # insert row
            # creeate basket and add user
            currentBasket = {}
            currentBasket[user] = data[user]

            cur.execute(sql_insert, (json.dumps(currentBasket),))
            logging.warning("Created today's basket row")
            conn.commit()
            socketio.emit('Client Basket Update', {'basket': cur.fetchone()[0] })
        elif cur.rowcount == 1:
            # update row
            # get basket and update user
            currentBasket = cur.fetchone()[0]
            currentBasket[user] = data[user]

            logging.warning("Updated today's basket row")
            cur.execute(sql_update, (json.dumps(currentBasket),))
            conn.commit()
            socketio.emit('Client Basket Update', {'basket': cur.fetchone()[0] })
        elif cur.rowcount > 1:
            # error this is sould be impossible
            logging.warning("ERROR: There is more than one order, I dont know what to do! PANIC!")

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
    finally:
        if conn is not None:
            conn.close()
            logging.error('Database connection closed.')



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
