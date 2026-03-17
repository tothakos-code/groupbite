from sqlalchemy import String, cast, delete, func, or_, select
from sqlalchemy.orm import joinedload, selectinload

from app.entities.order import Order
from app.entities.order_item import OrderItem
from app.entities.user_basket import UserBasket


class UserBasketRepository:
    def __init__(self, db):
        self.db = db

    def get_by_order(self, order_id):
        stmt = select(UserBasket).where(UserBasket.order_id == order_id)
        return self.db.execute(stmt).scalars().all()

    def find_basket_item(self, order_id, user_id, menu_item_id, size_id):
        stmt = select(UserBasket).where(
            UserBasket.order_id == order_id,
            UserBasket.user_id == user_id,
            UserBasket.menu_item_id == menu_item_id,
            UserBasket.size_id == size_id,
        )
        return self.db.execute(stmt).scalars().first()

    def delete(self, basket_item):
        self.db.delete(basket_item)
        self.db.flush()
        self.db.expunge(basket_item)

    def add(self, basket_item):
        self.db.add(basket_item)
        self.db.flush()
        return basket_item

    def decrement_count(self, basket_item):
        basket_item.count -= 1
        self.db.flush()

    def increment_count(self, basket_item):
        basket_item.count += 1
        self.db.flush()

    def find_user_orders(
        self,
        user_id,
        limit=None,
        offset=0,
        search=None,
        vendor_id=None,
        date_from=None,
        date_to=None,
    ):
        stmt = (
            select(OrderItem)
            .options(
                selectinload(OrderItem.order).selectinload(Order.vendor),
                selectinload(OrderItem.order),
            )
            .join(OrderItem.order)
            .where(OrderItem.user_id == user_id)
        )

        if search is not None:
            stmt = stmt.where(
                or_(
                    OrderItem.item_name.ilike(f"%{search}%"),
                    OrderItem.size_label.ilike(f"%{search}%"),
                    cast(Order.state_id, String).ilike(f"%{search}%"),
                )
            )

        if vendor_id is not None:
            stmt = stmt.where(Order.vendor_id == vendor_id)

        if date_from is not None and date_to is not None:
            stmt = stmt.where(Order.date_of_order.between(date_from, date_to))

        stmt = stmt.order_by(Order.date_of_order.desc())

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)

        return self.db.execute(stmt).scalars().all()

    def find_user_basket(self, order_id, user_id):
        stmt = select(UserBasket).where(
            UserBasket.user_id == user_id, UserBasket.order_id == order_id
        )
        return self.db.execute(stmt).scalars().all()

    def user_count(self, order_id):
        stmt = select(func.count(func.distinct(UserBasket.user_id))).where(
            UserBasket.order_id == order_id
        )
        return self.db.execute(stmt).scalar()

    def get_user_counts_batch(self, order_ids):
        stmt = (
            select(
                UserBasket.order_id,
                func.count(func.distinct(UserBasket.user_id)).label("user_count"),
            )
            .where(UserBasket.order_id.in_(order_ids))
            .group_by(UserBasket.order_id)
        )
        return self.db.execute(stmt).all()

    def find_items_by_order(self, order_id):
        stmt = (
            select(UserBasket)
            .options(joinedload(UserBasket.item), joinedload(UserBasket.size))
            .where(UserBasket.order_id == order_id)
        )
        return self.db.execute(stmt).scalars().all()

    def clear_items(self, user_id, order_id):
        stmt = delete(UserBasket).where(
            UserBasket.order_id == order_id, UserBasket.user_id == user_id
        )
        self.db.execute(stmt).scalars().all()

    def clear_order_items(self, order_id):
        stmt = delete(UserBasket).where(UserBasket.order_id == order_id)
        self.db.execute(stmt)
        self.db.expire_all()
