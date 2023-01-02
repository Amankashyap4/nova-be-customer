from datetime import datetime

from app.enums import AccountStatusEnum


class LoginAttemptTestData:
    @property
    def existing_attempt(self):
        return {
            "phone_number": "0507898766",
            "request_ip_address": "192.168.7.8",
            "failed_login_attempts": 3,
            "failed_login_time": datetime.now(),
            "status": AccountStatusEnum.active,
            "expires_in": datetime.now(),
        }
