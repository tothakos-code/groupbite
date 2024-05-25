from bs4 import BeautifulSoup
from flask import Blueprint, request
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
import requests,json,re
import logging

from app.controllers import menu_blueprint
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities import Session
from app.services.menu_service import MenuService
from app.services.vendor_service import VendorService
from app.vendor_factory import VendorFactory
from app.base_vendor import BaseVendor


@menu_blueprint.route('/update/<vendor_id>')
def update_menu(vendor_id):
    vendor = VendorFactory.get_one_vendor_object(str(vendor_id))
    if vendor is None:
        return "No vendor found with that id", 404
    vendor.scan()
    return "Vendor scan ran for " + str(vendor.id) + " id", 201

@menu_blueprint.route('/get/<vendor_id>', defaults={'requested_date': date.today().strftime('%Y-%m-%d')})
@menu_blueprint.route('/get/<vendor_id>/<requested_date>')
def get_requested_menu(vendor_id, requested_date):
    vendor = VendorFactory.get_one_vendor_object(str(vendor_id))
    if vendor is None:
        return "No vendor found with that id", 404
    return json.dumps(vendor.get_menu(requested_date))


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


@menu_blueprint.route('/<vendor_id>/get-items/<menu_id>', methods=['GET'])
def handle_menu_get_items(vendor_id, menu_id):
    items = MenuItem.find_all_by_menu(menu_id)
    result = []
    for i in items:
        result.append(i.serialized)
    logging.info(result)
    return json.dumps(result)


@menu_blueprint.route('/<vendor_id>/item-add', methods=['POST'])
def handle_menu_item_add(vendor_id):
    item = request.json['data']
    menu = request.json['menu']
    MenuItem.add(MenuItem(menu_id=menu, name=item['name'], link="", size=item['size'], price=item['price']))
    return "OK"


@menu_blueprint.route('/<vendor_id>/get', methods=['GET'])
def handle_menu_get(vendor_id):
    menus = Menu.find_all_by_vendor(vendor_id)
    result = []
    for m in menus:
        result.append(m.serialized)
    logging.info(result)
    return json.dumps(result)


@menu_blueprint.route('/<vendor_id>/update', methods=['POST'])
def handle_menu_update(vendor_id):
    menu = request.json['data']
    menu_db = Menu.find_by_id(menu['id']).update(menu['name'], menu['date'])
    return json.dumps(menu_db)


@menu_blueprint.route('/<vendor_id>/delete', methods=['POST'])
def handle_menu_delete(vendor_id):
    menu = request.json['data']
    Menu.find_by_id(menu['id']).delete()
    return "OK"


@menu_blueprint.route('/<vendor_id>/add', methods=['POST'])
def handle_menu_add(vendor_id):
    menu = request.json['data']
    Menu.add(Menu(name=menu['name'], vendor_id=vendor_id, freq_id=menu['freq']))
    return "OK"
