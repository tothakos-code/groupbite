from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base
from marshmallow import Schema, fields
import enum
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class MenuItem(Base):
    __tablename__ = 'menu_item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str]
    link: Mapped[str]
    size: Mapped[str]
    price: Mapped[int]

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="item")
    menu: Mapped["Menu"] = relationship(back_populates="items")

    def __repr__(self):
        return f"MenuItem<{self.id},menu_id={self.menu_id},size={self.size},price={self.price}>"

    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'price': self.price
        }

# class MenuItemSchema(Schema):
#     id = fields.Integer()
#     menu_id = fields.Integer()
#     name = fields.String()
#     size = fields.String()
#     price = fields.Integer()
