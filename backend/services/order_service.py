from entities.order import Order, OrderSchema, order_state_type
from datetime import date, timedelta, datetime
from entities.entity import Session

class OrderService:
    """docstring for OrderService."""
    def get_user_basket(user, date=date.today().strftime('%Y-%m-%d')):
        session = Session()
        order = session.query(Order).filter(Order.order_date == date).first()
        session.close()
        if not order:
            return {}
        return order.basket[user]
