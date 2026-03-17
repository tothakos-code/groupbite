from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

CURRENT_SCHEMA_VERSION = 1


class Visibility:
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class BaseSetting(ABC):
    key: str
    labelKey: str
    section: str
    visibility: str = Visibility.PUBLIC

    @abstractmethod
    def get_default_value(self) -> Any: ...

    @abstractmethod
    def get_type(self) -> str: ...

    def validate(self, value: Any) -> bool:
        raise NotImplementedError

    def to_registry_dict(self) -> Dict[str, Any]:
        """Schema descriptor — NOT stored per-vendor."""
        return {
            "key": self.key,
            "type": self.get_type(),
            "default": self.get_default_value(),
            "labelKey": self.labelKey,
            "section": self.section,
            "visibility": self.visibility,
        }


@dataclass
class StringSetting(BaseSetting):
    default_value: str = ""
    max_length: Optional[int] = None

    def get_default_value(self) -> str:
        return self.default_value

    def get_type(self) -> str:
        return "STR"

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if self.max_length and len(value) > self.max_length:
            return False
        return True


@dataclass
class TextAreaSetting(BaseSetting):
    default_value: str = ""

    def get_default_value(self) -> str:
        return self.default_value

    def get_type(self) -> str:
        return "STRBOX"

    def validate(self, value: Any) -> bool:
        return isinstance(value, str)


@dataclass
class IntegerSetting(BaseSetting):
    default_value: int = 0
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    def get_default_value(self) -> int:
        return self.default_value

    def get_type(self) -> str:
        return "INT"

    def validate(self, value: Any) -> bool:
        if isinstance(value, str):
            if not value.isdigit():
                return False
            value = int(value)
        if not isinstance(value, int):
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True


@dataclass
class BooleanSetting(BaseSetting):
    default_value: bool = False

    def get_default_value(self) -> bool:
        return self.default_value

    def get_type(self) -> str:
        return "BOOL"

    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)


@dataclass
class ListSetting(BaseSetting):
    default_value: List[Any] = field(default_factory=list)

    def get_default_value(self) -> List[Any]:
        return list(self.default_value)

    def get_type(self) -> str:
        return "LIST"

    def validate(self, value: Any) -> bool:
        return isinstance(value, list)


class VendorSettingsRegistry:
    """
    Single source of truth for all vendor settings.
    """

    _settings: Dict[str, BaseSetting] = {}

    TITLE = StringSetting(
        key="title",
        labelKey="vendor.settings.title",
        section="general",
        visibility=Visibility.PUBLIC,
    )
    LINK = StringSetting(
        key="link",
        labelKey="vendor.settings.link",
        section="general",
        visibility=Visibility.PUBLIC,
    )
    COMMENT_EXAMPLE = StringSetting(
        key="comment_example",
        labelKey="vendor.settings.comment_example",
        section="general",
        visibility=Visibility.PUBLIC,
    )
    TRANSPORT_PRICE = IntegerSetting(
        key="transport_price",
        labelKey="vendor.settings.transport_price",
        section="general",
        visibility=Visibility.PUBLIC,
        default_value=0,
        min_value=0,
    )
    ENABLE_FULL_AUTOMATIC_ORDER = BooleanSetting(
        key="enable_full_automatic_order",
        labelKey="vendor.settings.enable_full_automatic_order",
        section="order-types",
        visibility=Visibility.PUBLIC,
        default_value=False,
    )
    ENABLE_EMAIL_ORDER = BooleanSetting(
        key="enable_email_order",
        labelKey="vendor.settings.enable_email_order",
        section="order-types",
        visibility=Visibility.PUBLIC,
        default_value=False,
    )
    ENABLE_MANUAL_ORDER = BooleanSetting(
        key="enable_manual_order",
        labelKey="vendor.settings.enable_manual_order",
        section="order-types",
        visibility=Visibility.PUBLIC,
        default_value=True,
    )
    SHOW_NOTIFICATION_BUTTON = BooleanSetting(
        key="show_notification_button",
        labelKey="vendor.settings.show_notification_button",
        section="ui",
        visibility=Visibility.PUBLIC,
        default_value=True,
    )
    CLOSED_SCHEDULER_ACTIVE = BooleanSetting(
        key="closed_scheduler_active",
        labelKey="vendor.settings.closed_scheduler_active",
        section="order",
        visibility=Visibility.PRIVATE,
        default_value=False,
    )
    CLOSED_SCHEDULER = StringSetting(
        key="closed_scheduler",
        labelKey="vendor.settings.closed_scheduler",
        section="order",
        visibility=Visibility.PRIVATE,
    )
    CLOSED_SCHEDULER_DAYS = ListSetting(
        key="closed_scheduler_days",
        labelKey="vendor.settings.closed_scheduler_days",
        section="order",
        visibility=Visibility.PRIVATE,
    )
    CLOSURE_SCHEDULER_ACTIVE = BooleanSetting(
        key="closure_scheduler_active",
        labelKey="vendor.settings.closure_scheduler_active",
        section="order",
        visibility=Visibility.PRIVATE,
        default_value=False,
    )
    CLOSURE_SCHEDULER = StringSetting(
        key="closure_scheduler",
        labelKey="vendor.settings.closure_scheduler",
        section="order",
        visibility=Visibility.PRIVATE,
    )
    CLOSURE_SCHEDULER_DAYS = ListSetting(
        key="closure_scheduler_days",
        labelKey="vendor.settings.closure_scheduler_days",
        section="order",
        visibility=Visibility.PRIVATE,
    )
    ORDER_TEXT_TEMPLATE = StringSetting(
        key="order_text_template",
        labelKey="vendor.settings.order_text_template",
        section="order",
        visibility=Visibility.PRIVATE,
        default_value="${quantity}x ${item_name} ${size_name}\\n",
    )
    AUTO_EMAIL_ORDER = BooleanSetting(
        key="auto_email_order",
        labelKey="vendor.settings.auto_email_order",
        section="auto-order",
        visibility=Visibility.PRIVATE,
        default_value=False,
    )
    EMAIL_MIN_USER = IntegerSetting(
        key="email_min_user",
        labelKey="vendor.settings.email_min_user",
        section="auto-order",
        visibility=Visibility.PRIVATE,
        default_value=3,
        min_value=1,
    )
    AUTO_EMAIL_ORDER_TO = ListSetting(
        key="auto_email_order_to",
        labelKey="vendor.settings.auto_email_order_to",
        section="auto-order",
        visibility=Visibility.PRIVATE,
    )
    AUTO_EMAIL_ORDER_CC = ListSetting(
        key="auto_email_order_cc",
        labelKey="vendor.settings.auto_email_order_cc",
        section="auto-order",
        visibility=Visibility.PRIVATE,
    )
    AUTO_EMAIL_SUBJECT = StringSetting(
        key="auto_email_subject",
        labelKey="vendor.settings.auto_email_subject",
        section="auto-order",
        visibility=Visibility.PRIVATE,
        default_value="${vendor_name} rendelés - ${date}",
    )
    AUTO_EMAIL_ORDER_TEMPLATE = TextAreaSetting(
        key="auto_email_order_template",
        labelKey="vendor.settings.auto_email_order_template",
        section="auto-order",
        visibility=Visibility.PRIVATE,
    )
    MENU_SCAN_ACTIVE = BooleanSetting(
        key="menu_scan_active",
        labelKey="vendor.settings.menu_scan_active",
        section="menu-scan",
        visibility=Visibility.PRIVATE,
        default_value=False,
    )
    MENU_SCAN_TIME = StringSetting(
        key="menu_scan_time",
        labelKey="vendor.settings.menu_scan_time",
        section="menu-scan",
        visibility=Visibility.PRIVATE,
        default_value="",
    )
    MENU_SCAN_DAYS = ListSetting(
        key="menu_scan_days",
        labelKey="vendor.settings.menu_scan_days",
        section="menu-scan",
        visibility=Visibility.PRIVATE,
        default_value=[],
    )
    MENU_SCAN_DAYS_AHEAD = IntegerSetting(
        key="menu_scan_days_ahead",
        labelKey="vendor.settings.menu_scan_days_ahead",
        section="menu-scan",
        visibility=Visibility.PRIVATE,
        default_value=1,
        min_value=1,
        max_value=14,
    )
    FAVOURITE_NOTIFICATION_ON_ORDER = BooleanSetting(
        key="favourite_notification_on_order",
        labelKey="vendor.settings.favourite_notification_on_order",
        section="favourite",
        visibility=Visibility.PRIVATE,
        default_value=True,
    )
    FAVOURITE_NOTIFICATION_ACTIVE = BooleanSetting(
        key="favourite_notification_active",
        labelKey="vendor.settings.favourite_notification_active",
        section="favourite",
        visibility=Visibility.PRIVATE,
        default_value=False,
    )
    FAVOURITE_NOTIFICATION_TIME = StringSetting(
        key="favourite_notification_time",
        labelKey="vendor.settings.favourite_notification_time",
        section="favourite",
        visibility=Visibility.PRIVATE,
        default_value="",
    )
    FAVOURITE_NOTIFICATION_DAYS = ListSetting(
        key="favourite_notification_days",
        labelKey="vendor.settings.favourite_notification_days",
        section="favourite",
        visibility=Visibility.PRIVATE,
        default_value=[],
    )

    @classmethod
    def _iter(cls) -> Dict[str, BaseSetting]:
        if not cls._settings:
            cls._settings = {
                v.key: v for k, v in vars(cls).items() if isinstance(v, BaseSetting)
            }
        return cls._settings

    @classmethod
    def get_all(cls) -> Dict[str, BaseSetting]:
        return cls._iter()

    @classmethod
    def get(cls, key: str) -> Optional[BaseSetting]:
        return cls._iter().get(key)

    @classmethod
    def defaults(cls) -> Dict[str, Any]:
        return {k: s.get_default_value() for k, s in cls._iter().items()}

    @classmethod
    def validate_value(cls, key: str, value: Any) -> bool:
        setting = cls.get(key)
        if setting is None:
            return False
        return setting.validate(value)

    @classmethod
    def public_keys(cls) -> List[str]:
        return [k for k, s in cls._iter().items() if s.visibility == Visibility.PUBLIC]
