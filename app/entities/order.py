import enum, json
from typing import List
from . import Base, session
from uuid import UUID
from datetime import datetime,date
from marshmallow import Schema, fields
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class OrderState(enum.Enum):
    COLLECT = 'collect'
    ORDER = 'order'
    CLOSED = 'closed'

    def __str__(self):
        return self.value


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    state_id: Mapped[OrderState] = mapped_column(default=OrderState.COLLECT)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    date_of_order: Mapped[date]
    order_time: Mapped[datetime]

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    def __repr__():
        return f"Order(id={self.id},order_time={self.order_time})"

    def find_open_order_by_date_for_a_vendor(v_id: UUID, doo: date = date.today() ):
        return session.query(Order).filter(
            Order.vendor_id == v_id,
            Order.date_of_order == doo,
            Order.state_id == OrderState.COLLECT).first()

    @property
    def serialized(self):
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'state_id': self.state_id,
            'user_id': self.user_id,
            'order_time': self.order_time
        }
#
# class OrderSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Order
#         load_instance = True
