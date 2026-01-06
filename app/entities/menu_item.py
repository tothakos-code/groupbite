from typing import List

from marshmallow import Schema, fields, validate
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .size import Size


class BaseItemSchema(Schema):
    menu_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True)
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


class MenuItem(Base):
    __tablename__ = "menu_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    index: Mapped[int]
    category: Mapped[str]

    sizes: Mapped[List["Size"]] = relationship(
        back_populates="menu_item",
        cascade="all, delete-orphan",
        order_by="Size.index",
        passive_deletes=True,
    )
    orders: Mapped[List["UserBasket"]] = relationship(back_populates="item")
    menu: Mapped["Menu"] = relationship(back_populates="items")

    def __repr__(self):
        return f"MenuItem<{self.id},menu_id={self.menu_id},index={self.index},category={self.category}>"

    @property
    def serialized(self):
        return {
            "id": self.id,
            "menu_id": self.menu_id,
            "name": self.name,
            "description": self.description,
            "index": self.index,
            "sizes": [size.serialized for size in self.sizes],
            "category": self.category,
        }
