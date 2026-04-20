from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.entities.webhook import Webhook, WebhookType


class WebhookRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        """Find all webhooks"""
        stmt = select(Webhook)
        return self.db.execute(stmt).scalars().all()

    def find_by_vendor_id(self, vendor_id: UUID):
        """Find all webhooks for a specific vendor"""
        stmt = select(Webhook).where(Webhook.vendor_id == vendor_id)
        return self.db.execute(stmt).scalars().all()

    def find_active_by_vendor_id(self, vendor_id: UUID):
        """Find all active webhooks for a specific vendor"""
        stmt = select(Webhook).where(Webhook.vendor_id == vendor_id, Webhook.is_active)
        return self.db.execute(stmt).scalars().all()

    def find_all_active(self):
        """Find all active webhooks"""
        stmt = select(Webhook).where(Webhook.is_active)
        return self.db.execute(stmt).scalars().all()

    def find_by_event_type(self, trigger_type: WebhookType):
        """Find all active webhooks that listen to a specific event type"""
        stmt = select(Webhook).where(
            Webhook.is_active, Webhook.trigger_type == trigger_type
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_vendor_and_event(self, vendor_id: UUID, trigger_type: WebhookType):
        """Find active webhooks for a vendor that listen to a specific event"""
        stmt = select(Webhook).where(
            Webhook.vendor_id == vendor_id,
            Webhook.is_active,
            Webhook.trigger_type == trigger_type,
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_id(self, webhook_id: UUID):
        """Find webhook by primary key"""
        stmt = select(Webhook).where(Webhook.id == webhook_id)
        return self.db.execute(stmt).scalars().first()

    def save(self, webhook):
        """Add a new webhook"""
        self.db.add(webhook)
        return webhook

    def update(self, webhook, **kwargs):
        """Update webhook fields"""
        for key, value in kwargs.items():
            if hasattr(webhook, key):
                setattr(webhook, key, value)

        webhook.updated_at = datetime.utcnow()
        return webhook

    def delete(self, webhook):
        """Delete webhook"""
        self.db.delete(webhook)
