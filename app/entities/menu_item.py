from sqlalchemy import Column, Text, Enum, select, update
from uuid import UUID
from . import Base, session
from .size import Size
import enum
import logging
from typing import List
from sqlalchemy import ForeignKey, exc, func, or_
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, validate

class BaseItemSchema(Schema):
    menu_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True)
    index = fields.Int(required=True)


class UpdateItemSchema(BaseItemSchema):
    id = fields.Int(required=True)
    menu_id = fields.Int(required=True)

class BulkUpdateItemSchema(Schema):
    items = fields.List(
        fields.Nested({
            'id': fields.Integer(required=True),
            'index': fields.Integer(required=True, validate=validate.Range(min=0))
        }),
        required=True,
        validate=validate.Length(min=1, max=1000)
    )


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

    def find_all_by_menu(menu_id, search=None, limit=10, offset=0, desc=False):
        stmt = select(MenuItem).where(MenuItem.menu_id == menu_id)

        if search:
            ilike_expr = f"%{search}%"
            stmt = stmt.where(
                or_(
                    MenuItem.category.ilike(ilike_expr),
                    MenuItem.name.ilike(ilike_expr),
                    MenuItem.description.ilike(ilike_expr)
                )
            )

        stmt = stmt.order_by(MenuItem.index.desc() if desc else MenuItem.index)

        if limit:
            stmt = stmt.limit(limit).offset(offset)

        return session.execute(stmt).scalars().all()

    def get_by_ids(ids: list[int]):
        if not ids:
            return []

        stmt = select(MenuItem).where(MenuItem.id.in_(ids))
        return session.execute(stmt).scalars().all()

    def count_unique_menu_ids_by_item_ids(ids: list[int]):
        if not ids:
            return 0

        stmt = select(func.count(func.distinct(MenuItem.menu_id))).where(
            MenuItem.id.in_(ids)
        )
        return session.execute(stmt).scalar_one()

    def count_by_menu_id(menu_id, search=None):
        stmt = select(func.count(MenuItem.id)).where(
            MenuItem.menu_id == menu_id
        )

        if search:
            ilike_expr = f"%{search}%"
            stmt = stmt.where(
                or_(
                    MenuItem.category.ilike(ilike_expr),
                    MenuItem.name.ilike(ilike_expr),
                    MenuItem.description.ilike(ilike_expr)
                )
            )

        return session.execute(stmt).scalar_one()

    def find_all_by_menu_list(menu_id_list, filter=None, limit=None, desc=False):
        """
        Find all menu items by menu ID list with proper filtering and ordering

        Args:
            menu_id_list: List of menu IDs to search in
            filter: Optional list of categories to filter by
            limit: Optional limit for number of results
            desc: Whether to sort in descending order

        Returns:
            List of MenuItem objects properly ordered
        """
        if filter is None:
            filter = []

        # Build the base query
        stmt = select(MenuItem).where(MenuItem.menu_id.in_(menu_id_list))

        # Add category filter if provided and not empty
        if filter and len(filter) > 0:
            stmt = stmt.where(MenuItem.category.in_(filter))

        # Add ordering - first by category, then by index
        if desc:
            stmt = stmt.order_by(
                MenuItem.category.desc(),
                MenuItem.index.desc()
            )
        else:
            stmt = stmt.order_by(
                MenuItem.category.asc(),
                MenuItem.index.asc()
            )

        # Add limit if specified
        if limit:
            stmt = stmt.limit(limit)

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

    def update(self, menu_id, name, description, index, category):
        self.name = name
        self.menu_id = menu_id
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

    def bulk_update_indices(update_mapping):
        if not update_mapping:
            return True

        try:
            # Perform bulk update
            session.execute(update(MenuItem), update_mapping)
            session.commit()

            logging.info(f"Successfully bulk updated {len(update_mapping)} item indices")
            return True

        except exc.DataError as e:
            logging.exception("DataError during bulk index update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception during bulk index update")
            session.rollback()
            return False


    @property
    def serialized(self):
        return {
            "id": self.id,
            "menu_id": self.menu_id,
            "name": self.name,
            "description": self.description,
            "index": self.index,
            "sizes": [size.serialized for size in self.sizes],
            "category": self.category
        }
