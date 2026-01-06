import enum
from datetime import date as d
from typing import List
from uuid import UUID

from marshmallow import Schema, fields
from sqlalchemy import Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Frequency(enum.Enum):
    FIX = "fix"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    def __str__(self):
        return self.value


class BaseMenuSchema(Schema):
    name = fields.Str(required=True)
    vendor_id = fields.UUID(required=True)
    items = fields.List(fields.Dict())


class UpdateMenuSchema(BaseMenuSchema):
    id = fields.Int(required=True)
    active = fields.Bool(required=True)
    from_date = fields.Date(allow_none=True)
    to_date = fields.Date(allow_none=True)


class Menu(Base):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    from_date: Mapped[d] = mapped_column(
        insert_default=func.current_date(), nullable=True
    )
    to_date: Mapped[d] = mapped_column(
        insert_default=func.current_date(), nullable=True
    )
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))

    items: Mapped[List["MenuItem"]] = relationship(
        back_populates="menu", cascade="all, delete", order_by="MenuItem.index"
    )

    def __repr__(self):
        return f"Menu<{self.id},name={self.name},from_date={self.from_date},to_date={self.to_date},vendor_id={self.vendor_id}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "name": self.name,
            "from_date": str(self.from_date if self.from_date else ""),
            "to_date": str(self.to_date if self.to_date else ""),
            "vendor_id": str(self.vendor_id),
            "active": self.active,
            "items": [item.serialized for item in self.items],
        }
