from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    menu_item_id: Mapped[int] = mapped_column()
    size_id: Mapped[int] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    count: Mapped[int]

    # Snapshotted data
    item_name: Mapped[str]
    size_label: Mapped[str]
    unit_price: Mapped[int]
    total_price: Mapped[int]

    # Relationships (optional)
    order: Mapped["Order"] = relationship(back_populates="order_items")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        Index("idx_orderitem_user_id", "user_id"),
        Index("idx_orderitem_order_id", "order_id"),
        Index("idx_orderitem_user_order", "user_id", "order_id"),
        Index(
            "idx_orderitem_item_name_gin",
            "item_name",
            postgresql_using="gin",
            postgresql_ops={"item_name": "gin_trgm_ops"},
        ),
        Index(
            "idx_orderitem_size_label_gin",
            "size_label",
            postgresql_using="gin",
            postgresql_ops={"size_label": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"OrderItem<{self.id},order_id={self.order_id},user_id={self.user_id},item_name={self.item_name}>"
