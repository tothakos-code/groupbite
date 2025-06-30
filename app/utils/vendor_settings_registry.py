from typing import List, Dict, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Setting type definitions
@dataclass
class BaseSetting:
    name: str
    section: str

    @abstractmethod
    def get_default_value(self) -> Any:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.get_type(),
            "value": self.get_default_value(),
            "section": self.section
        }

@dataclass
class StringSetting(BaseSetting):
    default_value: str = ""

    def get_default_value(self) -> str:
        return self.default_value

    def get_type(self) -> str:
        return "STR"

@dataclass
class TextAreaSetting(BaseSetting):
    default_value: str = ""

    def get_default_value(self) -> str:
        return self.default_value

    def get_type(self) -> str:
        return "STRBOX"

@dataclass
class IntegerSetting(BaseSetting):
    default_value: int = 0

    def get_default_value(self) -> int:
        return self.default_value

    def get_type(self) -> str:
        return "INT"

@dataclass
class BooleanSetting(BaseSetting):
    default_value: bool = False

    def get_default_value(self) -> bool:
        return self.default_value

    def get_type(self) -> str:
        return "BOOL"

@dataclass
class ListSetting(BaseSetting):
    default_value: List[Any] = field(default_factory=list)

    def get_default_value(self) -> List[Any]:
        return self.default_value.copy()

    def get_type(self) -> str:
        return "LIST"

# Vendor settings registry
class VendorSettingsRegistry:
    """Registry for all vendor settings with type safety and validation"""

    # General Settings
    TITLE = StringSetting(
        name="Cím",
        section="general"
    )

    LINK = StringSetting(
        name="Eredeti oldal elérhetősége",
        section="general"
    )

    COMMENT_EXAMPLE = StringSetting(
        name="Rendelés megjegyzés példa",
        section="general"
    )

    TRANSPORT_PRICE = IntegerSetting(
        name="Szállítási díj",
        section="general",
        default_value=0
    )

    # Order Type Controls (New)
    ENABLE_FULL_AUTOMATIC_ORDER = BooleanSetting(
        name="Teljes automatikus rendelés engedélyezése",
        section="order-types",
        default_value=False
    )

    ENABLE_EMAIL_ORDER = BooleanSetting(
        name="Email rendelés engedélyezése",
        section="order-types",
        default_value=False
    )

    ENABLE_MANUAL_ORDER = BooleanSetting(
        name="Manuális rendelés engedélyezése",
        section="order-types",
        default_value=True
    )

    # UI Settings (New)
    SHOW_NOTIFICATION_BUTTON = BooleanSetting(
        name="Értesítési gomb megjelenítése",
        section="ui",
        default_value=True
    )

    # Order Process Settings
    CLOSED_SCHEDULER_ACTIVE = BooleanSetting(
        name="Automatikus lezárás aktív",
        section="order",
        default_value=False
    )

    CLOSED_SCHEDULER = StringSetting(
        name="Rendelés automatikus lezárása (formátum: hh:mm)",
        section="order"
    )

    CLOSURE_SCHEDULER_ACTIVE = BooleanSetting(
        name="Lezárás figyelmeztetés aktív",
        section="order",
        default_value=False
    )

    CLOSURE_SCHEDULER = StringSetting(
        name="Rendelés automatikus zárás figyelmeztetés (formátum: hh:mm)",
        section="order"
    )

    ORDER_TEXT_TEMPLATE = StringSetting(
        name="Rendelés szöveg sor minta",
        section="order",
        default_value="${quantity}x ${item_name} ${size_name}\\n"
    )

    # Auto Email Settings
    AUTO_EMAIL_ORDER = BooleanSetting(
        name="Automatikus email rendelés",
        section="auto-order",
        default_value=False
    )

    EMAIL_ORDER_SCHEDULER = StringSetting(
        name="Rendelés automatikus email küldése (formátum: hh:mm)",
        section="auto-order"
    )

    EMAIL_MIN_USER = IntegerSetting(
        name="Automatikus rendelés minimum részvevő felhasználó",
        section="auto-order",
        default_value=3
    )

    AUTO_EMAIL_ORDER_TO = ListSetting(
        name="Automatikus rendelés címzett",
        section="auto-order"
    )

    AUTO_EMAIL_ORDER_CC = ListSetting(
        name="Automatikus rendelés másolatot kap",
        section="auto-order"
    )

    AUTO_EMAIL_SUBJECT = StringSetting(
        name="Automatikus rendelés email tárgy",
        section="auto-order",
        default_value="${vendor_name} rendelés - ${date}"
    )

    AUTO_EMAIL_ORDER_TEMPLATE = TextAreaSetting(
        name="Automatikus rendelés üzenet sablon",
        section="auto-order"
    )

    @classmethod
    def get_all_settings(cls) -> Dict[str, BaseSetting]:
        """Get all settings as a dictionary"""
        settings = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, BaseSetting):
                # Use snake_case key for consistency
                key = attr_name.lower()
                settings[key] = attr
        return settings

    @classmethod
    def get_default_settings_dict(cls) -> Dict[str, Dict[str, Any]]:
        """Get all settings as the legacy dictionary format"""
        settings = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, BaseSetting):
                key = attr_name.lower()
                settings[key] = attr.to_dict()
        return settings

    @classmethod
    def validate_setting(cls, key: str, value: Any) -> bool:
        """Validate a setting value against its type"""
        settings = cls.get_all_settings()
        if key not in settings:
            return False

        setting = settings[key]
        expected_type = type(setting.get_default_value())

        # Special handling for different types
        if isinstance(setting, StringSetting) or isinstance(setting, TextAreaSetting):
            return isinstance(value, str)
        elif isinstance(setting, IntegerSetting):
            return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
        elif isinstance(setting, BooleanSetting):
            return isinstance(value, bool)
        elif isinstance(setting, ListSetting):
            return isinstance(value, list)

        return True

    @classmethod
    def get_setting_by_key(cls, key: str) -> BaseSetting:
        """Get a setting definition by key"""
        settings = cls.get_all_settings()
        return settings.get(key)
