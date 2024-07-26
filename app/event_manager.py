import logging
class EventManager:
    def __init__(self):
        self.listeners = {}

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

event_manager = EventManager()
