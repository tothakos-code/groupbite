from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BasketOptionSelection(Base):
    __tablename__ = "basket_option_selection"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"))
    menu_item_id: Mapped[int] = mapped_column()
    size_id: Mapped[int] = mapped_column()
    option_choice_id: Mapped[int] = mapped_column(ForeignKey("option_choice.id", ondelete="CASCADE"))

    choice: Mapped["OptionChoice"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "user_id", "order_id", "menu_item_id", "size_id", "option_choice_id",
            name="uq_basket_option_selection",
        ),
    )

    def __repr__(self):
        return (
            f"BasketOptionSelection<user={self.user_id},order={self.order_id},"
            f"item={self.menu_item_id},choice={self.option_choice_id}>"
        )
