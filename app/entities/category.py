from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    name: Mapped[str]
    default_packaging_fee: Mapped[int] = mapped_column(default=0)

    items: Mapped[List["MenuItem"]] = relationship(back_populates="category_obj")

    __table_args__ = (UniqueConstraint("vendor_id", "name", name="uq_category_vendor_name"),)

    @property
    def serialized(self):
        return {"id": self.id, "vendor_id": str(self.vendor_id), "name": self.name, "default_packaging_fee": self.default_packaging_fee}
