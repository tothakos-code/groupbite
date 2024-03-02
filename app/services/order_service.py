from datetime import date, timedelta, datetime
import logging

import json
from app.entities import Session
from app.entities.order import Order, OrderState
from app.entities.user_basket import UserBasket
from app.services.user_service import UserService
from app.services.menu_service import MenuService


class OrderService:
    """docstring for OrderService."""
    def get_user_basket(user, date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        order = session.query(Order).filter(Order.order_date == date).first()
        session.close()
        if not order or not str(UserService.username_to_id(user)) in order.basket:
            return {}
        return order.basket[str(UserService.username_to_id(user))]

    def get_formated_full_basket(order_id):
        result = []
        for basket_entry in UserBasket.find_items_by_order(order_id):
            result.append(basket_entry.basket_format)
        return json.dumps(result)

    def replace_userid_with_username(order_date):
        order = Order.find_open_order_by_date_for_a_vendor("de06edb7-24db-4869-b476-0ca14d4f1cb6", order_date)
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
            return str(OrderState.COLLECT)

        return str(order_state.order_state)


    def set_order_state(new_state, order_date=date.today().strftime('%Y-%m-%d')):
        """Setter for today's order state"""
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        if not order:
            session.close()
            return str(OrderState.COLLECT)

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
