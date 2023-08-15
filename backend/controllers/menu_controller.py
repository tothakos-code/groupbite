from flask import Blueprint, request
from entities.menu import Menu, MenuSchema

import requests,json,re
from bs4 import BeautifulSoup
import logging
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
from entities.entity import Session
from services.menu_service import MenuService

target_url = 'https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/'

napok = ["hetfoi","keddi", "szerdai","csutortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"

menu_controller = Blueprint('menu_controller', __name__, url_prefix='/menu')

@menu_controller.route('/update-all')
def add_or_update_all_menu():
    # Requesting and parsing the HTML
    result = requests.get(target_url)
    soup = BeautifulSoup(result.content, 'html.parser')

    # start of the week:
    today = date.today()
    start_date = today - timedelta(days=today.weekday())

    end_date = start_date + timedelta(days=6)

    delta = timedelta(days=1)

    session = Session()
    while (start_date <= end_date):
        logging.warning(start_date)
        new_menu = fetch_a_day(soup, napok[start_date.weekday()])

        # selecting current day
        existing_menu = session.query(Menu).filter(Menu.menu_date == start_date.strftime('%Y-%m-%d')).first()

        if existing_menu:
            # Update the existing menu
            existing_menu.menu = existing_menu.update(new_menu)
        else:
            # Create a new menu and add it to the database
            session.add(Menu(start_date.strftime('%Y-%m-%d'), new_menu))

        # stepping to the next day
        start_date += delta
    #
    session.commit()
    return "Menu updated succesfully", 201


@menu_controller.route('/get', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_controller.route('/get/<requested_date>')
def get_requested_menu(requested_date=date.today().strftime('%Y-%m-%d')):
    requested_menu = MenuService.get_menu_by_date(requested_date)
    if requested_menu:
        return json.dumps(requested_menu.menu)
    return []


def fetch_a_day(soup_obj, dayString):
    menu = []
    for li in soup_obj.find_all('li', class_='foods_' + dayString + '-menu'):
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
