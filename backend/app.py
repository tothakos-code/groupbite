from flask import Flask
from redis import Redis
import requests,json,re
from bs4 import BeautifulSoup
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
redis = Redis(host='redis', port=6379)
socketio = SocketIO(app,logger=True, engineio_logger=True)

@app.route('/')
def hello():
    redis.incr('hits')
    counter = str(redis.get('hits'),'utf-8')
    return "Welcome to this webpage!, This webpage has been test viewed "+counter+" time(s)"

@app.route('/getetlap')
def get_etlap():
    r = requests.get('https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/')

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')

    cs = soup.find_all('li', class_='foods_vasarnapi-menu')

    menu = []
    for li in soup.find_all('li', class_='foods_vasarnapi-menu'):
        menuElement = {}
        menuElement['label'] = li.find('div',class_='fdr_name_img').find('div', class_='fooddrink_name').text.strip()

        pattern = r"\/fdid-[0-9]+\/"

        menuSizes = []
        for size in li.find('div',id='food_params').find_all('div', class_='food_dring_size'):
            menuSizeElement = {}
            menuSizeElement['link'] = size.find('a', class_='billadd_link', href=True)['href']
            menuElement['id'] = re.search(pattern, menuSizeElement['link']).group().replace('/','')
            menuSizeElement['size'] = size.find('a', class_='billadd_link').find('span', class_='size').text
            menuSizeElement['price'] = size.find('a', class_='billadd_link').find('span', class_='price').text
            menuSizeElement['label'] = menuSizeElement['size'] + ' ' + menuSizeElement['price']
            menuSizes.append(menuSizeElement)


        menuElement['sizes'] = menuSizes
        menu.append(menuElement)
    return menu

@socketio.on('connect')
def handle_connect(data):
    logging.warning("Conncetion")
    logging.warning(data)
    socketio.emit('after connect', {'data':'Let us learn Web Socket in Flask'})

@socketio.on('Server Basket Update')
def handle_basket_update(data):
    logging.warning("Basket Update")
    currentBasket = redis.json().get('basket')
    user = list(data.keys())[0]
    currentBasket[user] = data[user]
    logging.warning(user)
    logging.warning(data[user])

    redis.json().set('basket', '$', currentBasket)
    socketio.emit('Client Basket Update', {'basket': redis.json().get('basket') })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    redis.json().set('basket', '$', {})
