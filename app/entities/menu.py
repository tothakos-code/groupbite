from sqlalchemy import Column, String, Integer, DateTime, JSON, func, Sequence
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

    def find_vendor_menu(vendor_id, menu_date):
        return session.query(Menu).filter_by(vendor_id = vendor_id, menu_date = menu_date).first()

    # def update(self, new_menu):
    #     self.menu = self.merge_lists(self.menu, new_menu)
    #     return self.menu
    #
    # # merging the new list with the current menu. If a new item apperar add to the current if dessaper one then mark is as sold_out.
    # def merge_lists(self, old_list, new_list):
    #     merged_list = []
    #     old_dict_keys = {item['id']: item for item in old_list}
    #
    #     for new_item in new_list:
    #         new_item_id = new_item['id']
    #
    #         if new_item_id in old_dict_keys:
    #             old_item = old_dict_keys[new_item_id]
    #             if old_item != new_item:
    #                 old_item = new_item
    #             old_item['sold_out'] = False
    #             merged_list.append(old_item)
    #         else:
    #             new_item['sold_out'] = False
    #             merged_list.append(new_item)
    #
    #     # If an item is missing mark it as sold_out
    #     for old_item in old_list:
    #         if old_item['id'] not in {item['id'] for item in new_list}:
    #             old_item['sold_out'] = True
    #             merged_list.append(old_item)
    #
    #     return merged_list


# class MenuSchema(Schema):
#     id = fields.Number()
#     menu_date = fields.DateTime()
#     menu = fields.List(fields.Dict())
