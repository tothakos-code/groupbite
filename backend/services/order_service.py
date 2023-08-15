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
        return True

    def replace_userid_with_username(order_date):
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        session.close()
        if not order:
            return {}
        basket = order.basket
        new_basket = {}
        user_ids = basket.keys()
        for user_id in user_ids:
            new_basket[UserService.id_to_username(user_id)] = basket[user_id]
        return new_basket

    def inject_label_and_price(basket):
        current_menu = MenuService.get_menu_as_dict()
        for basket_item in basket.values():
            basket_item['price'] = current_menu[basket_item['id']][basket_item['size']]['price']
            basket_item['label'] = current_menu[basket_item['id']]['label']
        return basket
