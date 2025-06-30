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

    def get_menus(self, date, filter=None):
        """
        Get menus for a specific date with proper ordering

        Args:
            date: The date to get menus for
            filter: Optional list of categories to filter by

        Returns:
            List of menu data with properly ordered items
        """
        if filter is None:
            filter = []

        menus = Menu.find_all_active(self.id, date)
        result = []
        
        for menu in menus:
            # Get items with proper ordering by category and index
            items = MenuItem.find_all_by_menu_list([menu.id], filter, limit=100)

            # Group items by category and maintain order
            categorized_items = {}
            for item in items:
                category = item.category or 'egyéb'
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item.serialized)

            # Sort categories alphabetically and flatten items
            result_items = []
            for category in sorted(categorized_items.keys(), key=lambda x: x.lower()):
                # Items within each category are already sorted by index from the query
                result_items.extend(categorized_items[category])

            result.append({
                "menu_id": menu.id,
                "from_date": str(menu.from_date),
                "to_date": str(menu.to_date),
                "items": result_items,
                "total_items": len(result_items),
                "categories": list(categorized_items.keys())
            })

        return result
