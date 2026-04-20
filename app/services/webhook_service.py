import logging
import re
from datetime import datetime
from typing import Set
from uuid import UUID

import requests

from app.entities.webhook import Webhook, WebhookType
from app.repositories.webhook_repository import WebhookRepository
from app.scheduler import cancel_task, schedule_task


class WebhookService:
    _active_webhooks: Set[str] = set()

    def __init__(self, event_manager):
        self.event_manager = event_manager

    @staticmethod
    def find_all(db):
        """Find all webhooks"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_all()

    @staticmethod
    def find_by_vendor_id(db, vendor_id: UUID):
        """Find all webhooks for a specific vendor"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_by_vendor_id(vendor_id)

    @staticmethod
    def find_active_by_vendor_id(db, vendor_id: UUID):
        """Find all active webhooks for a specific vendor"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_active_by_vendor_id(vendor_id)

    @staticmethod
    def find_all_active(db):
        """Find all active webhooks"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_all_active()

    @staticmethod
    def find_by_event_type(db, trigger_type: WebhookType):
        """Find all active webhooks that listen to a specific event type"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_by_event_type(trigger_type)

    @staticmethod
    def find_by_vendor_and_event(db, vendor_id: UUID, trigger_type: WebhookType):
        """Find active webhooks for a vendor that listen to a specific event"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_by_vendor_and_event(vendor_id, trigger_type)

    @staticmethod
    def find_by_id(db, webhook_id: UUID):
        """Find webhook by primary key"""
        webhook_repo = WebhookRepository(db)
        return webhook_repo.find_by_id(webhook_id)

    def register_all_webhooks_at_boot(self, db):
        """Register all active webhooks at application startup"""
        logging.info("Registering all active webhooks at boot...")
        webhook_repo = WebhookRepository(db)
        webhooks = webhook_repo.find_all_active()

        for webhook in webhooks:
            self._register_single_webhook(db, webhook)

        logging.info(f"Registered {len(webhooks)} webhooks at boot")

    def _register_single_webhook(self, db, webhook):
        """Register a single webhook based on its type"""
        webhook_id = str(webhook.id)

        if webhook.trigger_type == WebhookType.EVENT:
            # Register for event-based triggers
            if webhook.event_types:
                self.event_manager.register_webhook(
                    webhook_id,
                    [
                        event + "@" + webhook.vendor.name
                        for event in webhook.event_types
                    ],
                    webhook.url,
                    webhook.message_template,
                )
                WebhookService._active_webhooks.add(webhook_id)
                logging.info(
                    f"Event webhook {webhook_id} registered for events: {webhook.event_types}"
                )

        elif webhook.trigger_type == WebhookType.TIME:
            # Register for scheduled triggers
            if webhook.scheduled_time:
                self._schedule_webhook(db, webhook)
                WebhookService._active_webhooks.add(webhook_id)
                logging.info(
                    f"Scheduled webhook {webhook_id} registered for time: {webhook.scheduled_time}"
                )

    def _schedule_webhook(self, db, webhook):
        """Schedule a webhook for time-based execution"""
        try:
            hour, minute = map(int, webhook.scheduled_time.split(":"))
            webhook_id = str(webhook.id)

            def webhook_task():
                data = {
                    "webhook_id": webhook_id,
                    "vendor_id": str(webhook.vendor_id),
                    "executed_at": datetime.utcnow().isoformat(),
                    "trigger_type": "scheduled",
                }

                try:
                    payload = data
                    if webhook.message_template:
                        payload = {"text": webhook.message_template.format(**data)}

                    headers = {"Content-Type": "application/json"}
                    response = requests.post(
                        webhook.url, json=payload, headers=headers, timeout=5
                    )
                    response.raise_for_status()

                    webhook.last_executed = datetime.utcnow()
                    db.commit()

                    logging.info(
                        f"Scheduled webhook {webhook_id} executed successfully"
                    )
                except Exception as e:
                    logging.error(f"Scheduled webhook {webhook_id} failed: {e}")

            # Schedule the task
            schedule_task(
                webhook_id, hour, minute, webhook_task, webhook.scheduled_days
            )

        except ValueError as e:
            logging.error(
                f"Invalid scheduled_time format for webhook {webhook.id}: {e}"
            )

    def activate_webhook(self, db, webhook_id):
        """Activate a webhook"""
        webhook_repo = WebhookRepository(db)
        webhook = webhook_repo.find_by_id(webhook_id)
        if webhook:
            webhook.is_active = True
            webhook.updated_at = datetime.utcnow()
            db.commit()

            self._register_single_webhook(db, webhook)
            logging.info(f"Webhook {webhook_id} activated")

    def deactivate_webhook(self, db, webhook_id):
        """Deactivate a webhook"""
        webhook_repo = WebhookRepository(db)
        webhook = webhook_repo.find_by_id(webhook_id)
        if webhook:
            webhook.is_active = False
            webhook.updated_at = datetime.utcnow()
            db.commit()

            self.unregister_webhook(webhook_id)
            logging.info(f"Webhook {webhook_id} deactivated")

    def unregister_webhook(self, webhook_id):
        """Unregister a webhook from both events and scheduled tasks"""
        webhook_id_str = str(webhook_id)

        self.event_manager.unregister_webhook(webhook_id_str)

        cancel_task(webhook_id_str)

        WebhookService._active_webhooks.discard(webhook_id_str)

        logging.info(f"Webhook {webhook_id} fully unregistered")

    def get_active_webhooks(self):
        """Get list of currently active webhook IDs"""
        return list(WebhookService._active_webhooks)

    def add_webhook(self, db, data):
        webhook_repo = WebhookRepository(db)
        webhook = webhook_repo.save(
            Webhook(
                vendor_id=data["vendor_id"],
                url=data["url"],
                message_template=data["message_template"],
                trigger_type=WebhookType(data["trigger_type"]),
                scheduled_time=data["scheduled_time"],
                event_types=data["event_types"],
            )
        )
        return webhook

    def update_webhook(self, db, webhook, data):
        """Update webhook fields"""
        webhook_repo = WebhookRepository(db)
        self.validate_update_data(data)
        webhook_repo.update(
            webhook,
            url=data["url"],
            message_template=data["message_template"],
            trigger_type=WebhookType(data["trigger_type"]),
            scheduled_time=data["scheduled_time"],
            scheduled_days=data["scheduled_days"],
            event_types=data["event_types"],
            is_active=data["is_active"],
        )
        webhook_repo = WebhookRepository(db)
        if str(webhook.id) in WebhookService._active_webhooks:
            self.unregister_webhook(webhook.id)

        if webhook and webhook.is_active:
            self._register_single_webhook(db, webhook)

    def delete_webhook(self, db, webhook):
        """Delete webhook"""
        webhook_repo = WebhookRepository(db)
        self.unregister_webhook(webhook.id)
        webhook_repo.delete(webhook)

    @staticmethod
    def validate_update_data(data):
        """Validate webhook update data"""
        if "url" in data:
            url = data["url"]
            if not url or not url.strip():
                raise Exception("URL megadása kötelező")

            url_pattern = re.compile(r"^https?://.+")
            if not url_pattern.match(url):
                raise Exception("Érvényes URL-t adjon meg (http:// vagy https://)")

        trigger_type = data.get("trigger_type")
        if trigger_type == WebhookType.TIME:
            scheduled_time = data.get("scheduled_time")
            scheduled_days = data.get("scheduled_days")
            if not scheduled_time:
                raise Exception("Időpont megadása kötelező")

            time_pattern = re.compile(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
            if not time_pattern.match(scheduled_time):
                raise Exception("Érvénytelen időformátum. Érvényes formátum: HH:MM")

            if scheduled_days:
                if not isinstance(scheduled_days, list):
                    raise Exception(
                        "A 'scheduled_days' mezőnek listának kell lennie (pl. ['mon','tue','wed'])."
                    )
                else:
                    clean_days = []
                    for d in scheduled_days:
                        if isinstance(d, str):
                            day = d.strip().lower()
                            if (
                                len(day) == 3
                                and day
                                in {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
                                and day not in clean_days
                            ):
                                clean_days.append(day)
                    data["scheduled_days"] = clean_days

    @staticmethod
    def send_to_google_chat(webhook_url, message):
        import requests

        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

    def test_webhook(self, webhook_data):
        self.validate_update_data(webhook_data)
        self.send_to_google_chat(webhook_data["url"], webhook_data["message_template"])
        logging.info("Test Webhook message sent!")
