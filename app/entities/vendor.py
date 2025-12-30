import logging
import re
from datetime import date
from enum import Enum as pyenum
from typing import Any, List
from uuid import UUID, uuid4

from marshmallow import Schema, fields
from sqlalchemy import Boolean, event, exc, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified

from app.entities.setting import Setting
from app.utils.vendor_settings_registry import VendorSettingsRegistry

from . import Base, session
from .notification import NotificationType

non_mached = re.compile("\$\{.*?\}")


class BaseVendorSchema(Schema):
    name = fields.Str(required=True)
    active = fields.Bool()
    settings = fields.Dict(required=True)


class VendorType(pyenum):
    PLUGIN = "plugin"
    BASIC = "basic"

    def __str__(self):
        return self.value


class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    type: Mapped[VendorType] = mapped_column(default=VendorType.BASIC)
    settings: Mapped[dict] = mapped_column(JSONB)

    orders: Mapped[List["Order"]] = relationship(back_populates="vendor")

    def __repr__(self):
        return f"Vendor<id={self.id},name={self.name},type={str(self.type)}>"

    def _validate_settings(self):
        """Ensure all required settings exist with proper defaults"""
        if not isinstance(self.settings, dict):
            self.settings = {}

        # Get default settings from registry
        default_settings = VendorSettingsRegistry.get_default_settings_dict()

        # Merge with existing settings, keeping existing values
        for key, default_setting in default_settings.items():
            if key not in self.settings:
                self.settings[key] = default_setting
            else:
                # Ensure the structure is correct
                existing = self.settings[key]
                if not isinstance(existing, dict):
                    # Reset to default if structure is wrong
                    self.settings[key] = default_setting
                else:
                    # Ensure all required keys exist
                    for required_key in ["name", "type", "value", "section"]:
                        if required_key not in existing:
                            if required_key == "value":
                                existing[required_key] = default_setting[required_key]
                            else:
                                existing[required_key] = default_setting[required_key]

    def find_all():
        stmt = select(Vendor).order_by(Vendor.name)
        return session.execute(stmt).scalars().all()

    def find_all_by_type(type: VendorType):
        stmt = select(Vendor).where(Vendor.type == type)
        return session.execute(stmt).scalars().all()

    def find_all_active():
        stmt = select(Vendor).where(Vendor.active == True)
        return session.execute(stmt).scalars().all()

    def find_by_id(id):
        stmt = select(Vendor).where(Vendor.id == id)
        return session.execute(stmt).scalars().first()

    def get_setting_value(self, key: str, default=None):
        """Safely get a setting value with fallback to default"""
        try:
            if key in self.settings and "value" in self.settings[key]:
                return self.settings[key]["value"]
        except (KeyError, TypeError):
            pass

        # Fallback to registry default
        setting_def = VendorSettingsRegistry.get_setting_by_key(key)
        if setting_def:
            return setting_def.get_default_value()

        return default

    def set_setting_value(self, key: str, value: Any) -> bool:
        """Safely set a setting value with validation"""
        if not VendorSettingsRegistry.validate_setting(key, value):
            return False

        if key not in self.settings:
            # Create from default if doesn't exist
            setting_def = VendorSettingsRegistry.get_setting_by_key(key)
            if setting_def:
                self.settings[key] = setting_def.to_dict()
            else:
                return False

        self.settings[key]["value"] = value
        flag_modified(self, "settings")
        return True

    def update_setting(self, key, value):
        """Update a single setting value"""
        if not VendorSettingsRegistry.validate_setting(key, value):
            return False

        if not self.set_setting_value(key, value):
            return False

        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during vendor update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "active": self.active,
            "type": str(self.type),
            "settings": self.settings,
        }


def validate_before_save(mapper, connection, target):
    target._validate_settings()


event.listen(Vendor, "before_insert", validate_before_save)
event.listen(Vendor, "before_update", validate_before_save)
