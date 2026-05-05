import enum
from datetime import date, datetime, time
from typing import List, Optional
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
    open_from: Mapped[date]
    open_until: Mapped[Optional[date]] = mapped_column(nullable=True)
    close_time: Mapped[Optional[time]] = mapped_column(nullable=True)
    order_time: Mapped[datetime] = mapped_column(nullable=True)
    order_fee: Mapped[int] = mapped_column(default=0, nullable=False)
    total_price: Mapped[int] = mapped_column(default=0)

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    __table_args__ = (
        Index("idx_order_date_desc", text("open_from DESC")),
        Index("idx_order_vendor_id", "vendor_id"),
        Index("idx_order_state_id", "state_id"),
        Index("idx_order_vendor_date", "vendor_id", text("open_from DESC")),
    )

    @property
    def effective_until(self) -> date:
        return self.open_until or self.open_from

    def __repr__(self):
        return f"Order<id={self.id},vendor_id={self.vendor_id},state_id={str(self.state_id)},user_id={self.user_id},open_from={self.open_from},open_until={self.open_until},order_time={self.order_time}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "vendor": str(self.vendor.name),
            "state_id": str(self.state_id),
            "user_id": str(self.user_id),
            "user": self.ordered_by.serialized if self.ordered_by else None,
            "date_of_order": self.open_from.strftime("%Y-%m-%d"),
            "open_from": self.open_from.strftime("%Y-%m-%d"),
            "open_until": self.effective_until.strftime("%Y-%m-%d"),
            "close_time": self.close_time.strftime("%H:%M") if self.close_time else None,
            "order_time": self.order_time,
            "order_fee": self.order_fee,
            "total_price": self.total_price,
            "item_count": len(self.items),
        }
