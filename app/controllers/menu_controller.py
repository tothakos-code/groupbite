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
