from sqlalchemy import Column, Text, Enum, select, delete
from uuid import UUID, uuid4
from . import Base, session
from .size import Size
from .menu_item import MenuItem
from .user_basket import UserBasket
import enum
import logging
from typing import List
from sqlalchemy import ForeignKey, exc, func, or_
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    menu_item_id: Mapped[int] = mapped_column()
    size_id: Mapped[int] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    count: Mapped[int]

    # Snapshotted data
    item_name: Mapped[str]
    size_label: Mapped[str]
    unit_price: Mapped[int]
    total_price: Mapped[int]

    # Relationships (optional)
    order: Mapped["Order"] = relationship(back_populates="order_items")
    user: Mapped["User"] = relationship()

    def __repr__(self):
        return f"OrderItem<{self.id},order_id={self.order_id},user_id={self.user_id},item_name={self.item_name}>"

    def create(user_basket: UserBasket):
        order_item = OrderItem(
            order_id = user_basket.order_id,
            menu_item_id = user_basket.menu_item_id,
            size_id = user_basket.size_id,
            user_id = user_basket.user_id,
            count = user_basket.count,
            item_name = user_basket.item.name,
            size_label = user_basket.size.name,
            unit_price = user_basket.size.price,
            total_price = user_basket.size.price * user_basket.count
            )
        session.add(order_item)
        try:
            session.commit()
            session.refresh(order_item)
            return True, order_item
        except exc.DataError as e:
            logging.exception("DataError during OrderItem add. rolling back")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def delete_order(order_id):
        stmt = delete(OrderItem).where(
            OrderItem.order_id == order_id
        )

        session.execute(stmt)

        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during OrderItems delete")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False
