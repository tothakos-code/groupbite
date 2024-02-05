from bs4 import BeautifulSoup
from flask import Blueprint, request
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
import requests,json,re
import logging

from app.controllers import menu_blueprint
from app.entities.menu import Menu
from app.entities import Session
from app.services.menu_service import MenuService
from app.services.vendor_service import VendorService
from app.vendor_factory import VendorFactory
from app.base_vendor import BaseVendor

target_url = 'https://falusitekercsgyorsetterem.pgg.hu/falusitekercsgyorsetterem/etlap/'

napok = ["hetfoi","keddi", "szerdai","csutortoki","penteki","szombati","vasarnapi"]
fdidpattern = r"\/fdid-[0-9]+\/"



@menu_blueprint.route('/update-all')
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
        logging.warning("Updating menu " + start_date)
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
    session.close()
    return "Menu updated succesfully", 201

@menu_blueprint.route('/update/<vendor_id>')
def update_menu(vendor_id):
    vendor = VendorFactory.get_one_vendor_object(int(vendor_id))
    if vendor:
        logging.warning(vendor)
        vendor.scan()
        return "Vendor scan ran for " + str(vendor.id) + " id", 201

    else:
        return "No vendor with that id", 404


@menu_blueprint.route('/get', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_blueprint.route('/get/<requested_date>')
def get_requested_menu(requested_date=date.today().strftime('%Y-%m-%d')):
    requested_menu = MenuService.get_menu_by_date(requested_date)
    if requested_menu:
        return json.dumps(requested_menu.menu)
    return []


@menu_blueprint.route('/get_week', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_blueprint.route('/get_week/<requested_date>')
def get_week_requested_menu(requested_date=date.today().strftime('%Y-%m-%d')):
    # start of the week:
    today = date.today()
    start_date = today - timedelta(days=today.weekday())

    end_date = start_date + timedelta(days=6)

    delta = timedelta(days=1)

    result = {}
    while (start_date <= end_date):
        requested_menu = MenuService.get_menu_by_date(start_date.strftime('%Y-%m-%d'))
        if requested_menu:
            result[start_date.weekday()] = json.dumps(requested_menu.menu)
        else:
            result[start_date.weekday()] = {}
        # stepping to the next day
        start_date += delta
    return result


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
