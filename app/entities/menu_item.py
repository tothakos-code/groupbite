from sqlalchemy import Column, Text, Enum, select
from uuid import UUID
from . import Base, session
from .size import Size
import enum
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class MenuItem(Base):
    __tablename__ = 'menu_item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str]
    index: Mapped[int]
    category: Mapped[str]

    sizes: Mapped[List["Size"]] = relationship(back_populates="menu_item", cascade="all, delete-orphan", order_by="Size.index", passive_deletes=True)
    orders: Mapped[List["UserBasket"]] = relationship(back_populates="item")
    menu: Mapped["Menu"] = relationship(back_populates="items")

    def __repr__(self):
        return f"MenuItem<{self.id},menu_id={self.menu_id},index={self.index},category={self.category}>"

    def find_all_by_menu(menu_id, desc=False):
        stmt = select(MenuItem).where(MenuItem.menu_id == menu_id)
        if desc:
            stmt.order_by(MenuItem.index.desc())
        else:
            stmt.order_by(MenuItem.index)

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
            item.index = items[-1].index + 1
        session.add(item)
        session.commit()

    def update(self, name, index, category):
        self.name = name
        self.index = index
        self.category = category
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'index': self.index,
            'sizes': [size.serialized for size in self.sizes],
            'category': self.category
        }
