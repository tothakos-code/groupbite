from typing import Optional

from sqlalchemy import delete, func, or_, select, update

from app.entities.category import Category
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem


class MenuItemRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, menu_item_id) -> Optional[MenuItem]:
        stmt = select(MenuItem).where(MenuItem.id == menu_item_id)
        return self.db.execute(stmt).scalars().first()

    def find_all_by_menu(self, menu_id, search=None, limit=10, offset=0, desc=False):
        stmt = select(MenuItem).where(MenuItem.menu_id == menu_id)

        if search:
            ilike_expr = f"%{search}%"
            stmt = stmt.join(MenuItem.category_obj).where(
                or_(
                    Category.name.ilike(ilike_expr),
                    MenuItem.name.ilike(ilike_expr),
                    MenuItem.description.ilike(ilike_expr),
                )
            )

        stmt = stmt.order_by(MenuItem.index.desc() if desc else MenuItem.index)

        if limit:
            stmt = stmt.limit(limit).offset(offset)

        return self.db.execute(stmt).scalars().all()

    def get_by_ids(self, ids: list[int]):
        if not ids:
            return []

        stmt = select(MenuItem).where(MenuItem.id.in_(ids))
        return self.db.execute(stmt).scalars().all()

    def count_unique_menu_ids_by_item_ids(self, ids: list[int]):
        if not ids:
            return 0

        stmt = select(func.count(func.distinct(MenuItem.menu_id))).where(
            MenuItem.id.in_(ids)
        )
        return self.db.execute(stmt).scalar_one()

    def count_by_menu_id(self, menu_id, search=None):
        stmt = select(func.count(MenuItem.id)).where(MenuItem.menu_id == menu_id)

        if search:
            ilike_expr = f"%{search}%"
            stmt = stmt.join(MenuItem.category_obj).where(
                or_(
                    Category.name.ilike(ilike_expr),
                    MenuItem.name.ilike(ilike_expr),
                    MenuItem.description.ilike(ilike_expr),
                )
            )

        return self.db.execute(stmt).scalar_one()

    def find_all_by_menu_list(
        self, menu_id_list, category_filter=None, limit=None, desc=False
    ):
        if category_filter is None:
            category_filter = []

        stmt = select(MenuItem).join(MenuItem.category_obj).where(MenuItem.menu_id.in_(menu_id_list))

        if category_filter and len(category_filter) > 0:
            stmt = stmt.where(Category.name.in_(category_filter))

        if desc:
            stmt = stmt.order_by(Category.name.desc(), MenuItem.index.desc())
        else:
            stmt = stmt.order_by(Category.name.asc(), MenuItem.index.asc())

        if limit:
            stmt = stmt.limit(limit)

        return self.db.execute(stmt).scalars().all()

    def save(self, menu_item):
        self.db.add(menu_item)
        self.db.flush()
        return menu_item

    def update(self, menu_item, menu_id, name, description, index, category_id, packaging_fee=None):
        menu_item.name = name
        menu_item.menu_id = menu_id
        menu_item.description = description
        menu_item.index = index
        menu_item.category_id = category_id
        menu_item.packaging_fee = packaging_fee
        return menu_item

    def delete(self, menu_item):
        self.db.delete(menu_item)
        self.db.flush()
        self.db.expunge(menu_item)

    def bulk_update_indices(self, update_mapping):
        # Perform bulk update
        self.db.execute(update(MenuItem), update_mapping)
        self.db.commit()

    def count_unique_vendor_ids_by_item_ids(self, ids: list[int]) -> int:
        if not ids:
            return 0
        stmt = (
            select(func.count(func.distinct(Menu.vendor_id)))
            .select_from(MenuItem)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .where(MenuItem.id.in_(ids))
        )
        return self.db.execute(stmt).scalar_one()

    def get_ids_by_menu(self, menu_id) -> list[int]:
        stmt = select(MenuItem.id).where(MenuItem.menu_id == menu_id)
        return list(self.db.execute(stmt).scalars().all())

    def bulk_edit(self, items: list, patch: dict):
        for item in items:
            for key, value in patch.items():
                setattr(item, key, value)
        self.db.flush()
        return items

    def bulk_delete(self, item_ids: list[int]):
        stmt = delete(MenuItem).where(MenuItem.id.in_(item_ids))
        self.db.execute(stmt)
        self.db.flush()
