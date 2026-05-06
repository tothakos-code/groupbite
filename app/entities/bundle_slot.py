from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BundleSlot(Base):
    __tablename__ = "bundle_slot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bundle_discount_id: Mapped[int] = mapped_column(ForeignKey("bundle_discount.id", ondelete="CASCADE"))
    slot_index: Mapped[int]
    match_type: Mapped[str]
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    menu_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("menu_item.id", ondelete="SET NULL"), nullable=True
    )
    price_override: Mapped[Optional[int]] = mapped_column(nullable=True)
    price_delta: Mapped[Optional[int]] = mapped_column(nullable=True)

    bundle: Mapped["BundleDiscount"] = relationship(back_populates="slots")
    category: Mapped[Optional["Category"]] = relationship()
    item: Mapped[Optional["MenuItem"]] = relationship()

    def __repr__(self):
        return f"BundleSlot<{self.id},bundle={self.bundle_discount_id},slot_index={self.slot_index}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "bundle_discount_id": self.bundle_discount_id,
            "slot_index": self.slot_index,
            "match_type": self.match_type,
            "category_id": self.category_id,
            "menu_item_id": self.menu_item_id,
            "price_override": self.price_override,
            "price_delta": self.price_delta,
        }
