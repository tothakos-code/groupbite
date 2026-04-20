from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class UserFavourite(Base):
    __tablename__ = "user_favourite"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    item_name: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="favourites")

    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "vendor_id": str(self.vendor_id),
            "item_name": self.item_name,
        }
