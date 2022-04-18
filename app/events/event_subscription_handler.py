import json

from loguru import logger

from app.core.exceptions import AppException
from app.core.service_interfaces import EventHandlerInterface
from app.enums import events_subscribed_to, fields_subscribed_to, triggers_subscribed_to


class EventSubscriptionHandler(EventHandlerInterface):
    def __init__(self, customer_controller, data: dict):
        self.customer_controller = customer_controller
        self.data = data
        self.details = json.loads(data.get("details"))
        self.meta = data.get("meta")
        self.event_action = self.meta.get("event_action")

    def event_handler(self):
        valid_event = self.validate_event(event=self.event_action)
        if valid_event:
            getattr(self, self.meta.get("event_action"))(valid_event)

    def validate_event(self, event):
        if event in events_subscribed_to() and hasattr(self, event):
            event_data = {}
            for field in fields_subscribed_to(event):
                event_triggers = triggers_subscribed_to(event, field)
                if field in self.details.keys():
                    field_value = self.details.get(field)
                    if self.validate_event_trigger(event_triggers, field):
                        event_data[field] = field_value
            return event_data
        return None

    # noinspection PyMethodMayBeStatic
    def validate_event_trigger(self, event_triggers, field_value):
        if not event_triggers:
            return True
        elif event_triggers and field_value in event_triggers:
            return True
        return False

    def first_time_deposit(self, event_data):
        try:
            self.customer_controller.update(
                event_data.get("customer_id"),
                {"level": self.details.get("cylinder_size")},
            )
        except AppException.NotFoundException as exc:
            logger.error(exc.context)
        except AppException.InternalServerError as exc:
            logger.error(exc.context)
