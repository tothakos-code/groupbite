import logging

from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.size_repository import SizeRepository


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
    def update_size(db, size, data):
        size_repo = SizeRepository(db)
        size_repo.update(
            size,
            data["name"],
            data["price"],
            data["quantity"],
            data["unlimited"],
            data["index"],
        )
        return size

    @staticmethod
    def delete_size(db, size):
        size_repo = SizeRepository(db)
        size_repo.delete(size)

    @staticmethod
    def bulk_update_sizes(db, data):
        return SizeRepository(db).bulk_update(data["sizes"])
