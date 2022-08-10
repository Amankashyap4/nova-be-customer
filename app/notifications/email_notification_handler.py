from app.core import NotificationHandler
from app.producer import publish_to_kafka
from config import Config


class EmailNotificationHandler(NotificationHandler):
    """
    Email Notification handler

    this class handles email notification. It publishes a NOTIFICATION message to
    the kafka broker which is consumed by the notification service.

    :param recipients: {list} the recipient(s) email address(es)
    :param details: {dict} placeholders to be substituted by the notification service
    :param meta: {dict} the metadata of the notification to be sent. based on the
    specified, the message may be modified by the notification service.
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

        publish_to_kafka("EMAIL_NOTIFICATION", data)
