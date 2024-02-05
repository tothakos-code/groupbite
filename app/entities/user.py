from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base
from typing import List
from marshmallow import Schema, fields
import enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Theme(enum.Enum):
    LIGHT = 'light'
    DARK = 'dark'

    def __str__(self):
        return self.value

class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(Text, unique=True)
    theme: Mapped[Theme] = mapped_column(default=Theme.LIGHT)

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="user")
    placed_orders: Mapped[List["Order"]] = relationship(back_populates="ordered_by")

    def __repr__():
        return "Menu"

    @property
    def serialized(self):
        return {
            'id': self.id,
            'username': self.username,
            'theme': self.theme
        }

# class UserSchema(Schema):
#     id = fields.UUID()
#     username = fields.String()
#     theme = fields.Enum(Theme)
