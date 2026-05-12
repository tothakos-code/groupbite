from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


option_group_item = Table(
    "option_group_item",
    Base.metadata,
    Column("option_group_id", Integer, ForeignKey("option_group.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_item_id", Integer, ForeignKey("menu_item.id", ondelete="CASCADE"), primary_key=True),
    Column("index", Integer, nullable=False, default=0),
)


class OptionGroup(Base):
    __tablename__ = "option_group"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id", ondelete="CASCADE"))
    name: Mapped[str]
    min_choices: Mapped[int] = mapped_column(default=0)
    max_choices: Mapped[int] = mapped_column(default=1)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    index: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    choices: Mapped[List["OptionChoice"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="OptionChoice.index",
        passive_deletes=True,
    )
    items: Mapped[List["MenuItem"]] = relationship(
        secondary=option_group_item,
        back_populates="option_groups",
    )

    def __repr__(self):
        return f"OptionGroup<{self.id},vendor_id={self.vendor_id},name={self.name}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "name": self.name,
            "min_choices": self.min_choices,
            "max_choices": self.max_choices,
            "required": self.required,
            "index": self.index,
            "choices": [c.serialized for c in self.choices if c.active],
        }
