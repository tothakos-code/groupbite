import logging
import re
from sqlalchemy import  exc
from sqlalchemy import select
from uuid import UUID
from app.entities.order import Order
from app.entities.user import User


class UserRepository:

    def __init__(self, db):
        self.db = db

    def get_by_username(self, username):
        stmt = select(User).where(
            User.username == username
        )
        return self.db.execute(stmt).scalars().first()

    def find_all(self, limit=None, offset=0):
        stmt = select(User)
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def get_by_email(self, email):
        stmt = select(User).where(
            User.email == email
        )
        return self.db.execute(stmt).scalars().first()

    def get_by_id(self, user_id):
        # check if uuid is valid
        if not type(user_id) == UUID:
            try:
                UUID(user_id)
            except ValueError:
                return None
        else:
            user_id = str(user_id)
        return self.db.query(User).filter(User.id == user_id).first()

    def is_admin(self, user_id):
        stmt = select(User).where(
            User.id == user_id
        )
        return self.db.execute(stmt).scalars().first().admin

    def is_email_valid(self, email):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Helytelen email formátum"

        if self.db.get_one_by_email(email):
            return False, "Ez az email cím már foglalt"

        return True, ""

    def create_user(self, user):
        if self.db.query(User).filter(User.username == user.username).first():
            logging.error(f"Error in user creation. User '{user.username}' already exist.")
            return None
        self.db.add(user)

        try:
            self.db.commit()
            self.db.refresh(user)
            return True, user
        except exc.DataError:
            logging.exception("DataError during user add")
            self.db.rollback()
            return False, None
        except Exception:
            logging.exception("Unhandled exception happened, rolling back")
            self.db.rollback()
            return False, None

    def save(self, user: User):
        self.db.add(user)

    def get_all_orders_between(self, user_id, start, end):
        stmt = select(User).where(
            User.id == user_id,
            User.orders.any(Order.date_of_order.between(start, end))
        )
        return self.db.execute(stmt).all()
