from sqlalchemy import Column, Text, Enum, select, exc
from uuid import UUID
from . import Base, session
import enum
import logging
from typing import List
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields

class BaseSizeSchema(Schema):
    menu_item_id = fields.Int(required=True)
    name = fields.Str(required=True)
    link = fields.Str()
    price = fields.Int(required=True)
    quantity = fields.Int(required=True)
    index = fields.Int(required=True)


class UpdateSizeSchema(BaseSizeSchema):
    id = fields.Int(required=True)


class Size(Base):
    __tablename__ = "size"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_item.id", ondelete="CASCADE"))
    name: Mapped[str]
    link: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]
    index: Mapped[int]

    menu_item: Mapped["MenuItem"] = relationship(back_populates="sizes")
    orders: Mapped["UserBasket"] = relationship(back_populates="size", foreign_keys="[UserBasket.size_id]")

    __table_args__ = (
        UniqueConstraint('id', 'menu_item_id', name='uq_size_item'),
    )

    def __repr__(self):
        return f"Size<{self.id},menu_item_id={self.menu_item_id},name={self.name},price={self.price}>"

    def find_all_by_menu_item(menu_item_id, desc=False):
        stmt = select(Size).where(Size.menu_item_id == menu_item_id)
        if desc:
            stmt = stmt.order_by(Size.index.desc())
        else:
            stmt = stmt.order_by(Size.index)

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

        try:
            session.commit()
            session.refresh(size)
            return True, size
        except exc.DataError as e:
            logging.exception("DataError during size add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def update(self, name, price, quantity, index):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.index = index
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during size update")
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
            logging.exception("DataError during size delete")
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
            "price": self.price,
            "quantity": self.quantity,
            "index": self.index,
        }
