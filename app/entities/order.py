import enum, json
from typing import List
from . import Base, session
from uuid import UUID
from datetime import datetime, date
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
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"),nullable=True)
    date_of_order: Mapped[date]
    order_time: Mapped[datetime] = mapped_column(nullable=True)

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    def __repr__(self):
        return f"Order(id={self.id},order_time={self.order_time})"

    def create_order(v_id: UUID, doo: date = date.today()):
        order = Order(vendor_id=v_id,date_of_order=doo)
        session.add(order)
        session.commit()
        session.close()
        return order

    def find_open_order_by_date_for_a_vendor(v_id: UUID, doo: date = date.today() ):
        return session.query(Order).filter(
            Order.vendor_id == v_id,
            Order.date_of_order == doo,
            Order.state_id == OrderState.COLLECT).first()

    @property
    def serialized(self):
        return {
            'id': self.id,
            'vendor_id': str(self.vendor_id),
            'state_id': str(self.state_id),
            'user_id': str(self.user_id),
            'date_of_order': self.date_of_order.strftime('%Y-%m-%d'),
            'order_time': self.order_time
        }
#
# class OrderSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Order
#         load_instance = True
