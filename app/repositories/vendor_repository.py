from sqlalchemy import select

from app.entities.order import Order
from app.entities.user_basket import UserBasket
from app.entities.vendor import MenuType, Vendor


class VendorRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        stmt = select(Vendor).order_by(Vendor.name)
        return self.db.execute(stmt).scalars().all()

    def find_all_by_menu_type(self, menu_type: MenuType):
        stmt = select(Vendor).where(Vendor.menu_type == menu_type)
        return self.db.execute(stmt).scalars().all()

    def find_all_active(self):
        stmt = select(Vendor).where(Vendor.active == True)
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, vendor_id):
        stmt = select(Vendor).where(Vendor.id == vendor_id)
        return self.db.execute(stmt).scalars().first()

    def get_by_plugin_id(self, plugin_id: str):
        stmt = select(Vendor).where(Vendor.plugin_id == plugin_id)
        return self.db.execute(stmt).scalars().all()

    def get_by_name(self, name: str):
        stmt = select(Vendor).where(Vendor.name == name)
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

    def update(self, vendor, name):
        vendor.name = name
        self.db.flush()

    def delete(self, vendor):
        self.db.delete(vendor)
        self.db.flush()
        self.db.expunge(vendor)

    def find_vendors_by_user_orders(self, user_id):
        user_vendor_ids_subquery = (
            select(Order.vendor_id)
            .join(UserBasket, UserBasket.order_id == Order.id)
            .where(UserBasket.user_id == user_id)
            .distinct()
            .subquery()
        )

        stmt = (
            select(Vendor)
            .where(Vendor.id.in_(select(user_vendor_ids_subquery.c.vendor_id)))
            .order_by(Vendor.name)
        )
        return self.db.execute(stmt).scalars().all()
