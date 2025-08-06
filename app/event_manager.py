import logging
import threading
import requests

class EventManager:
    def __init__(self):
        self.listeners = {}
        self.webhook_listeners = {}

    def register_listener(self, event, listener):
        logging.debug(str(listener) + " registered for " + event + " event")
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def trigger_event(self, event, data, *args, **kwargs):
        logging.debug(event + " event triggered")
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(data, *args, **kwargs)

    def unregister_listener(self, event, listener):
        """Remove a specific listener from an event"""
        if event in self.listeners:
            try:
                self.listeners[event].remove(listener)
                logging.debug(f"Listener removed from {event} event")
                if not self.listeners[event]:  # Remove empty event list
                    del self.listeners[event]
            except ValueError:
                logging.warning(f"Listener not found for event {event}")

    def register_webhook(self, webhook_id, event_types, webhook_url, message_template=None):
        """Register a webhook as a listener to multiple events"""
        def webhook_listener(data, *args, **kwargs):
            def send_request():
                try:
                    # Use message template if provided, otherwise send raw data
                    payload = data
                    if message_template:
                        # Simple template replacement - you can enhance this
                        payload = {"text": message_template.format(**data) if isinstance(data, dict) else message_template}

                    logging.debug(f"Sending webhook to {webhook_url} for events {event_types}")
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(webhook_url, json=payload, headers=headers, timeout=5)
                    response.raise_for_status()
                    logging.info(f"Webhook {webhook_id} sent successfully")
                except Exception as e:
                    logging.error(f"Webhook call failed for {webhook_url}: {e}")

            threading.Thread(target=send_request).start()

        # Register for all specified event types
        for event_type in event_types:
            self.register_listener(event_type, webhook_listener)

        # Store webhook listener reference for later removal
        self.webhook_listeners[webhook_id] = {
            'listener': webhook_listener,
            'events': event_types
        }

    def unregister_webhook(self, webhook_id):
        """Unregister a webhook from all its events"""
        if webhook_id in self.webhook_listeners:
            webhook_info = self.webhook_listeners[webhook_id]
            listener = webhook_info['listener']
            events = webhook_info['events']

            for event_type in events:
                self.unregister_listener(event_type, listener)

            del self.webhook_listeners[webhook_id]
            logging.debug(f"Webhook {webhook_id} unregistered from events {events}")

event_manager = EventManager()
