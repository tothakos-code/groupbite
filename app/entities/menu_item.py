from sqlalchemy import Column, Text, Enum, select
from uuid import UUID
from . import Base, session
from .size import Size
import enum
import logging
from typing import List
from sqlalchemy import ForeignKey, exc, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields

class BaseItemSchema(Schema):
    menu_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True)
    index = fields.Int(required=True)


class UpdateItemSchema(BaseItemSchema):
    id = fields.Int(required=True)



class MenuItem(Base):
    __tablename__ = "menu_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str]
    description: Mapped[str]
    index: Mapped[int]
    category: Mapped[str]

    sizes: Mapped[List["Size"]] = relationship(back_populates="menu_item", cascade="all, delete-orphan", order_by="Size.index", passive_deletes=True)
    orders: Mapped[List["UserBasket"]] = relationship(back_populates="item")
    menu: Mapped["Menu"] = relationship(back_populates="items")

    def __repr__(self):
        return f"MenuItem<{self.id},menu_id={self.menu_id},index={self.index},category={self.category}>"

    def find_all_by_menu(menu_id, limit=10, offset=0, desc=False):
        stmt = select(MenuItem).where(MenuItem.menu_id == menu_id)
        if desc:
            stmt = stmt.order_by(MenuItem.category, MenuItem.index.desc())
        else:
            stmt = stmt.order_by(MenuItem.category, MenuItem.index)
        stmt = stmt.limit(limit).offset(offset)

        return session.execute(stmt).scalars().all()


    def count_by_menu_id(menu_id):
        stmt = select(func.count(MenuItem.id)).where(
            MenuItem.menu_id == menu_id
        )
        return session.execute(stmt).scalars().first()

    def find_all_by_menu_list(menu_id_list, filter=[], desc=False):
        stmt = select(MenuItem).where(
            MenuItem.menu_id.in_(menu_id_list),
            MenuItem.category.in_(filter) if len(filter) != 0 else True
            )
        if desc:
            stmt = stmt.order_by(MenuItem.category, MenuItem.index.desc())
        else:
            stmt = stmt.order_by(MenuItem.category, MenuItem.index)

        return session.execute(stmt).scalars().all()

    def find_by_id(id):
        stmt = select(MenuItem).where(
            MenuItem.id == id
        )
        return session.execute(stmt).scalars().first()

    def add(item):
        items = MenuItem.find_all_by_menu(item.menu_id, True)
        if not items:
            item.index = 0
        else:
            item.index = items[0].index + 1

        session.add(item)
        try:
            session.commit()
            session.refresh(item)
            return True, item
        except exc.DataError as e:
            logging.exception("DataError during menuitem add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def update(self, name, description, index, category):
        self.name = name
        self.description = description
        self.index = index
        self.category = category
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during menuitem update")
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
            logging.exception("DataError during menuitem update")
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


    @property
    def serialized(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "index": self.index,
            "sizes": [size.serialized for size in self.sizes],
            "category": self.category
        }
