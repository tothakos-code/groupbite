from sqlalchemy import Column, Text, Enum, select, exc, or_, String, cast
from uuid import UUID
from . import Base, session
from .order import Order
from .menu_item import MenuItem
from .vendor import Vendor
from .size import Size
import enum
from sqlalchemy import ForeignKey, ForeignKeyConstraint
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
    size: Mapped["Size"] = relationship(back_populates="orders", foreign_keys=[size_id])

    __table_args__ = (
        ForeignKeyConstraint(['size_id', 'menu_item_id'], ['size.id', 'size.menu_item_id'], name='fk_size_item'),
    )

    def __repr__(self):
        return f"UserBasket<user_id={self.user_id},menu_item_id={self.menu_item_id},order_id={self.order_id},count={self.count}>"

    def find_items_by_order(order_id):
        stmt = select(UserBasket).where(UserBasket.order_id == order_id)
        return session.execute(stmt).scalars().all()

    def find_user_orders(user_id, limit=None, offset=0, search=None, vendor_id=None, date_from=None, date_to=None):
        from .order_item import OrderItem
        subq = (
            select(Order.id, Order.date_of_order)
            .join(Order.order_items)
            .where(UserBasket.user_id == user_id)
        )

        if search is not None:
            subq = subq.where(
                or_(
                    OrderItem.item_name.ilike(f"%{search}%"),
                    OrderItem.size_label.ilike(f"%{search}%"),
                    cast(Order.state_id, String).ilike(f"%{search}%"),
                )
            )

        if vendor_id is not None:
            subq = subq.where(Order.vendor_id == vendor_id)

        if date_from is not None and date_to is not None:
            subq = subq.where(Order.date_of_order.between(date_from, date_to))

        # Add ordering + limit/offset to control pagination at ORDER level
        subq = subq.order_by(Order.date_of_order.desc()).limit(limit).offset(offset)
        subq = subq.distinct().subquery()

        # Outer query: get all UserBasket rows in those orders for this user
        stmt = (
            select(OrderItem)
            .join(OrderItem.order)
            .where(
                OrderItem.user_id == user_id,
                OrderItem.order_id.in_(select(subq.c.id))
            )
            .order_by(Order.date_of_order.desc())
        )

        return session.execute(stmt).scalars().all()

    def find_user_order_vendors(user_id):
        stmt = (
            select(Vendor)
            .join(Order.order_items)
            .join(Order.vendor)
            .where(UserBasket.user_id == user_id)
            .distinct()
        )
        return session.execute(stmt).scalars().all()


    def find_user_basket(user_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.user_id == user_id,
            UserBasket.order_id == order_id
        )
        return session.execute(stmt).scalars().all()

    def clear_items(user_id, order_id):
        stmt = select(UserBasket).where(
            UserBasket.order_id == order_id,
            UserBasket.user_id == user_id
        )
        user_baskets = session.execute(stmt).scalars().all()
        for basket_entry in user_baskets:
            basket_entry.delete()
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during removing user_basket")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

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
            return False, None
        else:
            size_stmt = select(Size).where(
                Size.id == size_id
            )
            size_to_remove = session.execute(size_stmt).scalars().first()

            if not size_to_remove.unlimited:
                size_to_remove.quantity += 1

            if user_basket.count == 1:
                session.delete(user_basket)
            else:
                user_basket.count -= 1

        try:
            session.commit()
            return True, None
        except exc.DataError as e:
            logging.exception("DataError during removing user_basket")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None


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

        if size_to_add.unlimited or size_to_add.quantity > 0:
            if not size_to_add.unlimited:
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
            # TODO: raise Item out of stock error?
            return False, None

        session.add(user_basket)
        try:
            session.commit()
            session.refresh(user_basket)
            return True, user_basket
        except exc.DataError as e:
            logging.exception("DataError during removing user_basket")
            session.rollback()
            return False, None
        except exc.IntegrityError as e:
            logging.exception("IntegrityError during item add to basket")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None


    def delete(self):
        if not self.size.unlimited:
            self.size.quantity += self.count
        session.delete(self)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during removing user_basket")
            session.rollback()
            return False

        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def user_count(order_id):
        stmt = select(UserBasket.user_id).distinct().where(
            UserBasket.order_id == order_id
        )
        return len(session.execute(stmt).all())

    @property
    def serialized(self):
        return {
            "user_id": self.user_id,
            "item_id": self.menu_item_id,
            "size_id": self.size_id,
            "order_id": self.order_id,
            "item_name": self.item.name,
            "size_name": self.size.name,
            "price": self.size.price,
            "category": self.item.category,
            "quantity": self.count,
        }

    @property
    def basket_format(self):
        return {
            "item_id": self.item.id,
            "size_id": self.size.id,
            "item_name": self.item.name,
            "size_name": self.size.name,
            "price": self.size.price,
            "category": self.item.category,
            "quantity": self.count,
        }
