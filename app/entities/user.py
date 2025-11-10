from sqlalchemy import Column, Text, Enum, select, exc, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from . import Base, session
from .order import Order
from typing import List
import enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import logging
import re

class Theme(enum.Enum):
    LIGHT = "light"
    DARK = "dark"

    def __str__(self):
        return self.value

class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid4)
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=True)
    admin: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=False)
    settings: Mapped[dict] = mapped_column(JSONB)
    theme: Mapped[Theme] = mapped_column(default=Theme.LIGHT)

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="user")
    placed_orders: Mapped[List["Order"]] = relationship(back_populates="ordered_by")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User<id={self.id},username={self.username}>"


    def get_one_by_email(email):
        stmt = select(User).where(
            User.email == email
        )
        return session.execute(stmt).scalars().first()


    def get_one_by_id(id):
        # check if uuid is valid
        if not type(id) == UUID:
            try:
                UUID(id)
            except ValueError as e:
                return None
        else:
            id  = str(id)
        return session.query(User).filter(User.id == id).first()

    def is_admin(user_id):
        stmt = select(User).where(
            User.id == user_id
        )
        return session.execute(stmt).scalars().first().admin

    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "theme": str(self.theme),
            "notifications": [notification.serialized for notification in self.notifications]
        }
