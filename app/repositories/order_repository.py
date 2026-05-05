from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, extract, func, select

from app.entities.order import Order, OrderState
from app.entities.order_item import OrderItem
from app.entities.user import User
from app.entities.user_basket import UserBasket


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, order_id) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        return self.db.execute(stmt).scalars().first()

    def find_orders_between_dates(self, start, end):
        stmt = select(Order).where(Order.open_from.between(start, end))
        return self.db.execute(stmt).scalars().all()

    def find_user_order_dates_between(self, user_id, start, end):
        stmt = (
            select(Order)
            .join(Order.order_items)
            .where(
                OrderItem.user_id == user_id, Order.open_from.between(start, end)
            )
        )
        return self.db.execute(stmt).scalars().all()

    def find_all(self, limit=None, offset=0):
        stmt = select(Order).order_by(Order.open_from.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def find_open_order_for_vendor(
        self, vendor_id: UUID, reference_date: date = None
    ) -> Optional[Order]:
        reference_date = reference_date or date.today()
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.open_from <= reference_date,
            func.coalesce(Order.open_until, Order.open_from) >= reference_date,
            Order.state_id != OrderState.CLOSED,
        )
        return self.db.execute(stmt).scalars().first()

    def find_order_by_date_for_a_vendor(
        self, vendor_id: UUID, reference_date: date = None
    ) -> Optional[Order]:
        reference_date = reference_date or date.today()
        if isinstance(reference_date, str):
            reference_date = date.fromisoformat(reference_date)
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.open_from <= reference_date,
            func.coalesce(Order.open_until, Order.open_from) >= reference_date,
        )
        return self.db.execute(stmt).scalars().first()

    def find_future_open_orders_for_vendor(self, vendor_id: UUID) -> list:
        """Returns non-CLOSED orders whose open_from is strictly after today."""
        today = date.today()
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.open_from > today,
            Order.state_id != OrderState.CLOSED,
        )
        return self.db.execute(stmt).scalars().all()

    def find_open_orders_with_close_time(self) -> list:
        """Returns non-CLOSED orders that have a close_time set and are still in their window."""
        today = date.today()
        stmt = select(Order).where(
            Order.close_time.isnot(None),
            Order.state_id != OrderState.CLOSED,
            func.coalesce(Order.open_until, Order.open_from) >= today,
        )
        return self.db.execute(stmt).scalars().all()

    def find_order_between(self, date_from, date_to):
        stmt = select(Order).where(Order.open_from.between(date_from, date_to))
        return self.db.execute(stmt).all()

    def find_order_participants(self, order):
        if order.state_id == OrderState.CLOSED:
            stmt = (
                select(User)
                .distinct()
                .join(OrderItem, User.id == OrderItem.user_id)
                .where(OrderItem.order_id == order.id)
            )
        else:
            stmt = (
                select(User)
                .distinct()
                .join(UserBasket, User.id == UserBasket.user_id)
                .where(UserBasket.order_id == order.id)
            )

        return self.db.execute(stmt).scalars().all()

    def has_overlapping_open_order(
        self, vendor_id: UUID, open_from: date, open_until: date
    ) -> bool:
        """Returns True if any non-CLOSED order for the vendor overlaps the given window."""
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.state_id != OrderState.CLOSED,
            Order.open_from <= open_until,
            func.coalesce(Order.open_until, Order.open_from) >= open_from,
        )
        return self.db.execute(stmt).scalars().first() is not None

    def save(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def delete(self, order: Order):
        self.db.delete(order)
        self.db.flush()

    def get_daily_sums(self, start_date: date, end_date: date, vendors_ids: list):
        daily_sums_query = (
            select(
                Order.vendor_id,
                Order.open_from,
                func.coalesce(func.sum(Order.total_price), 0).label("daily_sum"),
            )
            .where(
                and_(
                    Order.open_from >= start_date,
                    Order.open_from <= end_date,
                    Order.vendor_id.in_(vendors_ids),
                )
            )
            .group_by(Order.vendor_id, Order.open_from)
        )

        return self.db.execute(daily_sums_query).all()

    def get_monthly_sums(self, start_date: date, end_date: date, vendors_ids: list):
        monthly_sums_query = (
            select(
                Order.vendor_id,
                extract("year", Order.open_from).label("year"),
                extract("month", Order.open_from).label("month"),
                func.coalesce(func.sum(Order.total_price), 0).label("monthly_sum"),
            )
            .where(
                and_(
                    Order.open_from >= start_date,
                    Order.open_from <= end_date,
                    Order.vendor_id.in_(vendors_ids),
                )
            )
            .group_by(
                Order.vendor_id,
                extract("year", Order.open_from),
                extract("month", Order.open_from),
            )
        )

        return self.db.execute(monthly_sums_query).all()
