from sqlalchemy import Column, String, Integer, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from .entity import Entity, Base
from marshmallow import Schema, fields

class Menu(Entity, Base):
    __tablename__ = 'menu'

    menu_date = Column(DateTime, default=func.current_date())
    menu = Column(ARRAY(JSONB))

    def __init__(self, menu):
        Entity.__init__(self)
        self.menu = menu

class MenuSchema(Schema):
    id = fields.Number()
    menu_date = fields.DateTime()
    menu = fields.List(fields.Dict())
