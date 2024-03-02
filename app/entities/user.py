from sqlalchemy import Column, Text, Enum
from uuid import UUID, uuid4
from . import Base, session
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

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid4)
    username: Mapped[str] = mapped_column(Text, unique=True)
    theme: Mapped[Theme] = mapped_column(default=Theme.LIGHT)

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="user")
    placed_orders: Mapped[List["Order"]] = relationship(back_populates="ordered_by")

    def __repr__(self):
        return "Menu"

    def get_one_user(username):
        return session.query(User).filter(User.username == username).first()

    def create_user(user):
        if session.query(User).filter(User.username == user.username).first():
            logging.error(f"Error in user creation. User '{user.username}' already exist.")
            return None
        session.add(user)
        session.commit()
        session.close()
        return user

    @property
    def serialized(self):
        return {
            'id': self.id,
            'username': self.username,
            'theme': str(self.theme)
        }

# class UserSchema(Schema):
#     id = fields.UUID()
#     username = fields.String()
#     theme = fields.Enum(Theme)
