from sqlalchemy import Column, String, Integer, DateTime, JSON, func, Sequence, select, or_, and_
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date
import enum
from typing import List
from . import Base, session
from uuid import UUID
from .vendor import Vendor
from marshmallow import Schema, fields

class Frequency(enum.Enum):
    FIX = 'fix'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

    def __str__(self):
        return self.value



class Menu(Base):
    __tablename__ = 'menu'


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    menu_date: Mapped[date] = mapped_column(insert_default=func.current_date())
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    freq_id: Mapped[Frequency] = mapped_column(default=Frequency.FIX)

    items: Mapped[List["MenuItem"]] = relationship(back_populates="menu")

    def __repr__(self):
        return f"Menu<{self.id},name={self.name},menu_date={self.menu_date},vendor_id={self.vendor_id}>"

    def find_vendor_daily_menu(vendor_id, menu_date):
        return session.query(Menu).filter_by(vendor_id = vendor_id, menu_date = menu_date).first()

    def find_vendor_all_menu(vendor_id, menu_date):
        stmt = select(Menu).where(
            or_(
                and_(
                    Menu.vendor_id == vendor_id,
                    Menu.menu_date == menu_date
                ),
                and_(
                    Menu.vendor_id == vendor_id,
                    Menu.freq_id == Frequency.FIX
                )
            )
        )

        return session.execute(stmt).scalars().all()

    def find_all_by_vendor(vendor_id):
        return session.query(Menu).filter_by(vendor_id = vendor_id).all()

    def add(menu):
        session.add(menu)
        session.commit()
        session.close()

    @property
    def serialized(self):
        from app.vendor_factory import VendorFactory
        return {
            'id': self.id,
            'name': self.name,
            'date': str(self.menu_date),
            'vendor_id': str(self.vendor_id),
            'freq': str(self.freq_id),
        }
