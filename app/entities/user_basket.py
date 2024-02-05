from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base
from marshmallow import Schema, fields
import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class UserBasket(Base):
    __tablename__ = 'user_basket'

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_item.id"), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), primary_key=True)
    count: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="items")
    user: Mapped["User"] = relationship(back_populates="orders")
    item: Mapped["MenuItem"] = relationship(back_populates="orders")

    def __repr__():
        return "Menu"

    @property
    def serialized(self):
        return {
            'user_id': self.user_id,
            'menu_item_id': self.menu_item_id,
            'order_id': self.order_id,
            'count': self.price
        }

# class UserBasketSchema(Schema):
#     id = fields.Integer()
#     menu_id = fields.Integer()
#     name = fields.String()
#     count = fields.Integer()
