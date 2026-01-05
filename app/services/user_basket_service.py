from app.entities.user_basket import UserBasket
from app.repositories.size_repository import SizeRepository
from app.repositories.user_basket_repository import UserBasketRepository


class UserBasketService:
    @staticmethod
    def remove_item(db, user_id, menu_item_id, size_id, order_id):
        basket_repo = UserBasketRepository(db)
        size_repo = SizeRepository(db)

        # Find basket item
        basket_item = basket_repo.find_basket_item(order_id, user_id, menu_item_id, size_id)
        if not basket_item:
            raise ValueError("Item not found in basket")

        # Return size to inventory if not unlimited
        size = size_repo.get_by_id(size_id)
        if not size.unlimited:
            size_repo.increment_quantity(size)

        # Remove or decrement
        if basket_item.count == 1:
            basket_item = basket_repo.delete(basket_item)
        else:
            basket_repo.decrement_count(basket_item)

        return basket_item

    @staticmethod
    def add_item(db, user_id, menu_item_id, size_id, order_id):
        basket_repo = UserBasketRepository(db)
        size_repo = SizeRepository(db)

        # Find basket item
        basket_item = basket_repo.find_basket_item(order_id, user_id, menu_item_id, size_id)

        # Return size to inventory if not unlimited
        size = size_repo.get_by_id(size_id)
        if size.unlimited or size.quantity > 0:
            size_repo.decrement_quantity(size)
        else:
            raise ValueError("Item out of stock")

        # Remove or decrement
        if not basket_item:
            basket_item = basket_repo.add(UserBasket(
                    user_id = user_id,
                    menu_item_id = menu_item_id,
                    size_id = size_id,
                    order_id = order_id,
                    count = 1
                ))
        else:
            basket_repo.increment_count(basket_item)

        return basket_item

    @staticmethod
    def clear_items(db, user_id, order_id):
        basket_repo = UserBasketRepository(db)
        basket_repo.clear_items(order_id, user_id)

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
