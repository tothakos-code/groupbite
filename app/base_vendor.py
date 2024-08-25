from app.entities.vendor import VendorType
from app.entities.menu import Menu, Frequency
from app.entities.menu_item import MenuItem

import logging

class BaseVendor(object):
    def __init__(self, name, id=-1, configuration={}, settings={}):
        self.name = name
        self.id = id
        self.type = VendorType.BASIC
        self.settings = settings

    def scan(self):
        raise NotImplementedError("Subclasses must implement the scan method")

    def test(self):
        raise NotImplementedError("Subclasses must implement the test method")

    def get(self):
        raise NotImplementedError("Subclasses must implement the get method")

    def get_menu(self, date, filter=[]):
        menus = Menu.find_vendor_all_menu(self.id, date)
        menuids = [menu.id for menu in menus]
        logging.info(menuids)
        items = MenuItem.find_all_by_menu_list(menuids, filter)
        result = []
        for i in items:
            result.append(i.serialized)
        # result = [menu.serialized for menu in requested_menu]
        return result
