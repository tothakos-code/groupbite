from flask import Flask
from flask import request
from redis import Redis
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
import logging
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
redis = Redis(host='redis', port=6379)
socketio = SocketIO(app,logger=True, engineio_logger=True)

napok = ["hetfoi","keddi", "szerdai","csotortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"
sidfdpattern = r"\/sidfd-[0-9]+\/"

@app.route('/flush')
def flush():
    redis.flushdb()
    redis.json().set('basket', '$', {})
    return "DB flushed"

@app.route('/')
def hello():
    redis.incr('hits')
    counter = str(redis.get('hits'),'utf-8')
    return "Welcome to this webpage!, This webpage has been test viewed "+counter+" time(s)"

@app.route('/transferBasket', methods=['POST'])
def transfer_basket():
    PHPSESSIONID = request.json['psid']
    orders = redis.json().get('basket')

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
    currentBasket = redis.json().get('basket')
    user = list(data.keys())[0]
    currentBasket[user] = data[user]
    redis.json().set('basket', '$', currentBasket)
    socketio.emit('Client Basket Update', {'basket': redis.json().get('basket') })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    redis.json().set('basket', '$', {})
