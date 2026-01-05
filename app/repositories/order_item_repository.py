from sqlalchemy import delete

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
