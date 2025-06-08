import enum, json
from typing import List
from . import Base, session
from .vendor import Vendor
from uuid import UUID
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import ForeignKey, select, exc, extract
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields
import logging

class BaseOrderSchema(Schema):
    state_id = fields.Str(required=True)
    order_fee = fields.Int(required=True)

class OrderState(enum.Enum):
    COLLECT = "collect"
    ORDER = "order"
    CLOSED = "closed"

    def __str__(self):
        return self.value


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    state_id: Mapped[OrderState] = mapped_column(default=OrderState.COLLECT)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"),nullable=True)
    date_of_order: Mapped[date]
    order_time: Mapped[datetime] = mapped_column(nullable=True)
    order_fee: Mapped[int] = mapped_column(default=0)
    total_price: Mapped[int] = mapped_column(default=0)

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    def __repr__(self):
        return f"Order<id={self.id},order_time={self.order_time},vendor_id={self.vendor_id},state_id={str(self.state_id)},user_id={self.user_id},date_of_order={self.date_of_order},order_time={self.order_time}>"

    def create_order(v_id: UUID, doo: date = date.today()):
        vendor = Vendor.find_by_id(v_id)
        order = Order(vendor_id=v_id, date_of_order=doo, order_fee=vendor.settings["transport_price"]["value"])
        session.add(order)
        try:
            session.commit()
            session.refresh(order)
            return True, order
        except exc.DataError as e:
            logging.exception("DataError during order add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def get_by_id(order_id):
        stmt = select(Order).where(Order.id == order_id)
        return session.execute(stmt).scalars().first()


    def last_7_days_statistics():
        result = {}
        last_7_days = [(date.today() - relativedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        last_7_days.reverse()
        for vendor in Vendor.find_all_active():
            result[vendor.name] = {
            "data": []
            }
            for day in last_7_days:
                parsed_date = datetime.strptime(day, "%Y-%m-%d")
                result[vendor.name]["data"].append(Order.day_sum_by_vendor(vendor.id, parsed_date.year, parsed_date.month, parsed_date.day))

        return result, last_7_days


    def last_12_month_statistics():
        result = {}
        last_12_months = [(date.today() - relativedelta(months=i)).strftime("%Y-%m") for i in range(12)]
        last_12_months.reverse()
        for vendor in Vendor.find_all_active():
            result[vendor.name] = {
                "data": []
            }
            for month in last_12_months:
                parsed_date = datetime.strptime(month, "%Y-%m")
                result[vendor.name]["data"].append(Order.month_sum_by_vendor(vendor.id, parsed_date.year, parsed_date.month))


        return result, last_12_months


    def month_sum_by_vendor(vendor_id, year, month):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            extract("year", Order.date_of_order) == year,
            extract("month", Order.date_of_order) == month
        )

        orders = session.execute(stmt).scalars()
        sum = 0
        for order in orders:
            for basket_entry in order.items:
                sum += basket_entry.count * basket_entry.size.price
            if len(order.items) != 0:
                sum += order.order_fee


        return sum

    def day_sum_by_vendor(vendor_id, year, month, day):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            extract("year", Order.date_of_order) == year,
            extract("month", Order.date_of_order) == month,
            extract("day", Order.date_of_order) == day
        )

        orders = session.execute(stmt).scalars()
        sum = 0
        for order in orders:
            for basket_entry in order.items:
                sum += basket_entry.count * basket_entry.size.price
            if len(order.items) != 0:
                sum += order.order_fee


        return sum


    def find_all(limit=None, offset=0):
        stmt = select(Order).order_by(Order.date_of_order.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return session.execute(stmt).scalars().all()

    def find_open_order_by_date_for_a_vendor(vendor_id: UUID, date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == date,
            Order.state_id != OrderState.CLOSED)
        return session.execute(stmt).scalars().first()

    def find_order_by_date_for_a_vendor(vendor_id: UUID, date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == date)
        return session.execute(stmt).scalars().first()

    def find_order_between(date_from, date_to):
        stmt = select(Order).where(
            Order.date_of_order.between(date_from, date_to)
        )
        return session.execute(stmt).all()

    def find_order_participants(order_id):
        from .user import User
        from .user_basket import UserBasket
        stmt = select(User).distinct().join(
                UserBasket, User.id == UserBasket.user_id
            ).where(
                UserBasket.order_id == order_id
            )
        return session.execute(stmt).all()

    def get_users(self):
        from .user import User
        from .user_basket import UserBasket
        stmt = select(User).distinct().join(
                UserBasket, User.id == UserBasket.user_id
            ).where(
                UserBasket.order_id == self.id
            )
        return session.execute(stmt).all()

    def change_state(self, new_state, user_id=None):
        from .order_item import OrderItem

        if self.state_id == OrderState.CLOSED and new_state != OrderState.CLOSED:
            OrderItem.delete_order(self.id)

        self.state_id = new_state
        self.order_by = user_id
        if self.state_id == OrderState.CLOSED:

            order_price = 0
            for basket in self.items:
                ok, order_item = OrderItem.create(basket)
                if ok:
                    order_price += order_item.total_price
            order_price += self.order_fee
            self.total_price = order_price
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during order add")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def set_order_fee(self, fee):
        self.order_fee = fee
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during order add")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "vendor": str(self.vendor.name),
            "state_id": str(self.state_id),
            "user_id": str(self.user_id),
            "date_of_order": self.date_of_order.strftime("%Y-%m-%d"),
            "order_time": self.order_time,
            "order_fee": self.order_fee,
            "total_price": self.total_price
        }
