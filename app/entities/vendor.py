from enum import Enum as pyenum
from typing import List
from uuid import UUID

from marshmallow import Schema, fields
from sqlalchemy import Boolean, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.vendor_settings_registry import VendorSettingsRegistry

from . import Base


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
