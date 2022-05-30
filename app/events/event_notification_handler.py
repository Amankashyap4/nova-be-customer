import enum

from app.core import NotificationHandler
from app.enums import events_to_publish, fields_to_publish, triggers_to_publish
from app.producer import publish_to_kafka
from config import Config


class EventNotificationHandler(NotificationHandler):
    """
    Event Notification handler

    this class handles event notification. It publishes an Event message to
    the kafka broker which is consumed by the rightful service.

    :param publish: {enum} the event action to publish
    :param data: {object} the details of the event to be sent. based on
    the event details, a record may be altered in the rightful service.
    """

    def __init__(self, publish, data, schema):
        self.publish = publish
        self.data = data
        self.schema = schema()
        self.service_name = Config.APP_NAME

    def send(self):
        if self.validate_event(self.publish, self.data):
            publish_to_kafka(
                topic=self.publish.upper(), value=self.generate_event_data()
            )

    def validate_event(self, event, data):
        if event in events_to_publish():
            event_data = {}
            for field in fields_to_publish(event):
                # get triggers registered for event fields
                event_triggers = triggers_to_publish(event, field)
                field_value = None
                # check if the data has any event field associated with it
                if hasattr(data, field) and isinstance(getattr(data, field), enum.Enum):
                    field_value = getattr(data, field).value
                elif hasattr(data, field):
                    field_value = getattr(data, field)
                # check if data field has any event triggers associated with it
                if self.validate_event_trigger(event_triggers, field_value):
                    event_data[field] = str(field_value)
            return event_data
        return None

    # noinspection PyMethodMayBeStatic
    @staticmethod
    def validate_event_trigger(event_triggers, field_value):
        if event_triggers:
            if field_value in event_triggers:
                return True
            return False
        return True
        # if not event_triggers:
        #     return True
        # # else:
        # #     if field_value in event_triggers:
        # #         return True
        # elif event_triggers and field_value in event_triggers:
        #     return True
        # return False

    def generate_event_data(self):
        return {
            "service_name": self.service_name,
            "details": self.schema.dumps(self.data),
            "meta": {
                "event_action": self.publish,
            },
        }
