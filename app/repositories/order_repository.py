from app.entities.order_item import OrderItem
from app.entities.order import Order, OrderState
from app.entities.user import User
from app.entities.user_basket import UserBasket
from sqlalchemy import ForeignKey, select, exc, extract, Index, text, func, and_
from typing import Optional
from datetime import date
from uuid import UUID

class OrderRepository:

    def __init__(self, db):
        self.db = db

    def get_by_id(self, order_id) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        return self.db.execute(stmt).scalars().first()

    def find_orders_between_dates(self,  start, end):
        stmt = select(
            Order
        ).where(
            Order.date_of_order.between(start, end)
        )
        return self.db.execute(stmt).scalars().all()

    def find_user_order_dates_between(self, user_id, start, end):
        stmt = select(
            Order
        ).join(
            Order.order_items
        ).where(
            OrderItem.user_id == user_id,
            Order.date_of_order.between(start, end)
        )
        return self.db.execute(stmt).scalars().all()

    def find_all(self, limit=None, offset=0):
        stmt = select(Order).order_by(Order.date_of_order.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def find_open_order_by_date_for_a_vendor(self, vendor_id: UUID, order_date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == order_date,
            Order.state_id != OrderState.CLOSED)
        return self.db.execute(stmt).scalars().first()

    def find_order_by_date_for_a_vendor(self, vendor_id: UUID, order_date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == order_date)
        return self.db.execute(stmt).scalars().first()

    def find_order_between(self, date_from, date_to):
        stmt = select(Order).where(
            Order.date_of_order.between(date_from, date_to)
        )
        return self.db.execute(stmt).all()

    def find_order_participants(self, order):
        if order.state_id == OrderState.CLOSED:
            # Closed order → participants come from OrderItem
            stmt = (
                select(User)
                .distinct()
                .join(OrderItem, User.id == OrderItem.user_id)
                .where(OrderItem.order_id == order.id)
            )
        else:
            # Open (or other) state → participants come from UserBasket
            stmt = (
                select(User)
                .distinct()
                .join(UserBasket, User.id == UserBasket.user_id)
                .where(UserBasket.order_id == order.id)
            )

        return self.db.execute(stmt).scalars().all()

    def save(self, order: Order):
        self.db.add(order)

    def get_daily_sums(self, start_date: date, end_date: date, vendors_ids: list):
        daily_sums_query = (
            select(
                Order.vendor_id,
                Order.date_of_order,
                func.coalesce(func.sum(Order.total_price), 0).label('daily_sum')  # Adjust column name as needed
            )
            .where(
                and_(
                    Order.date_of_order >= start_date,
                    Order.date_of_order <= end_date,
                    Order.vendor_id.in_(vendors_ids)
                )
            )
            .group_by(
                Order.vendor_id,
                Order.date_of_order
            )
        )

        return self.db.execute(daily_sums_query).all()

    def get_monthly_sums(self, start_date: date, end_date: date, vendors_ids: list):
        monthly_sums_query = (
            select(
                Order.vendor_id,
                extract('year', Order.date_of_order).label('year'),
                extract('month', Order.date_of_order).label('month'),
                func.coalesce(func.sum(Order.total_price), 0).label('monthly_sum')  # Adjust column name as needed
            )
            .where(
                and_(
                    Order.date_of_order >= start_date,
                    Order.date_of_order <= end_date,
                    Order.vendor_id.in_(vendors_ids)
                )
            )
            .group_by(
                Order.vendor_id,
                extract('year', Order.date_of_order),
                extract('month', Order.date_of_order)
            )
        )

        return self.db.execute(monthly_sums_query).all()
