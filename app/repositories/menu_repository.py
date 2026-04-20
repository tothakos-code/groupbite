from sqlalchemy import (
    String,
    and_,
    cast,
    func,
    or_,
    select,
)

from app.entities.menu import Menu


class MenuRepository:
    def __init__(self, db):
        self.db = db

    def find_by_vendor_id(self, vendor_id, date):
        stmt = select(Menu).where(
            Menu.vendor_id == vendor_id, Menu.from_date <= date, Menu.to_date >= date
        )
        return self.db.execute(stmt).scalars().first()

    def find_active_by_vendor_id(self, vendor_id, date):
        stmt = select(Menu).where(
            Menu.active,
            Menu.vendor_id == vendor_id,
            or_(Menu.from_date <= date, Menu.from_date == None),
            or_(Menu.to_date >= date, Menu.to_date == None),
        )

        return self.db.execute(stmt).scalars().all()

    def find_upcoming_by_vendor_id(self, vendor_id, from_date):
        """Returns all active menus that have not yet expired (to_date >= from_date or open-ended)."""
        stmt = select(Menu).where(
            Menu.active,
            Menu.vendor_id == vendor_id,
            or_(Menu.to_date >= from_date, Menu.to_date == None),
        )
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, menu_id):
        stmt = select(Menu).where(Menu.id == menu_id)

        return self.db.execute(stmt).scalars().first()

    def find_by_vendor(
        self,
        vendor_id,
        limit=None,
        offset=0,
        search=None,
        active=None,
        date_from=None,
        date_to=None,
    ):
        stmt = select(Menu).where(Menu.vendor_id == vendor_id)

        if search:
            stmt = stmt.where(
                or_(
                    Menu.name.ilike(f"%{search}%"),
                    cast(Menu.from_date, String).ilike(f"%{search}%"),
                    cast(Menu.to_date, String).ilike(f"%{search}%"),
                )
            )

        if active is not None:
            stmt = stmt.where(Menu.active == active)

        if date_from is not None and date_to is not None:
            stmt = stmt.where(
                and_(
                    or_(Menu.from_date == None, Menu.from_date <= date_to),
                    or_(Menu.to_date == None, Menu.to_date >= date_from),
                )
            )

        stmt = stmt.order_by(Menu.active.desc(), Menu.from_date.desc(), Menu.name)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)

        return self.db.execute(stmt).scalars().all()

    def count_by_vendor_id(self, vendor_id):
        stmt = select(func.count(Menu.id)).where(Menu.vendor_id == vendor_id)
        return self.db.execute(stmt).scalars().first()

    def save(self, menu):
        self.db.add(menu)
        self.db.flush()
        return menu

    def activate(self, menu):
        menu.active = True
        self.db.flush()

    def deactivate(self, menu):
        menu.active = False
        self.db.flush()

    def update(self, menu, name, from_date, to_date):
        menu.name = name
        menu.from_date = from_date
        menu.to_date = to_date
        self.db.flush()

    def delete(self, menu):
        self.db.delete(menu)
        self.db.flush()
        self.db.expunge(menu)
