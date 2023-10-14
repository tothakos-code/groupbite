from entities.menu import Menu, MenuSchema
from datetime import date, timedelta, datetime
from entities.entity import Session

class MenuService:
    """docstring for UserService."""
    def get_menu_by_date(requested_date=date.today().strftime('%Y-%m-%d')):
        # fetching from the database
        session = Session()
        requested_menu = session.query(Menu).filter(Menu.menu_date == requested_date).first()
        session.close()
        return requested_menu

    def get_all_fdid_with_link():
        # fetching from the database
        # start of the week:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)


        # fetching from the database
        session = Session()
        menus = session.query(Menu).filter(Menu.menu_date.between(start_date,end_date))
        session.close()
        result = {}
        if not menus:
            return result

        for menu in menus:
            for menu_item in menu.menu:
                for sizes in menu_item['sizes']:
                    result[menu_item['id'] + "-" + sizes['size']] = sizes['link']
        return result

    def is_menu_item_exist(basket_item):
        current_menu = MenuService.get_weeklymenu_as_dict()
        # menu item exist
        if not current_menu[basket_item['id']]:
            return False
        # the size exist
        if not current_menu[basket_item['id']][basket_item['size']]:
            return False
        return True


    def get_weeklymenu_as_dict():

        # start of the week:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)


        # fetching from the database
        session = Session()
        menus = session.query(Menu).filter(Menu.menu_date.between(start_date,end_date))
        session.close()
        result = {}
        if not menus:
            return result

        for menu in menus:
            for menu_item in menu.menu:
                result[menu_item['id']] = {
                    'name': menu_item['label'],
                    'date': menu.menu_date.strftime('%Y-%m-%d')
                }
                for menu_item_size in menu_item['sizes']:
                    result[menu_item['id']][menu_item_size['size']] = {
                        'price': menu_item_size['price'],
                        'link': menu_item_size['link']
                    }
        return result
