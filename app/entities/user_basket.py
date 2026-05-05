from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entities.user import User

from . import Base
from .menu_item import MenuItem
from .order import Order
from .size import Size


class UserBasket(Base):
    __tablename__ = "user_basket"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_item.id", ondelete="CASCADE"), primary_key=True
    )
    size_id: Mapped[int] = mapped_column(
        ForeignKey("size.id", ondelete="CASCADE"), primary_key=True
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), primary_key=True)
    count: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="items")
    user: Mapped["User"] = relationship(back_populates="orders")
    item: Mapped["MenuItem"] = relationship(back_populates="orders")
    size: Mapped["Size"] = relationship(back_populates="orders", foreign_keys=[size_id])

    __table_args__ = (
        ForeignKeyConstraint(
            ["size_id", "menu_item_id"],
            ["size.id", "size.menu_item_id"],
            name="fk_size_item",
            ondelete="CASCADE",
        ),
        Index("idx_userbasket_user_id", "user_id"),
        Index("idx_userbasket_order_id", "order_id"),
        Index("idx_userbasket_user_order", "user_id", "order_id"),
    )

    def __repr__(self):
        return f"UserBasket<user_id={self.user_id},menu_item_id={self.menu_item_id},order_id={self.order_id},count={self.count}>"

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
            "category_id": self.item.category_id,
            "category": self.item.category_obj.name if self.item.category_obj else None,
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
            "category_id": self.item.category_id,
            "category": self.item.category_obj.name if self.item.category_obj else None,
            "quantity": self.count,
        }
