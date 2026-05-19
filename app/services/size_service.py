import logging

from sqlalchemy import select

from app.entities.size import Size
from app.entities.stock_history import StockChangeReason, StockHistory
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.stock_history_repository import StockHistoryRepository


class SizeService:
    @staticmethod
    def add_size(db, size):
        if not MenuItemRepository(db).get_by_id(size.menu_item_id):
            logging.warning("MenuItem not found")
            raise ValueError("MenuItem not found")

        size_repo = SizeRepository(db)
        sizes = size_repo.find_all_by_menu_item(size.menu_item_id, True)
        if not sizes:
            size.index = 0
        else:
            size.index = sizes[0].index + 1
        size_repo.save(size)

    @staticmethod
    def update_size(db, size, data, admin_user_id=None):
        old_qty = size.quantity
        SizeRepository(db).update(
            size,
            data["name"],
            data["price"],
            data["quantity"],
            data["unlimited"],
            data["index"],
        )
        if size.quantity != old_qty:
            StockHistoryRepository(db).save(StockHistory(
                size_id=size.id,
                quantity_change=size.quantity - old_qty,
                reason=StockChangeReason.ADJUSTMENT,
                performed_by=admin_user_id,
            ))
        return size

    @staticmethod
    def delete_size(db, size):
        SizeRepository(db).delete(size)

    @staticmethod
    def bulk_update_sizes(db, data, admin_user_id=None):
        sizes_data = data["sizes"]
        ids = [s["id"] for s in sizes_data]
        sizes = {
            s.id: s
            for s in db.execute(select(Size).where(Size.id.in_(ids))).scalars().all()
        }
        history_repo = StockHistoryRepository(db)
        updated = []
        for item_data in sizes_data:
            size = sizes.get(item_data["id"])
            if not size:
                continue
            old_qty = size.quantity
            size.name = item_data["name"]
            size.price = item_data["price"]
            size.quantity = item_data["quantity"]
            size.unlimited = item_data["unlimited"]
            if size.quantity != old_qty:
                db.add(StockHistory(
                    size_id=size.id,
                    quantity_change=size.quantity - old_qty,
                    reason=StockChangeReason.ADJUSTMENT,
                    performed_by=admin_user_id,
                ))
            updated.append(size)
        db.flush()
        return updated

    @staticmethod
    def bulk_edit_prices_by_items(db, data):
        item_repo = MenuItemRepository(db)

        item_ids = data.get('item_ids')
        if data.get('select_all_menu_id') is not None:
            item_ids = item_repo.get_ids_by_menu(data['select_all_menu_id'])

        if not item_ids:
            raise ValueError("No items found")

        if item_repo.count_unique_vendor_ids_by_item_ids(item_ids) != 1:
            raise ValueError("Items must belong to the same vendor")

        mode = data['mode']
        value = data['value']

        sizes = SizeRepository(db).get_by_item_ids(item_ids)
        for size in sizes:
            if mode == 'set':
                size.price = value
            elif mode == 'adjust_fixed':
                size.price = max(0, size.price + value)
            elif mode == 'adjust_percent':
                size.price = max(0, round(size.price * (1 + value / 100)))

        db.flush()
        return sizes
