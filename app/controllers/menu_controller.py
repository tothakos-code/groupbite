from bs4 import BeautifulSoup
from flask import Blueprint, request
from datetime import date, timedelta, datetime
from sqlalchemy import func, cast
import requests,json,re
import logging

from app.controllers import menu_blueprint
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.entities import Session
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
        requested_menu = Menu.find_by_date(start_date.strftime('%Y-%m-%d'))
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
    return json.dumps(result)


@menu_blueprint.route('/<vendor_id>/item-add', methods=['POST'])
def handle_menu_item_add(vendor_id):
    item = request.json['data']
    menu = request.json['menu']

    menu_item = MenuItem(
        menu_id=menu,
        name=item['name'],
        category=item['category']
    )
    menu_item.sizes.append(Size(
        link="",
        name=item['size'],
        price=item['price'],
        index=0,
        quantity=item['quantity'],
    ))

    MenuItem.add(menu_item)
    return "OK"

@menu_blueprint.route('/<vendor_id>/item-size-add', methods=['POST'])
def handle_menu_item_size_add(vendor_id):
    size = request.json['data']
    item_id = request.json['item']

    Size.add(
        Size(
            menu_item_id=item_id,
            link="",
            name=size['name'],
            price=size['price'],
            quantity=size['quantity'],
        )
    )
    return "OK"


@menu_blueprint.route('/<vendor_id>/item-update', methods=['POST'])
def handle_menu_item_update(vendor_id):
    item = request.json['data']
    item_db = MenuItem.find_by_id(item['id']).update(
        item['name'],
        item['index'],
        item['category']
    )
    return json.dumps(item_db)


@menu_blueprint.route('/<vendor_id>/item-size-update', methods=['POST'])
def handle_menu_item_size_update(vendor_id):
    size = request.json['data']
    item_id = request.json['item']

    size_db = Size.find_by_id(size['id'])
    if size_db:
        size_db.update(
            size['name'],
            size['price'],
            size['quantity'],
            size['index']
        )
    else:
        size_db = Size(
            menu_item_id=item_id,
            link="",
            name=size['name'],
            price=size['price'],
            quantity=size['quantity'],
            index=size['index']
        )
        Size.add(size_db)
    return json.dumps(size_db.serialized)


@menu_blueprint.route('/<vendor_id>/item-delete', methods=['POST'])
def handle_menu_item_delete(vendor_id):
    item = request.json['data']
    MenuItem.find_by_id(item['id']).delete()
    return "OK"


@menu_blueprint.route('/<vendor_id>/item-size-delete', methods=['POST'])
def handle_menu_item_size_delete(vendor_id):
    size = request.json['data']
    Size.find_by_id(size['id']).delete()
    return "OK"


@menu_blueprint.route('/<vendor_id>/menu-get', methods=['GET'])
def handle_menu_get(vendor_id):
    menus = Menu.find_all_by_vendor(vendor_id)
    result = []
    for m in menus:
        result.append(m.serialized)
    return json.dumps(result)


@menu_blueprint.route('/<vendor_id>/menu-update', methods=['POST'])
def handle_menu_update(vendor_id):
    menu = request.json['data']
    menu_db = Menu.find_by_id(menu['id']).update(menu['name'], menu['date'])
    return json.dumps(menu_db)


@menu_blueprint.route('/<vendor_id>/menu-delete', methods=['POST'])
def handle_menu_delete(vendor_id):
    menu = request.json['data']
    Menu.find_by_id(menu['id']).delete()
    return "OK"


@menu_blueprint.route('/<vendor_id>/menu-add', methods=['POST'])
def handle_menu_add(vendor_id):
    menu = request.json['data']
    Menu.add(Menu(name=menu['name'], vendor_id=vendor_id, freq_id=menu['freq']))
    return "OK"
