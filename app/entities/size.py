from marshmallow import Schema, fields
from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BaseSizeSchema(Schema):
    menu_item_id = fields.Int(required=True)
    name = fields.Str(required=True)
    link = fields.Str()
    price = fields.Int(required=True)
    quantity = fields.Int(required=True)
    unlimited = fields.Bool(required=True)
    index = fields.Int(required=True)


class UpdateSizeSchema(BaseSizeSchema):
    id = fields.Int(required=True)


class Size(Base):
    __tablename__ = "size"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_item.id", ondelete="CASCADE")
    )
    name: Mapped[str]
    link: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]
    unlimited: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=True)
    index: Mapped[int]

    menu_item: Mapped["MenuItem"] = relationship(back_populates="sizes")
    orders: Mapped["UserBasket"] = relationship(
        back_populates="size",
        foreign_keys="[UserBasket.size_id]",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint("id", "menu_item_id", name="uq_size_item"),)

    def __repr__(self):
        return f"Size<{self.id},menu_item_id={self.menu_item_id},name={self.name},price={self.price}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unlimited": self.unlimited,
            "index": self.index,
        }
