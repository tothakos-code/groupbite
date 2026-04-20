import logging

from app.entities.menu_item import MenuItem
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository


class MenuItemService:
    def __init__(
        self,
    ):
        pass

    @staticmethod
    def add_item(db, menu_item: MenuItem):
        if not MenuRepository(db).get_by_id(menu_item.menu_id):
            logging.warning("Menu not found")
            raise ValueError("Menu not found")
        menu_item_repo = MenuItemRepository(db)
        items = menu_item_repo.find_all_by_menu(menu_item.menu_id, True)
        if not items:
            menu_item.index = 0
        else:
            menu_item.index = items[0].index + 1
        item = menu_item_repo.save(menu_item)

        return item

    @staticmethod
    def update_item(db, menu_item, data):
        menu_item_repo = MenuItemRepository(db)
        menu_item_repo.update(
            menu_item,
            data["menu_id"],
            data["name"],
            data["description"],
            data["index"],
            data["category"],
        )

    @staticmethod
    def delete_item(db, menu_item):
        menu_item_repo = MenuItemRepository(db)
        menu_item_repo.delete(menu_item)

    @staticmethod
    def bulk_update_indices(db, data):
        """
        Bulk update menu item indices.
        Expects a list of items with id and new index values.
        """

        items_to_update = data["items"]

        item_ids = [item["id"] for item in items_to_update]

        menu_item_repo = MenuItemRepository(db)
        # Validate that all items are in the same menu:
        if menu_item_repo.count_unique_menu_ids_by_item_ids(item_ids) != 1:
            raise ValueError("Not all items are in the same menu")

        menu_items = menu_item_repo.get_by_ids(item_ids)

        if len(menu_items) != len(item_ids):
            found_ids = {item.id for item in menu_items}
            missing_ids = set(item_ids) - found_ids
            return {"error": f"Items not found: {list(missing_ids)}"}, 404

        menu_item_repo.bulk_update_indices(items_to_update)
        logging.info(f"Successfully bulk updated {len(items_to_update)} item indices")

        return items_to_update
