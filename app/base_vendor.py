from app.entities.vendor import VendorType
from app.entities.menu import Menu, Frequency

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

    def get_menu(self, date):
        requested_menu = Menu.find_vendor_all_menu(self.id, date)
        result = []
        temp_result = []
        for menu in requested_menu:
            logging.info(menu)
            # merging items with multiple sizes,
            # TODO: maybe rethink how sizes are handled
            unique_items = set(item.name for item in menu.items)
            for value in unique_items:
                keys = [{"id":dic.id, "size":dic.size, "price":dic.price} for dic in menu.items if dic.name == value]
                temp_result.append({"name":value,"sizes":keys})

        for menu in requested_menu:
            for item in menu.items:
                for temp_item in temp_result:
                    if temp_item['name'] == item.name:
                        result.append(temp_item)
                        temp_result.remove(temp_item)
                        break
        return result
