from sqlalchemy import Column, String, Integer, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from .entity import Entity, Base
from marshmallow import Schema, fields

class Menu(Entity, Base):
    __tablename__ = 'menu'

    menu_date = Column(DateTime, default=func.current_date())
    menu = Column(ARRAY(JSONB))

    def __init__(self,menu_date, menu):
        Entity.__init__(self)
        self.menu_date = menu_date
        self.menu = menu

    def update(self, new_menu):
        self.menu = self.merge_lists(self.menu, new_menu)
        return self.menu

    # merging the new list with the current menu. If a new item apperar add to the current if dessaper one then mark is as sold_out.
    def merge_lists(self, old_list, new_list):
        merged_list = []
        old_dict_keys = {item['id']: item for item in old_list}

        for new_item in new_list:
            new_item_id = new_item['id']

            if new_item_id in old_dict_keys:
                old_item = old_dict_keys[new_item_id]
                if old_item != new_item:
                    old_item = new_item
                old_item['sold_out'] = False
                merged_list.append(old_item)
            else:
                new_item['sold_out'] = False
                merged_list.append(new_item)

        # If an item is missing mark it as sold_out
        for old_item in old_list:
            if old_item['id'] not in {item['id'] for item in new_list}:
                old_item['sold_out'] = True
                merged_list.append(old_item)

        return merged_list


class MenuSchema(Schema):
    id = fields.Number()
    menu_date = fields.DateTime()
    menu = fields.List(fields.Dict())
