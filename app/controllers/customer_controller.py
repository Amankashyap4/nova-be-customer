import random

from app.definitions import Result, ServiceResult
from app.definitions.exceptions import AppException
from app.definitions.notifier import Notifier
from app.repositories import CustomerRepository, LeadRepository
from app.services import AuthService
from app.notifications import SMSNotificationHandler


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
        otp = random.randint(100000, 999999)
        data["otp"] = otp
        phone_number = data.get("phone_number")
        existing_customer = self.customer_repository.find_by_number(phone_number)
        if existing_customer:
            raise AppException.ResourceExists(
                f"Customer with phone number {phone_number} exists"
            )
        customer = self.lead_repository.create(data)

        self.notify(
            SMSNotificationHandler(customer.phone_number, {"otp": otp}, "sms_otp")
        )

        return ServiceResult(Result({"id": customer.id}, 201))

    def confirm_token(self, data):
        uuid = data.get("id")
        otp = data.get("token")
        user = self.lead_repository.find_by_otp(id=uuid, otp=otp)
        if user:
            user_data = {
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "id_type": user.id_type,
                "id_number": user.id_number,
                "status": "active",
            }

            customer = self.customer_repository.create(user_data)
            return ServiceResult(Result(customer, 200))
        else:
            raise AppException.BadRequest("Invalid authentication token")

    def add_pin(self, data):
        uuid = data.get("id")
        pin = data.get("pin")

        user = self.lead_repository.find_by_id(uuid)

        if user:
            user_data = {
                "username": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password": pin,
            }
            self.auth_service.create_user(user_data)
        else:
            raise AppException.NotFoundException("User does not exist")

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
