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
        session = Session()
        menu = session.query(Menu).filter(Menu.menu_date == date.today().strftime('%Y-%m-%d')).first()
        session.close()
        result = {}
        if not menu:
            return result

        for menu_item in menu.menu:
            result[menu_item['id']]=menu_item['link']
        return result

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
                    'label': menu_item['label'],
                    'date': menu.menu_date.strftime('%Y-%m-%d')
                }
                for menu_item_size in menu_item['sizes']:
                    result[menu_item['id']][menu_item_size['size']] = {
                        'price': menu_item_size['price'],
                        'link': menu_item_size['link']
                    }
        return result
