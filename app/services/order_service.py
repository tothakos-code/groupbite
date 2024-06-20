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

        if not order or not str(UserService.username_to_id(user)) in order.basket:
            return {}
        return order.basket[str(UserService.username_to_id(user))]

    def get_formated_full_basket(order_id):
        result = []
        for basket_entry in UserBasket.find_items_by_order(order_id):
            result.append(basket_entry.basket_format)
        return json.dumps(result)

    def get_formated_full_basket_group_by_user(order_id):
        result = {}
        for basket_entry in UserBasket.find_items_by_order(order_id):
            if str(basket_entry.user_id) not in result:
                result[str(basket_entry.user_id)] = {
                    'username': basket_entry.user.username,
                    'user_id': str(basket_entry.user_id),
                    'basket_entry': []
                }
            result[str(basket_entry.user_id)]['basket_entry'].append(basket_entry.basket_format)
        return json.dumps(result)


    def get_basket(date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        db_basket = session.query(Order).filter(Order.order_date == date).first()


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



    def get_order_state(order_date=date.today().strftime('%Y-%m-%d')):
        """Returns to current order state value"""
        session = Session()
        order_state = session.query(Order).filter(Order.order_date == order_date).first()

        if not order_state:
            return str(OrderState.COLLECT)

        return str(order_state.order_state)


    def set_order_state(new_state, order_date=date.today().strftime('%Y-%m-%d')):
        """Setter for today's order state"""
        session = Session()
        order = session.query(Order).filter(Order.order_date == order_date).first()
        if not order:

            return str(OrderState.COLLECT)

        order.order_state = new_state
        session.commit()
        result_state = str(order.order_state)

        return result_state

    def get_user_basket_between(user_id, date_from=date.today().strftime('%Y-%m-%d'), date_to=date.today().strftime('%Y-%m-%d')):
        session = Session()
        orders = session.query(Order).filter(Order.order_date.between(date_from, date_to)).all()

        result = {}
        for order in orders:
            if not order or not str(user_id) in order.basket:
                continue
            result[str(order.order_date)] = order.basket[str(user_id)]

        return result
