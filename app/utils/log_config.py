import logging
from datetime import datetime
from logging.handlers import SMTPHandler
from threading import Thread

from flask import has_request_context, request

from config import Config


class MailHandler(SMTPHandler):
    def emit(self, record):
        """
        Emit a record.
        Format the record and send it to the specified addressees.
        """
        Thread(target=self.send_mail, kwargs={"record": record}).start()

    def send_mail(self, record):
        try:
            import email.utils
            import smtplib
            from email.message import EmailMessage

            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port, timeout=self.timeout)
            msg = EmailMessage()
            msg["From"] = self.fromaddr
            msg["To"] = ",".join(self.toaddrs)
            msg["Subject"] = self.getSubject(record)
            msg["Date"] = email.utils.localtime()
            msg.set_content(self.format(record))
            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            smtp.quit()
        except Exception:
            self.handleError(record)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def log_config():
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "loggers": {
            "root": {
                "level": "ERROR",
                "handlers": ["console", "error_file"],
            },
            "gunicorn.error": {
                "handlers": ["console", "email", "error_file"],
                "level": "ERROR",
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["access_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "handlers": {
            "console": {
                "level": "ERROR",
                "class": "logging.StreamHandler",
                "formatter": "custom_formatter",
                "stream": "ext://sys.stdout",
            },
            "email": {
                "()": "app.utils.log_config.MailHandler",
                "formatter": "custom_formatter",
                "level": "ERROR",
                "mailhost": (Config.MAIL_SERVER, Config.MAIL_SERVER_PORT),
                "fromaddr": Config.DEFAULT_MAIL_SENDER_ADDRESS,
                "toaddrs": Config.ADMIN_MAIL_ADDRESSES,
                "subject": f"{Config.LOG_MAIL_SUBJECT} {datetime.utcnow().date()}",
                "credentials": (
                    Config.DEFAULT_MAIL_SENDER_ADDRESS,
                    Config.DEFAULT_MAIL_SENDER_PASSWORD,
                ),
                "secure": (),
            },
            "error_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "custom_formatter",
                "filename": "gunicorn.error.log",
                "when": "D",
                "interval": 30,
                "backupCount": 1,
            },
            "access_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "access",
                "filename": "gunicorn.access.log",
                "when": "D",
                "interval": 30,
                "backupCount": 1,
            },
        },
        "formatters": {
            "access": {
                "format": "%(message)s",
            },
            "custom_formatter": {
                "()": "app.utils.log_config.RequestFormatter",
                "format": "log_date: [%(asctime)s]\n%(remote_addr)s requested %(url)s %(levelname)s in %(module)s: %(message)s",  # noqa
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
    }
