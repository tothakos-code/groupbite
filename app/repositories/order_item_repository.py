from sqlalchemy import String, cast, delete, or_, select
from sqlalchemy.orm import selectinload

from app.entities.order import Order
from app.entities.order_item import OrderItem


class OrderItemRepository:
    def __init__(self, db) -> None:
        self.db = db

    def save(self, order_item: OrderItem):
        self.db.add(order_item)
        self.db.flush()
        return order_item

    def delete_order_items(self, order):
        stmt = delete(OrderItem).where(OrderItem.order_id == order.id)

        self.db.execute(stmt)

    def find_user_order_items(
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
