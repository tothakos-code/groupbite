from app.entities.webhook import Webhook, WebhookType
from app.entities import session
from app.event_manager import event_manager
from app.scheduler import schedule_task, cancel_task
from datetime import datetime
import logging
import requests

class WebhookService:
    def __init__(self, event_manager, session):
        self.event_manager = event_manager
        self.session = session
        self.active_webhooks: Set[str] = set()  # Track active webhook IDs

    def register_all_webhooks_at_boot(self):
        """Register all active webhooks at application startup"""
        logging.info("Registering all active webhooks at boot...")

        webhooks = Webhook.find_all_active()

        for webhook in webhooks:
            self._register_single_webhook(webhook)

        logging.info(f"Registered {len(webhooks)} webhooks at boot")

    def _register_single_webhook(self, webhook):
        """Register a single webhook based on its type"""
        webhook_id = str(webhook.id)

        if webhook.trigger_type == WebhookType.EVENT:
            # Register for event-based triggers
            if webhook.event_types:
                self.event_manager.register_webhook(
                    webhook_id,
                    [event + "@" + webhook.vendor.name for event in webhook.event_types],
                    webhook.url,
                    webhook.message_template
                )
                self.active_webhooks.add(webhook_id)
                logging.info(f"Event webhook {webhook_id} registered for events: {webhook.event_types}")

        elif webhook.trigger_type == WebhookType.TIME:
            # Register for scheduled triggers
            if webhook.scheduled_time:
                self._schedule_webhook(webhook)
                self.active_webhooks.add(webhook_id)
                logging.info(f"Scheduled webhook {webhook_id} registered for time: {webhook.scheduled_time}")

    def _schedule_webhook(self, webhook):
        """Schedule a webhook for time-based execution"""
        try:
            # Parse scheduled_time (assuming format "HH:MM")
            hour, minute = map(int, webhook.scheduled_time.split(':'))
            webhook_id = str(webhook.id)

            def webhook_task():
                # Create webhook data
                data = {
                    "webhook_id": webhook_id,
                    "vendor_id": str(webhook.vendor_id),
                    "executed_at": datetime.utcnow().isoformat(),
                    "trigger_type": "scheduled"
                }

                # Send webhook
                try:
                    payload = data
                    if webhook.message_template:
                        payload = {"text": webhook.message_template.format(**data)}

                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(webhook.url, json=payload, headers=headers, timeout=5)
                    response.raise_for_status()

                    # Update last_executed timestamp
                    webhook.last_executed = datetime.utcnow()
                    self.session.commit()

                    logging.info(f"Scheduled webhook {webhook_id} executed successfully")
                except Exception as e:
                    logging.error(f"Scheduled webhook {webhook_id} failed: {e}")

            # Schedule the task
            schedule_task(webhook_id, hour, minute, webhook_task)

        except ValueError as e:
            logging.error(f"Invalid scheduled_time format for webhook {webhook.id}: {e}")

    def update_webhook(self, webhook_id):
        """Handle webhook updates - unregister old, register new"""
        webhook_id_str = str(webhook_id)

        # Unregister existing webhook
        if webhook_id_str in self.active_webhooks:
            self.unregister_webhook(webhook_id)

        # Get updated webhook from database
        webhook = Webhook.find_by_id(webhook_id)
        if webhook and webhook.is_active:
            self._register_single_webhook(webhook)

    def activate_webhook(self, webhook_id):
        """Activate a webhook"""
        webhook = Webhook.find_by_id(webhook_id)
        if webhook:
            webhook.is_active = True
            webhook.updated_at = datetime.utcnow()
            self.session.commit()

            self._register_single_webhook(webhook)
            logging.info(f"Webhook {webhook_id} activated")

    def deactivate_webhook(self, webhook_id):
        """Deactivate a webhook"""
        webhook = Webhook.find_by_id(webhook_id)
        if webhook:
            webhook.is_active = False
            webhook.updated_at = datetime.utcnow()
            self.session.commit()

            self.unregister_webhook(webhook_id)
            logging.info(f"Webhook {webhook_id} deactivated")

    def unregister_webhook(self, webhook_id):
        """Unregister a webhook from both events and scheduled tasks"""
        webhook_id_str = str(webhook_id)

        # Unregister from event manager
        self.event_manager.unregister_webhook(webhook_id_str)

        # Cancel scheduled task if exists
        cancel_task(webhook_id_str)

        # Remove from active webhooks
        self.active_webhooks.discard(webhook_id_str)

        logging.info(f"Webhook {webhook_id} fully unregistered")

    def get_active_webhooks(self):
        """Get list of currently active webhook IDs"""
        return list(self.active_webhooks)


webhook_service = WebhookService(event_manager, session)
