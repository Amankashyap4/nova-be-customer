from app.definitions import NotificationHandler
from app.producer import publish_to_kafka


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
