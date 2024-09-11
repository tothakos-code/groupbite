import enum, json
from typing import List
from . import Base, session
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    order_fee: Mapped[int]

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    def __repr__(self):
        return f"Order<id={self.id},order_time={self.order_time},vendor_id={self.vendor_id},state_id={str(self.state_id)},user_id={self.user_id},date_of_order={self.date_of_order},order_time={self.order_time}>"

    def create_order(v_id: UUID, doo: date = date.today()):
        order = Order(vendor_id=v_id,date_of_order=doo)
        session.add(order)
        session.commit()

        return order

    def get_by_id(order_id):
        stmt = select(Order).where(Order.id == order_id)
        return session.execute(stmt).scalars().first()

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

    def change_state(self, new_state, user_id=None):
        self.state_id = new_state
        self.order_by = user_id
        session.commit()

    def set_order_fee(self, fee):
        self.order_fee = fee
        session.commit()

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "state_id": str(self.state_id),
            "user_id": str(self.user_id),
            "date_of_order": self.date_of_order.strftime("%Y-%m-%d"),
            "order_time": self.order_time,
            "order_fee": self.order_fee
        }
