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


    def get_one_by_username(username):
        stmt = select(User).where(
            User.username == username
        )
        return session.execute(stmt).scalars().first()


    def find_all(limit=None, offset=0):
        stmt = select(User)
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return session.execute(stmt).scalars().all()


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

    def is_username_valid(username):
        notvalid_usernames = [
            "null",
            "None",
            None,
            "undefined",
            ""
        ]
        if username in notvalid_usernames:
            return False, "Ez nem lehet a neved: " + username

        notvalid_characters = ["'", '"', "=", ",", ".", "&", "@", "#", "<", ">", "(", ")","[", "]", "{", "}", "%", ";", "*", "`"]
        for char in notvalid_characters:
            if char in username:
                return False, "Tiltott karakter a felhasználónévben: " + char

        if User.get_one_by_username(username):
            return False, "Ez a felhasználónév már foglalt"

        if len(username) > 50:
            return False, "Felhasználónév túl hosszú, válassz rövidebbet"

        return True, ""


    def is_email_valid(email):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Helytelen email formátum"

        if User.get_one_by_email(email):
            return False, "Ez az email cím már foglalt"

        return True, ""


    def create_user(user):
        if session.query(User).filter(User.username == user.username).first():
            logging.error(f"Error in user creation. User '{user.username}' already exist.")
            return None
        session.add(user)

        try:
            session.commit()
            session.refresh(user)
            return True, user
        except exc.DataError as e:
            logging.exception("DataError during user add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None


    def update_user(self, user):
        self.username = user["username"]
        try:
            session.commit()
            session.refresh(self)
            return True, user
        except exc.DataError as e:
            logging.exception("DataError during user update")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None
        return self


    def get_all_orders(self):
        return self.orders


    def get_all_orders_between(self, start, end):
        stmt = select(User).where(
            User.id == self.id,
            User.orders.any(Order.date_of_order.between(start, end))
        )
        return session.execute(stmt).all()


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
