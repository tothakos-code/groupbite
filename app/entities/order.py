import enum
from datetime import date, datetime
from typing import List
from uuid import UUID

from marshmallow import Schema, fields
from sqlalchemy import ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .vendor import Vendor


class BaseOrderSchema(Schema):
    state_id = fields.Str(required=True)
    order_fee = fields.Int(required=True)


class OrderState(enum.Enum):
    COLLECT = "collect"
    ORDER = "order"
    CLOSED = "closed"

    def __str__(self):
        return self.value


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    state_id: Mapped[OrderState] = mapped_column(default=OrderState.COLLECT)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=True)
    date_of_order: Mapped[date]
    order_time: Mapped[datetime] = mapped_column(nullable=True)
    order_fee: Mapped[int] = mapped_column(default=0, nullable=False)
    total_price: Mapped[int] = mapped_column(default=0)

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    __table_args__ = (
        Index("idx_order_date_desc", text("date_of_order DESC")),
        Index("idx_order_vendor_id", "vendor_id"),
        Index("idx_order_state_id", "state_id"),
        Index("idx_order_vendor_date", "vendor_id", text("date_of_order DESC")),
    )

    def __repr__(self):
        return f"Order<id={self.id},order_time={self.order_time},vendor_id={self.vendor_id},state_id={str(self.state_id)},user_id={self.user_id},date_of_order={self.date_of_order},order_time={self.order_time}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "vendor": str(self.vendor.name),
            "state_id": str(self.state_id),
            "user_id": str(self.user_id),
            "user": self.ordered_by.serialized if self.ordered_by else None,
            "date_of_order": self.date_of_order.strftime("%Y-%m-%d"),
            "order_time": self.order_time,
            "order_fee": self.order_fee,
            "total_price": self.total_price,
            "item_count": len(self.items),
        }
