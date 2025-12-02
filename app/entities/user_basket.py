from sqlalchemy import Column, Text, Enum, select, exc, or_, String, cast, func
from uuid import UUID
from . import Base, session
from .order import Order
from .menu_item import MenuItem
from .vendor import Vendor
from .size import Size
import enum
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index
from sqlalchemy.orm import selectinload
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
        Index('idx_userbasket_user_id', 'user_id'),
        Index('idx_userbasket_order_id', 'order_id'),
        Index('idx_userbasket_user_order', 'user_id', 'order_id'),
    )

    def __repr__(self):
        return f"UserBasket<user_id={self.user_id},menu_item_id={self.menu_item_id},order_id={self.order_id},count={self.count}>"
    # TODO: move to userbasket Repo
    def find_items_by_order(order_id):
        stmt = select(UserBasket).where(UserBasket.order_id == order_id)
        return session.execute(stmt).scalars().all()

    # TODO: Move to Orderitem repo
    @staticmethod
    def find_user_orders(user_id, limit=None, offset=0, search=None, vendor_id=None, date_from=None, date_to=None):
        from .order_item import OrderItem


        stmt = (
            select(OrderItem)
            .options(
                selectinload(OrderItem.order).selectinload(Order.vendor),
                selectinload(OrderItem.order)
            )
            .join(OrderItem.order)
            .where(OrderItem.user_id == user_id)
        )

        if search is not None:
            stmt = stmt.where(
                or_(
                    OrderItem.item_name.ilike(f"%{search}%"),
                    OrderItem.size_label.ilike(f"%{search}%"),
                    cast(Order.state_id, String).ilike(f"%{search}%"),
                )
            )

        if vendor_id is not None:
            stmt = stmt.where(Order.vendor_id == vendor_id)

        if date_from is not None and date_to is not None:
            stmt = stmt.where(Order.date_of_order.between(date_from, date_to))

        stmt = stmt.order_by(Order.date_of_order.desc())

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)

        return session.execute(stmt).scalars().all()
    # TODO: Move to Vendor repo
    def find_user_order_vendors(user_id):
        user_vendor_ids_subquery = (
            select(Order.vendor_id)
            .join(UserBasket, UserBasket.order_id == Order.id)
            .where(UserBasket.user_id == user_id)
            .distinct()
            .subquery()
        )

        stmt = (
            select(Vendor)
            .where(Vendor.id.in_(select(user_vendor_ids_subquery.c.vendor_id)))
            .order_by(Vendor.name)
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
