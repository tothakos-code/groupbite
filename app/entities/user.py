import enum
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .order import Order


class Theme(enum.Enum):
    LIGHT = "light"
    DARK = "dark"

    def __str__(self):
        return self.value


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid4
    )
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=True)
    admin: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=False)
    settings: Mapped[dict] = mapped_column(JSONB)
    theme: Mapped[Theme] = mapped_column(default=Theme.LIGHT)
    last_password_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="user")
    placed_orders: Mapped[List["Order"]] = relationship(back_populates="ordered_by")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    favourites: Mapped[List["UserFavourite"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User<id={self.id},username={self.username}>"

    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "theme": str(self.theme),
            "notifications": [
                notification.serialized for notification in self.notifications
            ],
        }
