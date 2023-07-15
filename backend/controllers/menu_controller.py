from flask import Blueprint, request
from entities.menu import Menu, MenuSchema

from flask import request
import requests,json,re
from bs4 import BeautifulSoup
import datetime
from datetime import date
from sqlalchemy import func, cast

from entities.entity import Session

target_url = 'https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/'

napok = ["hetfoi","keddi", "szerdai","csutortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"

menu_controller = Blueprint('menu_controller', __name__, url_prefix='/menu')

@menu_controller.route('/update', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_controller.route('/update/<requested_date>')
def add_or_update_menu(requested_date):
    # get menu from target
    new_menu = request_new_menu(date(*map(int, requested_date.split('-'))))

    # Check if the menu already exists in the database
    session = Session()
    existing_menu = session.query(Menu).filter(func.date_trunc('day', Menu.menu_date) == requested_date).first()

    result = 'added'
    if existing_menu:
        # Update the existing menu using a complex method

        existing_menu.menu = existing_menu.update(new_menu)
        result = 'updated'
    else:
        # Create a new menu and add it to the database
        session.add(Menu(requested_date,new_menu))

    session.commit()

    return {'message': f'Menu {result} successfully'}

@menu_controller.route('/get', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_controller.route('/get/<requested_date>')
def get_todays_menu(requested_date):
    # fetching from the database
    session = Session()
    requested_menu = session.query(Menu).filter(func.date_trunc('day', Menu.menu_date) == requested_date).first()
    session.close()
    if requested_menu:
        return json.dumps(requested_menu.menu, indent=4)
    return []

def request_new_menu(requestedDay):
    # Requesting and parsing th HTML
    result = requests.get(target_url)
    soup = BeautifulSoup(result.content, 'html.parser')

    day = requestedDay.weekday()
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
