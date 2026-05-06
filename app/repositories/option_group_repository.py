from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.entities.option_group import OptionGroup, option_group_item
from app.entities.option_choice import OptionChoice


class OptionGroupRepository:
    def __init__(self, db):
        self.db = db

    def find_by_vendor(self, vendor_id) -> list:
        stmt = (
            select(OptionGroup)
            .where(OptionGroup.vendor_id == vendor_id)
            .options(joinedload(OptionGroup.choices))
            .order_by(OptionGroup.index)
        )
        return self.db.execute(stmt).unique().scalars().all()

    def find_by_item(self, menu_item_id: int) -> list:
        stmt = (
            select(OptionGroup)
            .join(option_group_item, OptionGroup.id == option_group_item.c.option_group_id)
            .where(option_group_item.c.menu_item_id == menu_item_id)
            .options(joinedload(OptionGroup.choices))
            .order_by(option_group_item.c.index)
        )
        return self.db.execute(stmt).unique().scalars().all()

    def get_by_id(self, group_id: int):
        stmt = (
            select(OptionGroup)
            .where(OptionGroup.id == group_id)
            .options(joinedload(OptionGroup.choices))
        )
        return self.db.execute(stmt).unique().scalars().first()

    def save(self, group: OptionGroup) -> OptionGroup:
        self.db.add(group)
        self.db.flush()
        return group

    def delete(self, group_id: int):
        group = self.get_by_id(group_id)
        if group:
            self.db.delete(group)
            self.db.flush()

    def assign_to_item(self, option_group_id: int, menu_item_id: int, index: int = 0):
        self.db.execute(
            option_group_item.insert().values(
                option_group_id=option_group_id,
                menu_item_id=menu_item_id,
                index=index,
            )
        )
        self.db.flush()

    def unassign_from_item(self, option_group_id: int, menu_item_id: int):
        self.db.execute(
            option_group_item.delete().where(
                option_group_item.c.option_group_id == option_group_id,
                option_group_item.c.menu_item_id == menu_item_id,
            )
        )
        self.db.flush()
