import json

from loguru import logger

from app.core.service_interfaces import EventHandlerInterface

from .event_data_structure import ServiceEventSubscription


class EventSubscriptionHandler(EventHandlerInterface):
    def __init__(self, customer_controller):
        self.customer_controller = customer_controller
        self.data = None
        self.details = None
        self.meta = None
        self.event_action = None

    def event_handler(self, event_data: dict):
        self.data = event_data
        self.details = json.loads(event_data.get("details"))
        self.meta = event_data.get("meta")
        self.event_action = self.meta.get("event_action")

        valid_event_data = self.validate_event(self.details)
        if valid_event_data:
            getattr(self, self.event_action, self.unhandled_event)()
        else:
            logger.error(
                f"event {self.event_action} with data {self.data} did not pass data validation"  # noqa
            )

    def validate_event(self, data):
        validator = ServiceEventSubscription[self.event_action].value
        for field in validator:
            if field not in data:
                return None
            if isinstance(validator.get(field), list):
                if data.get(field) not in validator.get(field):
                    return None
        return data

    def unhandled_event(self):
        logger.error(f"event {self.event_action} with data {self.data} is unhandled")

    def first_time_deposit(self):
        self.customer_controller.first_time_deposit(self.details)
