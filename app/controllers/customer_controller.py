import random
import secrets
import pytz
from datetime import datetime, timedelta

from app.definitions import Result, ServiceResult
from app.definitions.exceptions import AppException
from app.definitions.notifier import Notifier
from app.repositories import CustomerRepository, LeadRepository
from app.services import AuthService
from app.notifications import SMSNotificationHandler


utc = pytz.UTC


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        lead_repository: LeadRepository,
        auth_service: AuthService,
    ):
        self.lead_repository = lead_repository
        self.customer_repository = customer_repository
        self.auth_service = auth_service

    def register(self, data):

        phone_number = data.get("phone_number")
        existing_customer = self.customer_repository.find({"phone_number": phone_number})

        if existing_customer:
            raise AppException.ResourceExists(
                f"Customer with phone number {phone_number} exists"
            )

        otp = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=5)

        data["otp"] = otp
        data["otp_expiration"] = otp_expiration

        customer = self.lead_repository.create(data)

        self.notify(
            SMSNotificationHandler(customer.phone_number, {"otp": otp}, "sms_otp")
        )

        return ServiceResult(Result({"id": customer.id}, 201))

    def confirm_token(self, data):
        uuid = data.get("id")
        otp = data.get("token")
        lead = self.lead_repository.find_by_otp(id=uuid, otp=otp)

        if not lead:
            raise AppException.BadRequest("Invalid authentication token")

        if utc.localize(dt=datetime.now()) > lead.otp_expiration:
            raise AppException.ExpiredTokenException("token expired")

        password_token = secrets.token_urlsafe(16)

        updated_lead = self.lead_repository.update_by_id(
            lead.id,
            {
                "password_token": password_token,
                "password_token_expiration": datetime.now() + timedelta(minutes=3),
            },
        )

        token_data = {"password_token": updated_lead.password_token}
        return ServiceResult(Result(token_data, 200))

    def resend_token(self, lead_id):
        lead = self.lead_repository.find_by_id(lead_id)
        otp = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=5)

        updated_lead = self.lead_repository.update_by_id(
            lead_id, {"otp": otp, "otp_expiration": otp_expiration}
        )

        self.notify(SMSNotificationHandler(lead.phone_number, {"otp": otp}, "sms_otp"))
        return ServiceResult(Result({"id": updated_lead.id}, 201))

    def add_pin(self, data):
        token = data.get("password_token")
        pin = data.get("pin")

        user = self.lead_repository.find({"password_token": token})

        if not user:
            raise AppException.NotFoundException("User does not exist")

        if utc.localize(dt=datetime.now()) > user.otp_expiration:
            raise AppException.ExpiredTokenException("token expired")

        user_data = {
            "username": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": pin,
        }
        self.auth_service.create_user(user_data)

        customer_data = {
            "id": user.id,
            "phone_number": user.phone_number,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id_type": user.id_type,
            "id_number": user.id_number,
            "status": "active",
        }
        return self.create(customer_data)

    def create(self, data):
        customer = self.customer_repository.create(data)
        result = ServiceResult(Result(customer, 201))
        return result

    def show(self, customer_id):
        customer = self.customer_repository.find_by_id(customer_id)
        result = ServiceResult(Result(customer, 200))
        return result

    def update(self, customer_id, data):
        customer = self.customer_repository.update_by_id(customer_id, data)
        result = ServiceResult(Result(customer, 200))
        return result

    def delete(self, customer_id):
        self.customer_repository.delete(customer_id)
        result = ServiceResult(Result({}, 204))
        return result
