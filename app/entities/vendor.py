from enum import Enum as pyenum
from typing import List, Optional
from uuid import UUID

from marshmallow import Schema, fields, validate
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.vendor_settings_registry import CURRENT_SCHEMA_VERSION, VendorSettingsRegistry

from . import Base


class BaseVendorSchema(Schema):
    name = fields.Str(required=True)
    active = fields.Bool(load_default=False)
    menu_type = fields.Str(
        load_default="fixed_menu",
        validate=validate.OneOf(["daily_menu", "fixed_menu", "own_inventory"]),
    )
    plugin_id = fields.Str(load_default=None, allow_none=True)
    settings = fields.Dict(load_default={})


class MenuType(pyenum):
    DAILY_MENU = "daily_menu"
    FIXED_MENU = "fixed_menu"
    OWN_INVENTORY = "own_inventory"

    def __str__(self):
        return self.value


class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    menu_type: Mapped[MenuType] = mapped_column(default=MenuType.FIXED_MENU)
    plugin_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB)

    orders: Mapped[List["Order"]] = relationship(back_populates="vendor")

    def __repr__(self):
        return f"Vendor<id={self.id},name={self.name},menu_type={str(self.menu_type)}>"

    def _validate_settings(self):
        if not isinstance(self.settings, dict):
            self.settings = {}
        blob = self.settings
        blob.setdefault("schemaVersion", CURRENT_SCHEMA_VERSION)
        blob.setdefault("core", {})
        blob.setdefault("plugins", {})
        defaults = VendorSettingsRegistry.defaults()
        for key, default_value in defaults.items():
            blob["core"].setdefault(key, default_value)

    @property
    def serialized(self):
        from app.utils.vendor_settings import load_vendor_settings

        return {
            "id": str(self.id),
            "name": self.name,
            "active": self.active,
            "menu_type": str(self.menu_type),
            "plugin_id": self.plugin_id,
            "settings": load_vendor_settings(self),
        }

    @property
    def public_serialized(self):
        from app.utils.vendor_settings import public_settings

        return {
            "id": str(self.id),
            "name": self.name,
            "active": self.active,
            "menu_type": str(self.menu_type),
            "plugin_id": self.plugin_id,
            "settings": public_settings(self),
        }
