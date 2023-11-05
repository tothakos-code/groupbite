from entities.order import Order, OrderSchema, order_state_type
from datetime import date, timedelta, datetime
from entities.entity import Session

from services.user_service import UserService
from services.menu_service import MenuService

import logging

class OrderService:
    """docstring for OrderService."""
    def get_user_basket(user, date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        order = session.query(Order).filter(Order.order_date == date).first()
        session.close()
        if not order or not str(UserService.username_to_id(user)) in order.basket:
            return {}
        return order.basket[str(UserService.username_to_id(user))]

    # this is not needed after the migration is complete-
    def migrate_to_userid_based_order(order_date):
        # check if this is already been migrated
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        for person in order.basket.keys():
            if not UserService.username_exist(person):
                session.close()
                return True

        # Migrate if not
        basket = order.basket
        migrated_basket = {}
        keys = basket.keys()
        for person in keys:
            migrated_basket[UserService.username_to_id(person)] = basket[person]
        order.basket = migrated_basket
        session.commit()
        session.close()
        return True

    def replace_userid_with_username(order_date):
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        session.close()
        if not order:
            return {}
        basket = order.basket
        basket_with_names = {}
        user_ids = basket.keys()
        for user_id in user_ids:
            basket_with_names[UserService.id_to_username(user_id)] = basket[user_id]
        return basket_with_names

    def inject_label_and_price(basket):
        current_menu = MenuService.get_weeklymenu_as_dict()
        for basket_item in basket.values():
            # skip notexistent menu items
            if not MenuService.is_menu_item_exist(basket_item):
                continue
            basket_item['price'] = current_menu[basket_item['id']][basket_item['size']]['price']
            basket_item['name'] = current_menu[basket_item['id']]['name']
            basket_item['date'] = current_menu[basket_item['id']]['date']
        return basket


    def get_basket(date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        db_basket = session.query(Order).filter(Order.order_date == date).first()
        session.close()

        if not db_basket:
            return {}
        return db_basket.basket


    def set_basket(new_basket, date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        db_basket = session.query(Order).filter(Order.order_date == date).first()

        if not db_basket:
            # insert
            session.add(Order(date, new_basket))
            logging.warning("Created today's basket row")
        else:
            # update
            db_basket.basket = new_basket
            logging.warning("Updated today's basket row")

        session.commit()
        session.close()


    def get_order_state(order_date=date.today().strftime('%Y-%m-%d')):
        """Returns to current order state value"""
        session = Session()
        order_state = session.query(Order).filter(Order.order_date == order_date).first()
        session.close()
        if not order_state:
            return str(order_state_type.collect)

        return str(order_state.order_state)


    def set_order_state(new_state, order_date=date.today().strftime('%Y-%m-%d')):
        """Setter for today's order state"""
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        if not order:
            session.close()
            return str(order_state_type.collect)

        order.order_state = new_state
        session.commit()
        result_state = str(order.order_state)
        session.close()
        return result_state

    def get_user_basket_between(user_id, date_from=date.today().strftime('%Y-%m-%d'), date_to=date.today().strftime('%Y-%m-%d')):
        session = Session()
        orders = session.query(Order).filter(Order.order_date.between(date_from, date_to)).all()
        session.close()
        result = {}
        for order in orders:
            if not order or not str(user_id) in order.basket:
                continue
            result[str(order.order_date)] = order.basket[str(user_id)]

        return result
