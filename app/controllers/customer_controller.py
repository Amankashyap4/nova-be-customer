import random
import secrets
import pytz
from datetime import datetime, timedelta

from core import Result
from core.exceptions import AppException
from core.notifier import Notifier
from core.service_interfaces import AuthServiceInterface
from app.repositories import CustomerRepository, LeadRepository
from app.notifications import SMSNotificationHandler

utc = pytz.UTC

USER_DOES_NOT_EXIST = "user does not exist"


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        lead_repository: LeadRepository,
        auth_service: AuthServiceInterface,
    ):
        self.lead_repository = lead_repository
        self.customer_repository = customer_repository
        self.auth_service = auth_service

    def show(self, customer_id):
        customer = self.customer_repository.find_by_id(customer_id)
        return Result(customer, 200)

    def update(self, customer_id, data):
        customer = self.customer_repository.update_by_id(customer_id, data)
        result = Result(customer, 200)
        return result

    def delete(self, customer_id):
        self.customer_repository.delete(customer_id)
        result = Result({}, 204)
        return result

    def register(self, data):
        phone_number = data.get("phone_number")
        existing_customer = self.customer_repository.find({"phone_number": phone_number})

        if existing_customer:
            raise AppException.ResourceExists(
                f"Customer with phone number {phone_number} exists"
            )

        auth_token = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=5)

        data["otp"] = auth_token
        data["otp_expiration"] = otp_expiration

        lead = self.lead_repository.create(data)

        self.notify(
            SMSNotificationHandler(
                recipient=lead.phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )

        return Result({"id": lead.id}, 201)

    def confirm_token(self, data):
        uuid = data.get("id")
        otp = data.get("token")
        lead = self.lead_repository.find({"id": uuid, "otp": otp})
        if not lead:
            raise AppException.BadRequest("Invalid authentication token")

        assert lead.otp == otp, "Wrong token"

        if utc.localize(datetime.now()) > lead.otp_expiration:
            raise AppException.ExpiredTokenException("the token you passed is expired")

        password_token = secrets.token_urlsafe(16)

        updated_lead = self.lead_repository.update_by_id(
            lead.id,
            {
                "password_token": password_token,
                "password_token_expiration": datetime.now() + timedelta(minutes=3),
            },
        )

        token_data = {"password_token": updated_lead.password_token}
        return Result(token_data, 200)

    def resend_token(self, lead_id):
        lead = self.lead_repository.find_by_id(lead_id)
        auth_token = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=5)

        updated_lead = self.lead_repository.update_by_id(
            lead_id, {"otp": auth_token, "otp_expiration": otp_expiration}
        )

        self.notify(
            SMSNotificationHandler(
                recipient=lead.phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": updated_lead.id}, 200)

    def add_pin(self, data):
        token = data.get("password_token")
        pin = data.get("pin")

        # find if password_token exists
        user = self.lead_repository.find({"password_token": token})

        if not user:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)

        # Check if password_token is valid or expired
        if utc.localize(datetime.now()) > user.password_token_expiration:
            raise AppException.ExpiredTokenException("token expired")

        user_data = {
            "username": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": pin,
            "group": "customer",
        }
        # Create user in auth service
        auth_result = self.auth_service.create_user(user_data)

        # Create user in customer table
        customer_data = {
            "id": user.id,
            "phone_number": user.phone_number,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id_type": user.id_type,
            "id_number": user.id_number,
            "status": "active",
            "auth_service_id": auth_result.get("id"),
        }

        self.customer_repository.create(customer_data)
        # Remove id from auth_result
        auth_result.pop("id", None)
        return Result(auth_result, 201)

    def login(self, data):
        phone_number = data.get("phone_number")
        pin = data.get("pin")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)

        access_token = self.auth_service.get_token(
            {"username": customer.id, "password": pin}
        )

        return Result(access_token, 200)

    def change_password(self, data):
        customer_id = data.get("customer_id")
        new_pin = data.get("new_pin")
        old_pin = data.get("old_pin")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        self.auth_service.get_token({"username": str(customer.id), "password": old_pin})
        self.auth_service.reset_password(
            {
                "user_id": str(customer.auth_service_id),
                "new_password": new_pin,
            }
        )
        return Result({}, 204)

    def request_password_reset(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})

        if not customer:
            raise AppException.NotFoundException("User not found")

        auth_token = random.randint(100000, 999999)
        auth_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": auth_token, "auth_token_expiration": auth_token_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipient=customer.phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": customer.id}, 200)

    def reset_password(self, data):
        auth_token = data.get("token")
        new_pin = data.get("new_pin")
        customer_id = data.get("id")

        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")

        assert customer.auth_token == auth_token, "Wrong token"

        if utc.localize(datetime.now()) > customer.auth_token_expiration:
            raise AppException.ExpiredTokenException("token expired")

        self.auth_service.reset_password(
            {"user_id": str(customer.auth_service_id), "new_password": new_pin}
        )
        self.notify(
            SMSNotificationHandler(
                recipient=customer.phone_number,
                details={"name": customer.first_name},
                meta={"type": "sms_notification", "subtype": "pin_change"},
            )
        )

        return Result("", 204)
