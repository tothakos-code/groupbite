from sqlalchemy import Column, Text, Enum, select
from uuid import UUID
from . import Base, session
import enum
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Size(Base):
    __tablename__ = 'size'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_item.id", ondelete='CASCADE'))
    name: Mapped[str]
    link: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]
    index: Mapped[int]

    menu_item: Mapped["MenuItem"] = relationship(back_populates="sizes")
    orders: Mapped["UserBasket"] = relationship(back_populates="size")

    def __repr__(self):
        return f"Size<{self.id},menu_item_id={self.menu_item_id},name={self.name},price={self.price}>"

    def find_all_by_menu_item(menu_item_id, desc=False):
        stmt = select(Size).where(Size.menu_item_id == menu_item_id)
        if desc:
            stmt.order_by(Size.index.desc())
        else:
            stmt.order_by(Size.index)

        return session.execute(stmt).scalars().all()

    def find_by_id(id):
        stmt = select(Size).where(
            Size.id == id
        )

        return session.execute(stmt).scalars().first()

    def add(size):
        sizes = Size.find_all_by_menu_item(size.menu_item_id, True)
        if not sizes:
            size.index = 0
        else:
            size.index = sizes[0].index + 1
        session.add(size)
        session.commit()

    def update(self, name, price, quantity, index):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.index = index
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'index': self.index,
        }
