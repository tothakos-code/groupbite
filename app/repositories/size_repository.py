from sqlalchemy import select

from app.entities.size import Size


class SizeRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, size_id):
        return self.db.get(Size, size_id)

    def increment_quantity(self, size):
        size.quantity += 1
        self.db.flush()

    def decrement_quantity(self, size):
        size.quantity -= 1
        self.db.flush()

    def save(self, size: Size) -> Size:
        self.db.add(size)
        self.db.flush()
        return size

    def delete(self, size: Size) -> None:
        self.db.delete(size)
        self.db.flush()
        self.db.expunge(size)

    def update(self, size, name, price, quantity, unlimited, index):
        size.name = name
        size.price = price
        size.quantity = quantity
        size.unlimited = unlimited
        size.index = index
        self.db.flush()
        return size

    def find_all_by_menu_item(self, menu_item_id, desc=False):
        stmt = select(Size).where(Size.menu_item_id == menu_item_id)
        if desc:
            stmt = stmt.order_by(Size.index.desc())
        else:
            stmt = stmt.order_by(Size.index)

        return self.db.execute(stmt).scalars().all()
