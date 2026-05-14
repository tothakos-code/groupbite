from sqlalchemy import func, select

from app.entities.category import Category
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.entities.stock_history import StockChangeReason, StockHistory
from app.repositories.size_repository import SizeRepository
from app.repositories.stock_history_repository import StockHistoryRepository


class StockService:

    @staticmethod
    def top_up_stock(db, size_id: int, quantity: int, note: str, admin_user_id) -> tuple[Size, StockHistory]:
        size = SizeRepository(db).get_by_id(size_id)
        if not size:
            raise ValueError(f"Size {size_id} not found")
        if quantity <= 0:
            raise ValueError("Top-up quantity must be positive")
        size.quantity += quantity
        db.flush()
        entry = StockHistoryRepository(db).save(StockHistory(
            size_id=size.id, quantity_change=quantity,
            reason=StockChangeReason.TOPUP,
            performed_by=admin_user_id, note=note,
        ))
        return size, entry

    @staticmethod
    def get_stock_levels(db, vendor_id, category_id=None) -> list[dict]:
        stmt = (
            select(MenuItem, Size, Category)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .join(Size, Size.menu_item_id == MenuItem.id)
            .outerjoin(Category, MenuItem.category_id == Category.id)
            .where(
                Menu.vendor_id == vendor_id,
                Size.unlimited.is_(False),
            )
            .order_by(Category.name, MenuItem.name, Size.index)
        )
        if category_id is not None:
            stmt = stmt.where(MenuItem.category_id == category_id)

        rows = db.execute(stmt).all()

        items: dict[int, dict] = {}
        for menu_item, size, category in rows:
            if menu_item.id not in items:
                items[menu_item.id] = {
                    "item_id": menu_item.id,
                    "item_name": menu_item.name,
                    "category_id": menu_item.category_id,
                    "category_name": category.name if category else None,
                    "sizes": [],
                }
            items[menu_item.id]["sizes"].append({
                "size_id": size.id,
                "size_name": size.name,
                "quantity": size.quantity,
                "unlimited": size.unlimited,
            })

        return list(items.values())

    @staticmethod
    def get_stock_history(db, size_id: int, from_date=None, to_date=None) -> dict:
        size = SizeRepository(db).get_by_id(size_id)
        if not size:
            raise ValueError(f"Size {size_id} not found")

        history = StockHistoryRepository(db).find_by_size(size_id, from_date, to_date)

        total_recorded = sum(e.quantity_change for e in history)
        anchor_quantity = size.quantity - total_recorded

        return {
            "anchor_quantity": anchor_quantity,
            "history": [e.serialized for e in history],
        }
