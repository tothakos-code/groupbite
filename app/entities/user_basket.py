from sqlalchemy import Column, Text, Enum, select
from uuid import UUID
from . import Base, session
from .order import Order
from .menu_item import MenuItem
from .size import Size
import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import logging

class UserBasket(Base):
    __tablename__ = "user_basket"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_item.id"), primary_key=True)
    size_id: Mapped[int] = mapped_column(ForeignKey("size.id"), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), primary_key=True)
    count: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="items")
    user: Mapped["User"] = relationship(back_populates="orders")
    item: Mapped["MenuItem"] = relationship(back_populates="orders")
    size: Mapped["Size"] = relationship(back_populates="orders")

    def __repr__(self):
        return f"UserBasket<user_id={self.user_id},menu_item_id={self.menu_item_id},order_id={self.order_id},count={self.count}>"

    def find_items_by_order(order_id):
        stmt = select(UserBasket).where(UserBasket.order_id == order_id)
        return session.execute(stmt).scalars().all()

    def find_user_orders(user_id):
        stmt = select(UserBasket).where(UserBasket.user_id == user_id)
        return session.execute(stmt).scalars().all()

    def find_user_basket(user_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.user_id == user_id,
            UserBasket.order_id == order_id
        )
        return session.execute(stmt).scalars().all()

    def find_user_orders_by_date(user_id, date):
        stmt = select(UserBasket).where(UserBasket.user_id == user_id, UserBasket.order.date_of_order == date)
        return session.execute(stmt).all()

    def get_basket_group_by_user(order_id):
        result = {}
        for basket_entry in UserBasket.find_items_by_order(order_id):
            if str(basket_entry.user_id) not in result:
                result[str(basket_entry.user_id)] = {
                    "username": basket_entry.user.username,
                    "user_id": str(basket_entry.user_id),
                    "items": []
                }
            result[str(basket_entry.user_id)]["items"].append(basket_entry.basket_format)
        return result

    def find_user_order_dates(user_id):
        stmt = select(
            UserBasket.order_id,
            Order.date_of_order
        ).join(
            UserBasket,
            Order.items
        ).where(
            UserBasket.user_id == user_id
        )
        return session.execute(stmt).all()

    def find_orders_between_dates(start, end):
        stmt = select(
            UserBasket.order_id,
            Order.date_of_order,
            Order.state_id
        ).join(
            UserBasket,
            Order.items
        ).where(
            Order.date_of_order.between(start, end)
        )
        return session.execute(stmt).all()

    def find_user_order_dates_between(user_id, start, end):
        stmt = select(
            UserBasket.order_id,
            Order.date_of_order
        ).join(
            UserBasket,
            Order.items
        ).where(
            UserBasket.user_id == user_id,
            Order.date_of_order.between(start, end)
        )
        return session.execute(stmt).all()

    def clear_items(user_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.order_id == order_id,
            UserBasket.user_id == user_id
        )
        user_basket = session.execute(stmt).scalars().all()
        for basket_entry in user_basket:
            basket_entry.delete()
        session.commit()
        return True

    def remove_item(user_id, menu_item_id, size_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.order_id == order_id,
            UserBasket.menu_item_id == menu_item_id,
            UserBasket.size_id == size_id,
            UserBasket.user_id == user_id
        )
        user_basket = session.execute(stmt).scalars().first()

        if not user_basket:
            logging.error("Cannot remove item. Item not found.")
        else:
            size_stmt = select(Size).where(
                Size.id == size_id
            )
            size_to_add = session.execute(size_stmt).scalars().first()

            if size_to_add.quantity >= 0:
                size_to_add.quantity += 1

            if user_basket.count == 1:
                session.delete(user_basket)
            else:
                user_basket.count -= 1

        session.commit()

        return user_basket

    def add_item(user_id, menu_item_id, size_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.order_id == order_id,
            UserBasket.menu_item_id == menu_item_id,
            UserBasket.size_id == size_id,
            UserBasket.user_id == user_id
        )

        user_basket = session.execute(stmt).scalars().first()

        size_stmt = select(Size).where(
            Size.id == size_id
        )
        size_to_add = session.execute(size_stmt).scalars().first()

        if size_to_add.quantity != 0:
            size_to_add.quantity -= 1
            if not user_basket:
                user_basket = UserBasket(
                    user_id = user_id,
                    menu_item_id = menu_item_id,
                    size_id = size_id,
                    order_id = order_id,
                    count = 1
                )
            else:
                user_basket.count += 1
        else:
            logging.error("Item out of stock error.")
            return None, "Item out of stock error"

        session.add(user_basket)
        session.commit()

        return user_basket, None

    def delete(self):
        session.delete(self)
        session.commit()

    def user_count(order_id):
        stmt = select(UserBasket.user_id).distinct().where(
            UserBasket.order_id == order_id
        )
        return len(session.execute(stmt).all())

    @property
    def serialized(self):
        return {
            "user_id": str(self.user_id),
            "menu_item_id": self.menu_item_id,
            "order_id": self.order_id,
            "count": self.count
        }

    @property
    def basket_format(self):
        return {
            "item_id": self.item.id,
            "size_id": self.size.id,
            "item_name": self.item.name,
            "size_name": self.size.name,
            "price": self.size.price,
            "quantity": self.count,
        }
