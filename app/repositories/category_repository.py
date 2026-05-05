from typing import Optional

from sqlalchemy import select

from app.entities.category import Category


class CategoryRepository:
    def __init__(self, db):
        self.db = db

    def find_by_vendor(self, vendor_id) -> list[Category]:
        stmt = select(Category).where(Category.vendor_id == vendor_id).order_by(Category.name)
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        stmt = select(Category).where(Category.id == category_id)
        return self.db.execute(stmt).scalars().first()

    def get_by_vendor_and_name(self, vendor_id, name: str) -> Optional[Category]:
        stmt = select(Category).where(Category.vendor_id == vendor_id, Category.name == name)
        return self.db.execute(stmt).scalars().first()

    def save(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category

    def delete(self, category: Category):
        self.db.delete(category)
        self.db.flush()
        self.db.expunge(category)
