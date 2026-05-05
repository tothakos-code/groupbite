from app.entities.category import Category
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    def get_or_create(db, vendor_id, name: str) -> Category:
        name = (name or "").strip() or "egyéb"
        repo = CategoryRepository(db)
        category = repo.get_by_vendor_and_name(vendor_id, name)
        if not category:
            category = repo.save(Category(vendor_id=vendor_id, name=name))
        return category

    @staticmethod
    def get_all(db, vendor_id) -> list[Category]:
        return CategoryRepository(db).find_by_vendor(vendor_id)

    @staticmethod
    def update(db, category_id: int, name: str) -> Category:
        repo = CategoryRepository(db)
        category = repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        category.name = name.strip()
        db.flush()
        return category

    @staticmethod
    def delete(db, category_id: int):
        repo = CategoryRepository(db)
        category = repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        if category.items:
            raise ValueError("Category still has items, cannot delete")
        repo.delete(category)
