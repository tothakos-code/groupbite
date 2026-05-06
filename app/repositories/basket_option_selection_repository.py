from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.entities.basket_option_selection import BasketOptionSelection
from app.entities.option_choice import OptionChoice
from app.entities.option_group import OptionGroup


class BasketOptionSelectionRepository:
    def __init__(self, db):
        self.db = db

    def find_by_basket_entry(self, user_id, order_id: int, menu_item_id: int, size_id: int) -> list:
        stmt = select(BasketOptionSelection).where(
            BasketOptionSelection.user_id == user_id,
            BasketOptionSelection.order_id == order_id,
            BasketOptionSelection.menu_item_id == menu_item_id,
            BasketOptionSelection.size_id == size_id,
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_order_with_details(self, order_id: int) -> list:
        """Loads all selections for an order with choice and group eagerly loaded."""
        stmt = (
            select(BasketOptionSelection)
            .where(BasketOptionSelection.order_id == order_id)
            .options(
                joinedload(BasketOptionSelection.choice).joinedload(OptionChoice.group)
            )
        )
        return self.db.execute(stmt).unique().scalars().all()

    def find_by_user_order(self, user_id, order_id: int) -> list:
        stmt = select(BasketOptionSelection).where(
            BasketOptionSelection.user_id == user_id,
            BasketOptionSelection.order_id == order_id,
        )
        return self.db.execute(stmt).scalars().all()

    def save(self, selection: BasketOptionSelection) -> BasketOptionSelection:
        self.db.add(selection)
        self.db.flush()
        return selection

    def delete_by_basket_entry(self, user_id, order_id: int, menu_item_id: int, size_id: int):
        rows = self.find_by_basket_entry(user_id, order_id, menu_item_id, size_id)
        for row in rows:
            self.db.delete(row)
        self.db.flush()

    def delete_by_user_order(self, user_id, order_id: int):
        rows = self.find_by_user_order(user_id, order_id)
        for row in rows:
            self.db.delete(row)
        self.db.flush()
