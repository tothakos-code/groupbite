import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from marshmallow import Schema, fields
from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BaseWebhookSchema(Schema):
    vendor_id = fields.Str(required=True)
    url = fields.Str(required=True)
    message_template = fields.Str(required=True)
    trigger_type = fields.Str(required=True)
    scheduled_time = fields.Str(required=False)
    scheduled_days = fields.List(fields.Str(), required=False, load_default=None)
    event_types = fields.List(fields.Str(), required=False)


class UpdateWebhookSchema(BaseWebhookSchema):
    id = fields.Str(required=True)
    is_active = fields.Bool()
    last_executed = fields.Str(required=False, allow_none=True)
    created_at = fields.Str(required=False, allow_none=True)
    updated_at = fields.Str(required=False, allow_none=True)


class WebhookType(enum.Enum):
    TIME = "time"
    EVENT = "event"

    def __str__(self):
        return self.value


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, nullable=False, default=uuid4
    )
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    message_template: Mapped[str] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[WebhookType] = mapped_column(nullable=False)
    scheduled_time: Mapped[str] = mapped_column(Text, nullable=True)
    scheduled_days: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    event_types: Mapped[List[str]] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    last_executed: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    vendor: Mapped["Vendor"] = relationship()

    @property
    def serialized(self):
        """Serialize webhook for JSON response"""
        return {
            "id": str(self.id),
            "vendor_id": str(self.vendor_id),
            "url": self.url,
            "message_template": self.message_template,
            "is_active": self.is_active,
            "trigger_type": str(self.trigger_type),
            "scheduled_time": self.scheduled_time,
            "scheduled_days": self.scheduled_days,
            "event_types": self.event_types,
            "last_executed": self.last_executed.isoformat()
            if self.last_executed
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
