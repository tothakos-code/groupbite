import enum, json
from typing import List
from . import Base, session
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import event, ForeignKey, select, exc
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

import base64
from cryptography.fernet import Fernet
import logging
from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

FERNET_KEY = getenv('FERNET_KEY')
cipher = Fernet(str.encode(FERNET_KEY))

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

    def encrypt_value(value=None):
        if value is not None:
            encrypted_value = cipher.encrypt(value.encode())
            return base64.b64encode(encrypted_value).decode()
        return value

    def decrypt_value(value=None):
        if value is not None:
            decrypted_value = cipher.decrypt(base64.b64decode(value))
            return decrypted_value.decode()
        return value

    def update_setting(key, value):
        setting = Setting.get_setting_by_key(key)
        if setting:
            if setting.key == "smtp_password":
                if value != setting.value:
                    setting.value = Setting.encrypt_value(value)
            if setting.key == "smtp_address" and value == "":
                from app.entities.vendor import Vendor
                from app.scheduler import cancel_task
                vendors = Vendor.find_all()
                for vendor in vendors:
                    vendor.update_setting("auto_email_order", False)
                    cancel_task(str(vendor.id) + "-email-order")
                setting.value = value
            else:
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
