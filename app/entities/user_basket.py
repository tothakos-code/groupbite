from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base, session
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

    def __repr__(self):
        return "Menu"

    def find_items_by_order(order_id):
        return session.query(UserBasket).filter(UserBasket.order_id == order_id).all()

    def clear_items(user_id, order_id):
        user_basket = session.query(UserBasket).filter(
            UserBasket.order_id == order_id,
            UserBasket.user_id == user_id
        ).delete()
        return True

    def remove_item(user_id, menu_item_id, order_id):
        user_basket = session.query(UserBasket).filter(
            UserBasket.order_id == order_id,
            UserBasket.menu_item_id == menu_item_id,
            UserBasket.user_id == user_id
        ).first()

        if not user_basket:
            logger.error("Error: Cannot remove item. Item not found.")
        else:
            if user_basket.count == 1:
                session.delete(user_basket)
            else:
                user_basket.count -= 1

        session.commit()
        session.close()
        return user_basket

    def add_item(user_id, menu_item_id, order_id):
        user_basket = session.query(UserBasket).filter(
            UserBasket.order_id == order_id,
            UserBasket.menu_item_id == menu_item_id,
            UserBasket.user_id == user_id
        ).first()

        if not user_basket:
            user_basket = UserBasket(
                user_id = user_id,
                menu_item_id = menu_item_id,
                order_id = order_id,
                count = 1
            )
        else:
            user_basket.count += 1

        session.add(user_basket)
        session.commit()
        session.close()
        return user_basket

    @property
    def serialized(self):
        return {
            'user_id': str(self.user_id),
            'menu_item_id': self.menu_item_id,
            'order_id': self.order_id,
            'count': self.count
        }

    @property
    def basket_format(self):
        return {
            'user_id': str(self.user_id),
            'username': self.user.username,
            'item': self.item.serialized,
            'count': self.count
        }

# class UserBasketSchema(Schema):
#     id = fields.Integer()
#     menu_id = fields.Integer()
#     name = fields.String()
#     count = fields.Integer()
