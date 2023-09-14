from sqlalchemy import Column, Enum, DateTime, JSON, func, Sequence, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum, json
from .entity import Entity, Base
from marshmallow import Schema, fields

class order_state_type(enum.Enum):
    collect = 'collect'
    order = 'order'
    closed = 'closed'

    def __str__(self):
        return self.value


class Order(Entity, Base):
    __tablename__ = 'orders'

    id = Column(Integer, Sequence('orders_id_seq'), primary_key=True, autoincrement=True)
    order_date = Column(DateTime, default=func.current_date())
    order_state = Column(Enum(order_state_type), default=order_state_type.collect)
    basket = Column(JSONB)

    def __init__(self, order_date, basket):
        Entity.__init__(self)
        self.order_date = order_date
        self.basket = basket

    @property
    def serialized(self):
        return {
            'id': self.id,
            'order_date': self.order_date,
            'order_state': str(self.order_state),
            'basket': json.dumps(self.basket)
        }

class OrderSchema(Schema):
    id = fields.Number()
    order_date = fields.DateTime()
    order_state = fields.Enum(order_state_type)
    basket = fields.Dict()
