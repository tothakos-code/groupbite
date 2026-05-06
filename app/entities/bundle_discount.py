from typing import List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BundleDiscount(Base):
    __tablename__ = "bundle_discount"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id", ondelete="CASCADE"))
    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    slots: Mapped[List["BundleSlot"]] = relationship(
        back_populates="bundle",
        cascade="all, delete-orphan",
        order_by="BundleSlot.slot_index",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"BundleDiscount<{self.id},vendor_id={self.vendor_id},name={self.name}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "name": self.name,
            "description": self.description,
            "slots": [s.serialized for s in self.slots],
        }
