import logging
from typing import Optional

from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository


class MenuService:

    def __init__(self):
        pass

    @staticmethod
    def get_by_id(db, menu_id: int) -> Optional[Menu]:
        menu_repo = MenuRepository(db)
        menu = menu_repo.get_by_id(menu_id)
        if not menu:
            logging.info(f"Order {menu_id} not found")
            raise ValueError(f"Order {menu_id} not found")
        return menu

    @staticmethod
    def deactivate_menu(db, menu_id: int) -> Optional[Menu]:
        menu_repo = MenuRepository(db)
        menu = menu_repo.get_by_id(menu_id)
        menu_repo.deactivate(menu)
        return menu

    @staticmethod
    def activate_menu(db, menu_id: int) -> Optional[Menu]:
        menu_repo = MenuRepository(db)
        menu = menu_repo.get_by_id(menu_id)
        menu_repo.activate(menu)
        return menu

    @staticmethod
    def add_menu(db, name, vendor_id) -> Menu:
        menu = Menu(name=name, vendor_id=vendor_id)
        menu_repo = MenuRepository(db)
        menu_repo.add(menu)
        return menu

    @staticmethod
    def delete_menu(db, menu_id: int):
        menu_repo = MenuRepository(db)
        menu = menu_repo.get_by_id(menu_id)
        menu_repo.delete(menu)

    @staticmethod
    def update_menu(db, menu_id, name, from_date, to_date) -> Menu:
        menu_repo = MenuRepository(db)
        menu = menu_repo.get_by_id(menu_id)
        menu_repo.update(menu, name, from_date, to_date)
        return menu

    @staticmethod
    def duplicate_menu(db, menu_id: int) -> Menu:
        menu_repo = MenuRepository(db)
        orig_menu = menu_repo.get_by_id(menu_id)

        new_menu = Menu(
            name=orig_menu.name + "-copy",
            vendor_id=orig_menu.vendor_id,
            from_date=orig_menu.from_date,
            to_date=orig_menu.to_date,
            active=False
        )

        for item in orig_menu.items:
            menu_item = MenuItem(
                name=item.name,
                category=item.category,
                description=item.description,
                index=item.index
            )

            for size in item.sizes:
                menu_item.sizes.append(Size(
                    link=size.link,
                    name=size.name,
                    price=size.price,
                    index=size.index,
                    quantity=size.quantity,
                    unlimited=size.unlimited
                ))

            new_menu.items.append(menu_item)
        menu_repo.add(new_menu)
        return new_menu

    @staticmethod
    def get_menu_items(db, menu_id, args):
        try:
            limit = int(args.get('limit'))
            page = int(args.get('page'))
        except (ValueError, TypeError):
            limit = None
            page = None

        offset = 0 if page is None else limit * (page - 1)
        search = args.get("search")
        menu_item_repo = MenuItemRepository(db)
        items = menu_item_repo.find_all_by_menu(menu_id, search, limit, offset)

        total_count = (
            menu_item_repo.count_by_menu_id(menu_id, search) if limit else len(items)
        )
        return {
            "items": [i.serialized for i in items],
            "page": page,
            "limit": limit,
            "total_count": total_count
        }