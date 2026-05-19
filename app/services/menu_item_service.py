import logging

from app.entities.menu_item import MenuItem
from app.repositories.category_repository import CategoryRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository
from app.services.category_service import CategoryService


class MenuItemService:
    def __init__(
        self,
    ):
        pass

    @staticmethod
    def add_item(db, vendor_id, menu_item: MenuItem):
        menu = MenuRepository(db).get_by_id(menu_item.menu_id)
        if not menu:
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
    def update_item(db, vendor_id, menu_item, data):
        category = CategoryService.get_or_create(db, vendor_id, data.get("category") or "")
        menu_item_repo = MenuItemRepository(db)
        menu_item_repo.update(
            menu_item,
            data["menu_id"],
            data["name"],
            data["description"],
            data["index"],
            category.id,
            packaging_fee=data.get("packaging_fee"),
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

    @staticmethod
    def bulk_edit(db, data):
        repo = MenuItemRepository(db)

        item_ids = data.get('item_ids')
        if data.get('select_all_menu_id') is not None:
            item_ids = repo.get_ids_by_menu(data['select_all_menu_id'])

        if not item_ids:
            raise ValueError("No items found")

        if repo.count_unique_vendor_ids_by_item_ids(item_ids) != 1:
            raise ValueError("Items must belong to the same vendor")

        items = repo.get_by_ids(item_ids)

        patch = {k: data[k] for k in ('category_id', 'packaging_fee', 'description') if k in data}

        if 'category_id' in patch and patch['category_id'] is not None:
            vendor_id = items[0].menu.vendor_id
            category = CategoryRepository(db).get_by_id(patch['category_id'])
            if not category or category.vendor_id != vendor_id:
                raise ValueError("Category not found or belongs to a different vendor")

        return repo.bulk_edit(items, patch)

    @staticmethod
    def bulk_delete(db, data):
        repo = MenuItemRepository(db)

        item_ids = data.get('item_ids')
        if data.get('select_all_menu_id') is not None:
            item_ids = repo.get_ids_by_menu(data['select_all_menu_id'])

        if not item_ids:
            raise ValueError("No items found")

        if repo.count_unique_vendor_ids_by_item_ids(item_ids) != 1:
            raise ValueError("Items must belong to the same vendor")

        repo.bulk_delete(item_ids)
        return len(item_ids)
