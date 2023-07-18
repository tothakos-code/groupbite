from sqlalchemy import Column, Text, Enum

from .entity import Entity, Base
from marshmallow import Schema, fields
import enum

class subscribe_type(enum.Enum):
    none = 'none'
    temp = 'temp'
    full = 'full'

    def __str__(self):
        return self.value

class daily_state_type(enum.Enum):
    none = 'none'
    video = 'video'
    skip = 'skip'
    done = 'done'

    def __str__(self):
        return self.value

class User(Entity, Base):
    __tablename__ = 'users'

    username = Column(Text, unique=True)
    subscribed = Column(Enum(subscribe_type), default=subscribe_type.none)
    daily_state = Column(Enum(daily_state_type), default=subscribe_type.none)

    def __init__(self, username):
        Entity.__init__(self)
        self.username = username

    @property
    def serialized(self):
        return {
            'id': self.id,
            'username': self.username,
            'subscribed': str(self.subscribed),
            'daily_state': str(self.daily_state)
        }

class UserSchema(Schema):
    id = fields.Number()
    username = fields.String()
    subscribed = fields.Enum(subscribe_type)
    daily_state = fields.Enum(daily_state_type)
