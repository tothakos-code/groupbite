from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, JSON, func, Sequence, Boolean, select, or_, and_, exc
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import extract
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date as d
from marshmallow import Schema, fields
from typing import List
from uuid import UUID
from . import Base, session
from .vendor import Vendor
import enum
import datetime
import logging

class Frequency(enum.Enum):
    FIX = "fix"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    def __str__(self):
        return self.value

class BaseMenuSchema(Schema):
    name = fields.Str(required=True)
    vendor_id = fields.UUID(required=True)
    freq = fields.Str(required=True)

    items = fields.List(fields.Dict())

class UpdateMenuSchema(BaseMenuSchema):
    id = fields.Int(required=True)
    active = fields.Bool(required=True)
    date = fields.Date(required=True)


class Menu(Base):
    __tablename__ = "menu"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    date: Mapped[d] = mapped_column(insert_default=func.current_date())
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    freq_id: Mapped[Frequency] = mapped_column(default=Frequency.FIX)

    items: Mapped[List["MenuItem"]] = relationship(back_populates="menu", order_by="MenuItem.index")

    def __repr__(self):
        return f"Menu<{self.id},name={self.name},date={self.date},vendor_id={self.vendor_id}>"

    def find_vendor_menu(vendor_id, date, menu_freq):
        stmt = select(Menu).where(
            Menu.vendor_id == vendor_id,
            Menu.date == date,
            Menu.freq_id == menu_freq
        )
        return session.execute(stmt).scalars().first()

    def find_vendor_all_menu(vendor_id, date):
        stmt = select(Menu).where(
            Menu.active,
            Menu.vendor_id == vendor_id,
            or_(
                and_(
                    Menu.date == date,
                    Menu.freq_id == Frequency.DAILY
                ),
                and_(
                    Menu.freq_id == Frequency.FIX
                ),
                and_(
                    extract("week",Menu.date) == datetime.datetime.strptime(date, "%Y-%m-%d").isocalendar()[1],
                    Menu.freq_id == Frequency.WEEKLY
                ),
                and_(
                    extract("month",Menu.date) == datetime.datetime.strptime(date, "%Y-%m-%d").month,
                    Menu.freq_id == Frequency.MONTHLY
                ),
                and_(
                    extract("year",Menu.date) == datetime.datetime.strptime(date, "%Y-%m-%d").year,
                    Menu.freq_id == Frequency.YEARLY
                )
            )
        )

        return session.execute(stmt).scalars().all()

    def find_by_date(date=d.today().strftime("%Y-%m-%d")):
        stmt = select(Menu).where(Menu.date == date)
        return session.execute(stmt).scalars().first()

    def find_by_id(menu_id):
        stmt = select(Menu).where(
            Menu.id == menu_id
        )

        return session.execute(stmt).scalars().first()

    def find_all_by_vendor(vendor_id, limit=10, offset=0):
        stmt = select(Menu).where(
            Menu.vendor_id == vendor_id
        ).order_by(Menu.date.desc()).limit(limit).offset(offset)
        return session.execute(stmt).scalars().all()

    def count_by_vendor_id(vendor_id):
        stmt = select(func.count(Menu.id)).where(
            Menu.vendor_id == vendor_id
        )
        return session.execute(stmt).scalars().first()

    def add(menu):
        session.add(menu)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu add")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def activate(self):
        self.active = True;
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu activation")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def deactivate(self):
        self.active = False;
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu deactivation")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def update(self, name, date):
        self.name = name
        self.date = date
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def delete(self):
        session.delete(self)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu delete")
            session.rollback()
            return False
        except exc.IntegrityError as e:
            logging.exception("IntegrityError during Menu delete")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def fill_menu(vendor_id, date_to_fill, raw_item_list):
        """Creates MenuItem's from a raw json list of items.

        Parameters:
        vendor_id (str): Vendor ID which menu to be filled
        raw_item_list (Dict):

        """
        menu = Menu.find_vendor_menu(vendor_id, date_to_fill)
        if menu is None:
            logging.error("Menu to fill not found!")
            return
        # TODO: Handlig items that got out of stock
        for raw_menu_item in raw_item_list:
            found = False
            for item in menu.items:
                if item.name == raw_menu_item["name"]:
                    found = True
                    break
            if found:
                continue

            session.add(
                MenuItem(
                    menu_id=menu.id,
                    name=raw_menu_item["name"],
                    link=raw_menu_item["link"],
                    size=raw_menu_item["size"],
                    price=raw_menu_item["price"]
                )
            )
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

# TODO: Is this replaceable with Menu.add()?
    def create_menu(name, vendor, date, freq):
        menu = Menu.find_vendor_menu(vendor,date)
        # TODO: Need to check that date corresponed to the frequency. This currently only works for daily types
        if menu is not None:
            return
        session.add(Menu(name=name, vendor_id=vendor, date=date, freq_id=freq))
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during Menu create")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        from app.vendor_factory import VendorFactory
        return {
            "id": self.id,
            "name": self.name,
            "date": str(self.date),
            "vendor_id": str(self.vendor_id),
            "freq": str(self.freq_id),
            "active": self.active,
            "items": [item.serialized for item in self.items]
        }
