from app.entities.basket_option_selection import BasketOptionSelection
from app.entities.user_basket import UserBasket
from app.repositories.basket_option_selection_repository import BasketOptionSelectionRepository
from app.repositories.option_group_repository import OptionGroupRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.user_basket_repository import UserBasketRepository
from app.services.bundle_engine import bundle_engine


class UserBasketService:
    @staticmethod
    def remove_item(db, user_id, menu_item_id, size_id, order_id, option_choice_ids=None):
        basket_repo = UserBasketRepository(db)
        size_repo = SizeRepository(db)

        line_key = _compute_line_key(option_choice_ids)
        basket_item = basket_repo.find_basket_item(
            order_id, user_id, menu_item_id, size_id, line_key=line_key
        )
        if not basket_item:
            raise ValueError("Item not found in basket")

        size = size_repo.get_by_id(size_id)
        if not size.unlimited:
            size_repo.increment_quantity(size)

        if basket_item.count == 1:
            BasketOptionSelectionRepository(db).delete_by_basket_entry(
                user_id, order_id, menu_item_id, size_id, line_key=line_key
            )
            basket_item = basket_repo.delete(basket_item)
        else:
            basket_repo.decrement_count(basket_item)

        bundle_engine.invalidate(order_id)
        return basket_item

    @staticmethod
    def add_item(db, user_id, menu_item_id, size_id, order_id,
                 option_choice_ids: list = None, skip_validation: bool = False):
        if not skip_validation:
            _validate_option_selections(db, menu_item_id, option_choice_ids)

        basket_repo = UserBasketRepository(db)
        size_repo = SizeRepository(db)

        line_key = _compute_line_key(option_choice_ids)
        basket_item = basket_repo.find_basket_item(
            order_id, user_id, menu_item_id, size_id, line_key=line_key
        )

        size = size_repo.get_by_id(size_id)
        if size.unlimited or size.quantity > 0:
            size_repo.decrement_quantity(size)
        else:
            raise ValueError("Item out of stock")

        if not basket_item:
            basket_item = basket_repo.add(
                UserBasket(
                    user_id=user_id,
                    menu_item_id=menu_item_id,
                    size_id=size_id,
                    order_id=order_id,
                    line_key=line_key,
                    count=1,
                )
            )
        else:
            basket_repo.increment_count(basket_item)

        bos_repo = BasketOptionSelectionRepository(db)
        bos_repo.delete_by_basket_entry(user_id, order_id, menu_item_id, size_id, line_key=line_key)
        for cid in (option_choice_ids or []):
            bos_repo.save(BasketOptionSelection(
                user_id=user_id,
                order_id=order_id,
                menu_item_id=menu_item_id,
                size_id=size_id,
                line_key=line_key,
                option_choice_id=cid,
            ))

        bundle_engine.invalidate(order_id)
        return basket_item

    @staticmethod
    def clear_items(db, user_id, order_id):
        BasketOptionSelectionRepository(db).delete_by_user_order(user_id, order_id)
        UserBasketRepository(db).clear_items(user_id, order_id)
        bundle_engine.invalidate(order_id)

    @staticmethod
    def delete(db, basket_item):
        user_basket_repo = UserBasketRepository(db)
        if not basket_item.size.unlimited:
            basket_item.size.quantity += basket_item.count
        user_basket_repo.delete(basket_item)

    @staticmethod
    def get_user_count_by_order(db, order_ids):
        user_basket_repo = UserBasketRepository(db)
        result = user_basket_repo.get_user_counts_batch(order_ids)
        return {row.order_id: row.user_count for row in result}


def _compute_line_key(option_choice_ids) -> str:
    if not option_choice_ids:
        return ""
    return ",".join(str(cid) for cid in sorted(int(cid) for cid in option_choice_ids))


def _validate_option_selections(db, menu_item_id: int, option_choice_ids: list):
    groups = OptionGroupRepository(db).find_by_item(menu_item_id)
    if not groups:
        return

    choice_ids = list(option_choice_ids or [])

    # Map each active choice id to its group for fast lookup.
    choice_to_group = {}
    for group in groups:
        for choice in group.choices:
            choice_to_group[choice.id] = group

    for cid in choice_ids:
        if cid not in choice_to_group:
            raise ValueError(f"Option choice {cid} is not valid for this item")

    for group in groups:
        count = sum(1 for cid in choice_ids if choice_to_group.get(cid) is group)
        if count < group.min_choices:
            raise ValueError(
                f"Option group '{group.name}' requires at least {group.min_choices} "
                f"selection(s), got {count}"
            )
        if count > group.max_choices:
            raise ValueError(
                f"Option group '{group.name}' allows at most {group.max_choices} "
                f"selection(s), got {count}"
            )
