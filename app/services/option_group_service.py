from sqlalchemy import select

from app.entities.basket_option_selection import BasketOptionSelection
from app.entities.option_choice import OptionChoice
from app.entities.option_group import OptionGroup
from app.entities.order import Order, OrderState
from app.repositories.basket_option_selection_repository import BasketOptionSelectionRepository
from app.repositories.option_choice_repository import OptionChoiceRepository
from app.repositories.option_group_repository import OptionGroupRepository


class OptionGroupService:
    @staticmethod
    def get_by_vendor(db, vendor_id) -> list:
        return OptionGroupRepository(db).find_by_vendor(vendor_id)

    @staticmethod
    def get_by_item(db, menu_item_id: int) -> list:
        return OptionGroupRepository(db).find_by_item(menu_item_id)

    @staticmethod
    def create(db, vendor_id, name: str, min_choices: int, max_choices: int,
               required: bool, index: int) -> OptionGroup:
        group = OptionGroup(
            vendor_id=vendor_id,
            name=name,
            min_choices=min_choices,
            max_choices=max_choices,
            required=required,
            index=index,
        )
        return OptionGroupRepository(db).save(group)

    @staticmethod
    def update(db, group_id: int, **fields) -> OptionGroup:
        repo = OptionGroupRepository(db)
        group = repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"OptionGroup {group_id} not found")
        allowed = {"name", "min_choices", "max_choices", "required", "index"}
        for key, value in fields.items():
            if key in allowed:
                setattr(group, key, value)
        return repo.save(group)

    @staticmethod
    def delete(db, group_id: int):
        repo = OptionGroupRepository(db)
        group = repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"OptionGroup {group_id} not found")

        choice_ids = [c.id for c in group.choices]
        if choice_ids and _has_open_order_selections(db, choice_ids):
            raise ValueError(
                "Cannot delete option group: it is referenced by an active order basket"
            )
        repo.delete(group_id)

    @staticmethod
    def add_choice(db, group_id: int, name: str, price_delta: int, index: int) -> OptionChoice:
        choice = OptionChoice(
            option_group_id=group_id,
            name=name,
            price_delta=price_delta,
            index=index,
            active=True,
        )
        return OptionChoiceRepository(db).save(choice)

    @staticmethod
    def update_choice(db, choice_id: int, **fields) -> OptionChoice:
        repo = OptionChoiceRepository(db)
        choice = repo.find_by_id_include_inactive(choice_id)
        if not choice:
            raise ValueError(f"OptionChoice {choice_id} not found")
        allowed = {"name", "price_delta", "index"}
        for key, value in fields.items():
            if key in allowed:
                setattr(choice, key, value)
        return repo.save(choice)

    @staticmethod
    def soft_delete_choice(db, choice_id: int):
        repo = OptionChoiceRepository(db)
        choice = repo.find_by_id_include_inactive(choice_id)
        if not choice:
            raise ValueError(f"OptionChoice {choice_id} not found")
        if _has_open_order_selections(db, [choice_id]):
            raise ValueError(
                "Cannot delete option choice: it is referenced by an active order basket"
            )
        repo.soft_delete(choice_id)

    @staticmethod
    def assign_to_item(db, group_id: int, item_id: int, index: int = 0):
        OptionGroupRepository(db).assign_to_item(group_id, item_id, index)

    @staticmethod
    def unassign_from_item(db, group_id: int, item_id: int):
        OptionGroupRepository(db).unassign_from_item(group_id, item_id)


def _has_open_order_selections(db, choice_ids: list) -> bool:
    stmt = (
        select(BasketOptionSelection.id)
        .join(Order, Order.id == BasketOptionSelection.order_id)
        .where(
            BasketOptionSelection.option_choice_id.in_(choice_ids),
            Order.state_id != OrderState.CLOSED,
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None
