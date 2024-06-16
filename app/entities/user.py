from sqlalchemy import Column, Text, Enum, select
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from . import Base, session
from .order import Order
from typing import List
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
    settings: Mapped[dict] = mapped_column(JSONB)
    theme: Mapped[Theme] = mapped_column(default=Theme.LIGHT)

    orders: Mapped[List["UserBasket"]] = relationship(back_populates="user")
    placed_orders: Mapped[List["Order"]] = relationship(back_populates="ordered_by")

    def __repr__(self):
        return f"User<id={self.id},username={self.username}>"

    def get_one_by_username(username):
        return session.query(User).filter(User.username == username).first()

    def get_one_by_id(id):
        return session.query(User).filter(User.id == id).first()

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

        notvalid_characters = ["'", '"', "=", ",", ".", "&", "@", "#", "<", ">", "(", ")","[", "]", "{", "}"]
        for char in notvalid_characters:
            if char in username:
                return False, "Tiltott karakter a felhasználónévben: " + char

        if User.get_one_by_username(username):
            return False, "Ez a felhasználónév már foglalt"

        return True, ""

    def create_user(user):
        if session.query(User).filter(User.username == user.username).first():
            logging.error(f"Error in user creation. User '{user.username}' already exist.")
            return None
        session.add(user)
        session.commit()
        session.close()
        return user

    def update_user(self, user):
        self.username = user['username']
        session.commit()
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
            'id': self.id,
            'username': self.username,
            'theme': str(self.theme)
        }
