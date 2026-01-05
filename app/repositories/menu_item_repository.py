from typing import Optional

from sqlalchemy import select

from app.entities.menu_item import MenuItem


class MenuItemRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, menu_item_id) -> Optional[MenuItem]:
        stmt = select(MenuItem).where(MenuItem.id == menu_item_id)
        return self.db.execute(stmt).scalars().first()
