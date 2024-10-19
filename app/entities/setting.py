import enum, json
from typing import List
from . import Base, session
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import event, ForeignKey, select, exc
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Setting(Base):
    __tablename__ = "setting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str]
    category: Mapped[str]


    def __repr__(self):
        return f"Setting<id={self.id},key={self.key},value={self.value}>"

    def get_all_settings():
        stmt = select(Setting).order_by(Setting.id)
        return session.execute(stmt).scalars().all()

    def get_all_settings_as_kv():
        stmt = select(Setting).order_by(Setting.id)
        settings = session.execute(stmt).scalars().all()
        return {setting.key: setting.value for setting in settings}

    def get_setting_by_key(key):
        stmt = select(Setting).where(Setting.key == key)
        return session.execute(stmt).scalars().first()

    def get_value_by_key(key):
        stmt = select(Setting).where(Setting.key == key)
        return session.execute(stmt).scalars().first().value

    def update_setting(key, value):
        setting = Setting.get_setting_by_key(key)
        if setting:
            setting.value = value
            session.commit()
            return True
        return False


    @property
    def serialized(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value
        }
