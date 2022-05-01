from app.core import NotificationHandler
from app.producer import publish_to_kafka
from config import Config


class SMSNotificationHandler(NotificationHandler):
    """
    SMS Notification handler

    this class handles sms notification. It publishes a NOTIFICATION message to
    the kafka broker which is consumed by the notification service.

    :param recipient: {string} the recipient phone number
    :param message: {string} the message you want to send
    :param sms_type: {string} the type of message you want to send. based on
    the sms type specified, the message may be modified by the notification service.
    Check out https://github.com/theQuantumGroup/nova-be-notification for more info
    """

    def __init__(self, recipients: list, details: dict, meta: dict):
        self.recipients = recipients
        self.details = details
        self.meta = meta
        self.service_name = Config.APP_NAME

    def send(self):
        data = {
            "service_name": self.service_name,
            "meta": {"entity": "customer", **self.meta},
            "details": self.details,
            "recipients": self.recipients,
        }

        publish_to_kafka("SMS_NOTIFICATION", data)
