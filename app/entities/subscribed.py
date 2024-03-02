from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base
from marshmallow import Schema, fields
import enum
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .user import User
from .vendor import Vendor

class SubscriptionType(enum.Enum):
    SUB = 'sub'
    VIDEO = 'video'
    SKIP = 'skip'

    def __str__(self):
        return self.value

class Subscribed(Base):
    __tablename__ = 'subscribed'

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"), primary_key=True)
    type: Mapped[SubscriptionType]

    def __repr__(self):
        return "Menu"

    @property
    def serialized(self):
        return {
            'user_id': self.user_id,
            'vendor_id': self.vendor_id,
            'type': str(self.type)
        }

# class SubscribedSchema(Schema):
#     user_id = fields.String()
#     vendor_id = fields.String()
#     type = fields.String()
