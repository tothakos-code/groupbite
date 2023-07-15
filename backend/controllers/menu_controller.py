from flask import Blueprint, request
from entities.menu import Menu, MenuSchema

from flask import request
import requests,json,re
from bs4 import BeautifulSoup
import datetime
from datetime import date
from sqlalchemy import func, cast

from entities.entity import Session

napok = ["hetfoi","keddi", "szerdai","csutortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"

menu_controller = Blueprint('menu_controller', __name__, url_prefix='/menu')

@menu_controller.route('/update')
def add_or_update_menu():
    # get menu from target
    new_menu = request_new_menu(request.args.get('day'))

    # Check if the menu already exists in the database
    session = Session()
    # TODO: How can i query by menu_date = CURRENT_DATE
    existing_menu = session.query(Menu).filter(func.date_trunc('day', Menu.menu_date) == date.today()).first()

    result = 'added'
    if existing_menu:
        # Update the existing menu using a complex method

        existing_menu.menu = existing_menu.update(new_menu)
        result = 'updated'
    else:
        # Create a new menu and add it to the database
        session.add(Menu(new_menu))

    session.commit()

    return {'message': f'Menu {result} successfully'}

@menu_controller.route('/get')
def get_todays_menu():
    # fetching from the database
    session = Session()
    todays_menu = session.query(Menu).filter(func.date_trunc('day', Menu.menu_date) == date.today()).first()

    # serializing as JSON
    session.close()
    return json.dumps(todays_menu.menu, indent=4)

def request_new_menu(requestedDay=None):
    # Requesting and parsing th HTML
    result = requests.get('https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/')
    soup = BeautifulSoup(result.content, 'html.parser')

    # Getting the current day
    if requestedDay is None or requestedDay == 'undefined':
        day = datetime.datetime.today().weekday()
    else:
        day = int(requestedDay) - 1

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
