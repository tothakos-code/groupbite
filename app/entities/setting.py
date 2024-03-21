from sqlalchemy import Column, Text, Enum
from uuid import UUID
from . import Base
from marshmallow import Schema, fields
import enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class SettingType(enum.Enum):
    INT = 'int'
    STR = 'str'
    BOOL = 'bool'

    def __str__(self):
        return self.value


class Setting(Base):
    __tablename__ = 'setting'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section: Mapped[str] = mapped_column(default='root')
    key: Mapped[str]
    value: Mapped[str]
    type: Mapped[SettingType]

    def __repr__(self):
        return f"Setting<id={self.id},section={self.section}>"

    @property
    def serialized(self):
        return {
            'id': self.id,
            'section': self.section,
            'key': self.key,
            'value': self.value,
            'type': str(self.type)
        }

# class SettingSchema(Schema):
#     id = fields.Integer()
#     section = fields.String()
#     key = fields.String()
#     value = fields.String()
#     type = fields.Enum(SettingType)
