from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, JSON, func, Sequence, Boolean, select, or_, and_, exc, cast
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
    items = fields.List(fields.Dict())

class UpdateMenuSchema(BaseMenuSchema):
    id = fields.Int(required=True)
    active = fields.Bool(required=True)
    from_date = fields.Date(allow_none=True)
    to_date = fields.Date(allow_none=True)


class Menu(Base):
    __tablename__ = "menu"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    from_date: Mapped[d] = mapped_column(insert_default=func.current_date(), nullable=True)
    to_date: Mapped[d] = mapped_column(insert_default=func.current_date(), nullable=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))

    items: Mapped[List["MenuItem"]] = relationship(back_populates="menu", cascade="all, delete", order_by="MenuItem.index")

    def __repr__(self):
        return f"Menu<{self.id},name={self.name},from_date={self.from_date},to_date={self.to_date},vendor_id={self.vendor_id}>"

    def find_all_active(vendor_id, date):
        stmt = select(Menu).where(
            Menu.active,
            Menu.vendor_id == vendor_id,
            or_(
                Menu.from_date <= date,
                Menu.from_date == None
            ),
            or_(
                Menu.to_date >= date,
                Menu.to_date == None
            )
        )

        return session.execute(stmt).scalars().all()

    def find_by_id(menu_id):
        stmt = select(Menu).where(
            Menu.id == menu_id
        )

        return session.execute(stmt).scalars().first()

    def find_by_vendor(vendor_id, limit=None, offset=0, search=None, active=None, date_from=None, date_to=None):
        stmt = select(Menu).where(
            Menu.vendor_id == vendor_id
        )

        if search:
            stmt = stmt.where(
                or_(
                    Menu.name.ilike(f"%{search}%"),
                    cast(Menu.from_date, String).ilike(f"%{search}%"),
                    cast(Menu.to_date, String).ilike(f"%{search}%")
                )
            )

        if active is not None:
            stmt = stmt.where(Menu.active == active)

        if date_from is not None and date_to is not None:
            stmt = stmt.where(
                 and_(
                    or_(Menu.from_date == None, Menu.from_date <= date_to),
                    or_(Menu.to_date == None,   Menu.to_date   >= date_from)
                )
            )

        stmt = stmt.order_by(Menu.active.desc(), Menu.from_date.desc(), Menu.name)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)

        return session.execute(stmt).scalars().all()

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

    @property
    def serialized(self):
        return {
            "id": self.id,
            "name": self.name,
            "from_date": str(self.from_date if self.from_date else ""),
            "to_date": str(self.to_date if self.to_date else ""),
            "vendor_id": str(self.vendor_id),
            "active": self.active,
            "items": [item.serialized for item in self.items]
        }
