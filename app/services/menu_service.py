from datetime import date, timedelta, datetime
from app.entities import session
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem

class MenuService:
    """docstring for UserService."""
    def get_menu_by_date(requested_date=date.today().strftime('%Y-%m-%d')):
        # fetching from the database
        requested_menu = session.query(Menu).filter(Menu.menu_date == requested_date).first()
        
        return requested_menu

    def get_all_fdid_with_link():
        # fetching from the database
        # start of the week:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)


        # fetching from the database
        menus = session.query(Menu).filter(Menu.menu_date.between(start_date,end_date))
        
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
        menus = session.query(Menu).filter(Menu.menu_date.between(start_date,end_date))
        
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

    def fill_menu(vendor_id, date_to_fill, raw_item_list):
        menu = Menu.find_vendor_menu(vendor_id, date_to_fill)
        if menu is None:
            logging.error("Menu to fill not found!")
            return
        # TODO: Handlig items that got out of stock
        for raw_menu_item in raw_item_list:
            found = False
            for item in menu.items:
                if item.name == raw_menu_item['name']:
                    found = True
                    break
            if found:
                continue

            session.add(
                MenuItem(
                    menu_id=menu.id,
                    name=raw_menu_item['name'],
                    link=raw_menu_item['link'],
                    size=raw_menu_item['size'],
                    price=raw_menu_item['price']
                )
            )

    # TODO: migrate this to Menu? idea: fat model thin controller
    def create_menu(name, vendor, date, freq):
        menu = Menu.find_vendor_menu(vendor,date)
        # TODO: Need to check that date corresponed to the frequency. This currently only works for daily types
        if menu is not None:
            return
        session.add(Menu(name=name, vendor_id=vendor, menu_date=date, freq_id=freq))
        session.commit()
        
