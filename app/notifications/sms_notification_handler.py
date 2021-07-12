from app.definitions import NotificationHandler
from app.producer import publish_to_kafka


class SMSNotificationHandler(NotificationHandler):
    def __init__(self, recipient, message, sms_type):
        self.recipient = recipient
        self.message = message
        self.sms_type = sms_type

    def send(self):
        data = {
            "sms_type": self.sms_type,
            "message": self.message,
            "recipient": self.recipient,
        }

        publish_to_kafka("SMS_NOTIFICATION", data)
