from uuid import UUID

from sqlalchemy import select

from app.entities.order import Order
from app.entities.user import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_username(self, username):
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalars().first()

    def find_all(self, limit=None, offset=0):
        stmt = select(User)
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def get_by_email(self, email):
        stmt = select(User).where(User.email == email)
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
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalars().first().admin

    def save(self, user: User):
        self.db.add(user)

    def get_all_orders_between(self, user_id, start, end):
        stmt = select(User).where(
            User.id == user_id, User.orders.any(Order.date_of_order.between(start, end))
        )
        return self.db.execute(stmt).all()
