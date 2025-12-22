from sqlalchemy import ForeignKey, select, exc, extract, Index, or_, func, and_, cast, String

from app.entities.vendor import Vendor, VendorType


class VendorRepository:

    def __init__(self, db):
        self.db = db

    def find_all(self):
        stmt = select(Vendor).order_by(Vendor.name)
        return self.db.execute(stmt).scalars().all()

    def find_all_by_type(self, vendor_type: VendorType):
        stmt = select(Vendor).where(Vendor.type == vendor_type)
        return self.db.execute(stmt).scalars().all()

    def find_all_active(self):
        stmt = select(Vendor).where(Vendor.active == True)
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, vendor_id):
        stmt = select(Vendor).where(
            Vendor.id == vendor_id
        )

        return self.db.execute(stmt).scalars().first()

    def save(self, vendor):
        self.db.add(vendor)
        self.db.flush()
        return vendor

    def activate(self, vendor):
        vendor.active = True
        self.db.flush()

    def deactivate(self, vendor):
        vendor.active = False
        self.db.flush()

    def update(self, vendor, name, from_date, to_date):
        vendor.name = name
        vendor.from_date = from_date
        vendor.to_date = to_date
        self.db.flush()

    def delete(self, vendor):
        self.db.delete(vendor)
        self.db.flush()
        self.db.expunge(vendor)

    def get_by_name_and_type(self, vendor_name: str, vendor_type: VendorType):
        stmt = select(Vendor).where(Vendor.type == vendor_type, Vendor.name == vendor_name)
        return self.db.execute(stmt).scalars().first()