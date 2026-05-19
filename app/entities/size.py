from typing import List

from marshmallow import Schema, fields, validate, validates_schema, ValidationError
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


class BulkUpdateSizeSchema(Schema):
    sizes = fields.List(
        fields.Nested(
            {
                "id": fields.Integer(required=True),
                "name": fields.Str(required=True),
                "price": fields.Int(required=True),
                "quantity": fields.Int(required=True),
                "unlimited": fields.Bool(required=True),
            }
        ),
        required=True,
        validate=validate.Length(min=1, max=5000),
    )


class BulkSizePriceByItemsSchema(Schema):
    item_ids = fields.List(fields.Integer(), validate=validate.Length(min=1, max=500))
    select_all_menu_id = fields.Integer()
    mode = fields.Str(required=True, validate=validate.OneOf(['set', 'adjust_fixed', 'adjust_percent']))
    value = fields.Integer(required=True)

    @validates_schema
    def validate_request(self, data, **kwargs):
        has_ids = 'item_ids' in data
        has_all = 'select_all_menu_id' in data
        if has_ids == has_all:
            raise ValidationError('Provide exactly one of item_ids or select_all_menu_id')


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
    orders: Mapped[List["UserBasket"]] = relationship(
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
