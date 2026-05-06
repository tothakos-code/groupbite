from app.entities.bundle_discount import BundleDiscount
from app.entities.bundle_slot import BundleSlot
from app.repositories.bundle_discount_repository import BundleDiscountRepository
from app.repositories.order_repository import OrderRepository
from app.services.bundle_engine import bundle_engine


class BundleDiscountService:
    @staticmethod
    def get_by_vendor(db, vendor_id) -> list:
        return BundleDiscountRepository(db).find_by_vendor(vendor_id)

    @staticmethod
    def create(db, vendor_id, name: str, description: str = None) -> BundleDiscount:
        bundle = BundleDiscount(vendor_id=vendor_id, name=name, description=description)
        return BundleDiscountRepository(db).save(bundle)

    @staticmethod
    def update(db, bundle_id: int, **fields) -> BundleDiscount:
        repo = BundleDiscountRepository(db)
        bundle = repo.get_by_id(bundle_id)
        if not bundle:
            raise ValueError(f"BundleDiscount {bundle_id} not found")
        allowed = {"name", "description"}
        for key, value in fields.items():
            if key in allowed:
                setattr(bundle, key, value)
        return repo.save(bundle)

    @staticmethod
    def delete(db, bundle_id: int):
        repo = BundleDiscountRepository(db)
        bundle = repo.get_by_id(bundle_id)
        if not bundle:
            raise ValueError(f"BundleDiscount {bundle_id} not found")
        _invalidate_vendor_orders(db, bundle.vendor_id)
        repo.delete(bundle_id)

    @staticmethod
    def add_slot(db, bundle_id: int, slot_index: int, match_type: str,
                 category_id: int = None, menu_item_id: int = None,
                 price_override: int = None, price_delta: int = None) -> BundleSlot:
        slot = BundleSlot(
            bundle_discount_id=bundle_id,
            slot_index=slot_index,
            match_type=match_type,
            category_id=category_id,
            menu_item_id=menu_item_id,
            price_override=price_override,
            price_delta=price_delta,
        )
        repo = BundleDiscountRepository(db)
        slot = repo.save_slot(slot)
        bundle = repo.get_by_id(bundle_id)
        if bundle:
            _invalidate_vendor_orders(db, bundle.vendor_id)
        return slot

    @staticmethod
    def update_slot(db, slot_id: int, **fields) -> BundleSlot:
        repo = BundleDiscountRepository(db)
        slot = repo.get_slot_by_id(slot_id)
        if not slot:
            raise ValueError(f"BundleSlot {slot_id} not found")
        allowed = {"slot_index", "match_type", "category_id", "menu_item_id",
                   "price_override", "price_delta"}
        for key, value in fields.items():
            if key in allowed:
                setattr(slot, key, value)
        slot = repo.save_slot(slot)
        bundle = repo.get_by_id(slot.bundle_discount_id)
        if bundle:
            _invalidate_vendor_orders(db, bundle.vendor_id)
        return slot

    @staticmethod
    def delete_slot(db, slot_id: int):
        repo = BundleDiscountRepository(db)
        slot = repo.get_slot_by_id(slot_id)
        if not slot:
            raise ValueError(f"BundleSlot {slot_id} not found")
        bundle = repo.get_by_id(slot.bundle_discount_id)
        vendor_id = bundle.vendor_id if bundle else None
        repo.delete_slot(slot_id)
        if vendor_id:
            _invalidate_vendor_orders(db, vendor_id)


def _invalidate_vendor_orders(db, vendor_id):
    for order in OrderRepository(db).find_all_open_for_vendor(vendor_id):
        bundle_engine.invalidate(order.id)
