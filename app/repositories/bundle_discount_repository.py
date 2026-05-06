from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.entities.bundle_discount import BundleDiscount
from app.entities.bundle_slot import BundleSlot


class BundleDiscountRepository:
    def __init__(self, db):
        self.db = db

    def find_by_vendor(self, vendor_id) -> list:
        stmt = (
            select(BundleDiscount)
            .where(BundleDiscount.vendor_id == vendor_id)
            .options(joinedload(BundleDiscount.slots))
        )
        return self.db.execute(stmt).unique().scalars().all()

    def get_by_id(self, bundle_id: int):
        stmt = (
            select(BundleDiscount)
            .where(BundleDiscount.id == bundle_id)
            .options(joinedload(BundleDiscount.slots))
        )
        return self.db.execute(stmt).unique().scalars().first()

    def save(self, bundle: BundleDiscount) -> BundleDiscount:
        self.db.add(bundle)
        self.db.flush()
        return bundle

    def delete(self, bundle_id: int):
        bundle = self.get_by_id(bundle_id)
        if bundle:
            self.db.delete(bundle)
            self.db.flush()

    def get_slot_by_id(self, slot_id: int):
        stmt = select(BundleSlot).where(BundleSlot.id == slot_id)
        return self.db.execute(stmt).scalars().first()

    def save_slot(self, slot: BundleSlot) -> BundleSlot:
        self.db.add(slot)
        self.db.flush()
        return slot

    def delete_slot(self, slot_id: int):
        slot = self.get_slot_by_id(slot_id)
        if slot:
            self.db.delete(slot)
            self.db.flush()
