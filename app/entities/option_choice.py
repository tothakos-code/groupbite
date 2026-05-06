from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class OptionChoice(Base):
    __tablename__ = "option_choice"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    option_group_id: Mapped[int] = mapped_column(ForeignKey("option_group.id", ondelete="CASCADE"))
    name: Mapped[str]
    price_delta: Mapped[int] = mapped_column(default=0)
    index: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    group: Mapped["OptionGroup"] = relationship(back_populates="choices")

    def __repr__(self):
        return f"OptionChoice<{self.id},group_id={self.option_group_id},name={self.name}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "option_group_id": self.option_group_id,
            "name": self.name,
            "price_delta": self.price_delta,
            "index": self.index,
            "active": self.active,
        }
