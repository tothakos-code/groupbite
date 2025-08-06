from sqlalchemy import ForeignKey, select, exc, Text, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields
from . import Base, session

from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
import logging
import enum
import re

class BaseWebhookSchema(Schema):
    vendor_id = fields.Str(required=True)
    url = fields.Str(required=True)
    message_template = fields.Str(required=True)
    trigger_type = fields.Str(required=True)
    scheduled_time = fields.Str(required=False)
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

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid4)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    message_template: Mapped[str] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[WebhookType] = mapped_column(nullable=False)
    scheduled_time: Mapped[str] = mapped_column(Text, nullable=True)
    event_types: Mapped[List[str]] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    last_executed: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


    vendor: Mapped["Vendor"] = relationship()

    @staticmethod
    def find_all():
        """Find all webhooks"""
        stmt = select(Webhook)
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_by_vendor_id(vendor_id: UUID):
        """Find all webhooks for a specific vendor"""
        stmt = select(Webhook).where(Webhook.vendor_id == vendor_id)
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_active_by_vendor_id(vendor_id: UUID):
        """Find all active webhooks for a specific vendor"""
        stmt = select(Webhook).where(
            Webhook.vendor_id == vendor_id,
            Webhook.is_active == True
        )
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_all_active():
        """Find all active webhooks"""
        stmt = select(Webhook).where(
            Webhook.is_active == True
        )
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_by_event_type(trigger_type: WebhookType):
        """Find all active webhooks that listen to a specific event type"""
        stmt = select(Webhook).where(
            Webhook.is_active == True,
            Webhook.trigger_type == trigger_type
        )
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_by_vendor_and_event(vendor_id: UUID, trigger_type: WebhookType):
        """Find active webhooks for a vendor that listen to a specific event"""
        stmt = select(Webhook).where(
            Webhook.vendor_id == vendor_id,
            Webhook.is_active == True,
            Webhook.trigger_type == trigger_type
        )
        return session.execute(stmt).scalars().all()

    @staticmethod
    def find_by_id(webhook_id: UUID):
        """Find webhook by primary key"""
        stmt = select(Webhook).where(Webhook.id == webhook_id)
        return session.execute(stmt).scalars().first()

    @staticmethod
    def add(webhook):
        """Add a new webhook"""
        session.add(webhook)
        try:
            session.commit()
            session.refresh(webhook)
            return True, webhook
        except exc.DataError as e:
            logging.exception("DataError during webhook add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False, None

    def update(self, **kwargs):
        """Update webhook fields"""
        try:
            Webhook.validate_update_data(kwargs)

            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            self.updated_at = datetime.utcnow()

            session.commit()
            from app.services.webhook_service import webhook_service
            webhook_service.update_webhook(self.id)
            return True
        except exc.DataError as e:
            logging.exception("DataError during webhook update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    def delete(self):
        """Delete webhook"""
        from app.services.webhook_service import webhook_service
        webhook_service.unregister_webhook(self.id)
        session.delete(self)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during webhook delete")
            session.rollback()
            return False
        except exc.IntegrityError as e:
            logging.exception("IntegrityError during webhook delete")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    @staticmethod
    def validate_update_data(data):
        """Validate webhook update data"""
        # URL validation
        if 'url' in data:
            url = data['url']
            if not url or not url.strip():
                raise Exception("URL megadása kötelező")

            # URL format validation
            url_pattern = re.compile(r'^https?://.+')
            if not url_pattern.match(url):
                raise Exception("Érvényes URL-t adjon meg (http:// vagy https://)")

        # Trigger type validation
        trigger_type = data.get('trigger_type')
        if trigger_type == WebhookType.TIME:
            # Time validation for scheduled webhooks
            logging.info("scheduled_time")
            scheduled_time = data.get('scheduled_time')
            logging.info("scheduled_time")
            logging.info(scheduled_time)
            if not scheduled_time:
                raise Exception("Időpont megadása kötelező")

            # Time format validation (HH:MM)
            time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
            if not time_pattern.match(scheduled_time):
                raise Exception("Érvénytelen időformátum. Érvényes formátum: HH:MM")

    def send_to_google_chat(webhook_url, message):
        import requests
        payload = {
            "text": message
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")
        else:
            logging.info("Test Webhook message sent!")


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
            "event_types": self.event_types,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
