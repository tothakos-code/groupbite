from typing import List, Optional

from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .size import Size
from .option_group import option_group_item


class BaseItemSchema(Schema):
    menu_id = fields.Int(required=True)
    vendor_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(allow_none=True, load_default=None)
    category_id = fields.Int(allow_none=True, load_default=None)
    packaging_fee = fields.Int(allow_none=True, load_default=None)
    index = fields.Int(required=True)


class UpdateItemSchema(BaseItemSchema):
    id = fields.Int(required=True)
    menu_id = fields.Int(required=True)


class BulkUpdateItemSchema(Schema):
    items = fields.List(
        fields.Nested(
            {
                "id": fields.Integer(required=True),
                "index": fields.Integer(required=True, validate=validate.Range(min=0)),
            }
        ),
        required=True,
        validate=validate.Length(min=1, max=1000),
    )


class BulkEditItemsSchema(Schema):
    item_ids = fields.List(fields.Integer(), validate=validate.Length(min=1, max=500))
    select_all_menu_id = fields.Integer()
    category_id = fields.Integer(allow_none=True)
    packaging_fee = fields.Integer(allow_none=True)
    description = fields.Str(allow_none=True)

    @validates_schema
    def validate_request(self, data, **kwargs):
        has_ids = 'item_ids' in data
        has_all = 'select_all_menu_id' in data
        if has_ids == has_all:
            raise ValidationError('Provide exactly one of item_ids or select_all_menu_id')
        if not {'category_id', 'packaging_fee', 'description'}.intersection(data):
            raise ValidationError('At least one of category_id, packaging_fee, or description must be provided')


class BulkDeleteItemsSchema(Schema):
    item_ids = fields.List(fields.Integer(), validate=validate.Length(min=1, max=500))
    select_all_menu_id = fields.Integer()

    @validates_schema
    def validate_request(self, data, **kwargs):
        has_ids = 'item_ids' in data
        has_all = 'select_all_menu_id' in data
        if has_ids == has_all:
            raise ValidationError('Provide exactly one of item_ids or select_all_menu_id')


class MenuItem(Base):
    __tablename__ = "menu_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    index: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    packaging_fee: Mapped[Optional[int]] = mapped_column(nullable=True)

    sizes: Mapped[List["Size"]] = relationship(
        back_populates="menu_item",
        cascade="all, delete-orphan",
        order_by="Size.index",
        passive_deletes=True,
    )
    orders: Mapped[List["UserBasket"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    menu: Mapped["Menu"] = relationship(back_populates="items")
    category_obj: Mapped["Category"] = relationship(back_populates="items")
    option_groups: Mapped[List["OptionGroup"]] = relationship(
        secondary=option_group_item,
        back_populates="items",
        order_by="OptionGroup.index",
    )

    @property
    def effective_packaging_fee(self) -> int:
        if self.packaging_fee is not None:
            return self.packaging_fee
        return self.category_obj.default_packaging_fee if self.category_obj else 0

    def __repr__(self):
        return f"MenuItem<{self.id},menu_id={self.menu_id},index={self.index},category_id={self.category_id}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "menu_id": self.menu_id,
            "name": self.name,
            "description": self.description,
            "index": self.index,
            "sizes": [size.serialized for size in self.sizes],
            "category_id": self.category_id,
            "category": self.category_obj.name if self.category_obj else None,
            "packaging_fee": self.packaging_fee,
            "effective_packaging_fee": self.effective_packaging_fee,
            "option_groups": [g.serialized for g in self.option_groups],
        }
