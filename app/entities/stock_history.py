import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base


class StockChangeReason(enum.Enum):
    ORDER = "order"
    TOPUP = "topup"
    ADJUSTMENT = "adjustment"


class StockHistory(Base):
    __tablename__ = "stock_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    size_id: Mapped[int] = mapped_column(ForeignKey("size.id", ondelete="CASCADE"))
    quantity_change: Mapped[int]
    reason: Mapped[StockChangeReason]
    performed_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("user.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    note: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    size: Mapped["Size"] = relationship()
    user: Mapped[Optional["User"]] = relationship()

    __table_args__ = (
        Index("idx_stockhistory_size_id", "size_id"),
        Index("idx_stockhistory_timestamp", "timestamp"),
    )

    @property
    def serialized(self):
        return {
            "id": self.id,
            "size_id": self.size_id,
            "quantity_change": self.quantity_change,
            "reason": self.reason.value,
            "performed_by": str(self.performed_by) if self.performed_by else None,
            "timestamp": self.timestamp.isoformat(),
            "note": self.note,
        }
