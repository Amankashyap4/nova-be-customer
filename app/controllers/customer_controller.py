import random
import secrets
from datetime import datetime, timedelta

import pytz

from app.core import Result
from app.core.exceptions import AppException
from app.core.notifications.notifier import Notifier
from app.core.service_interfaces import AuthServiceInterface
from app.repositories import CustomerRepository
from app.utils import keycloak_fields, validate_uuid

utc = pytz.UTC

USER_DOES_NOT_EXIST = "user does not exist"


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        auth_service: AuthServiceInterface,
    ):
        self.customer_repository = customer_repository
        self.auth_service = auth_service

    def index(self):
        result = self.customer_repository.index()
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, "missing data of object to be saved"
        assert "phone_number" in obj_data, "phone number missing"
        phone_number = obj_data.get("phone_number")
        user_data = {
            "phone_number": phone_number,
        }
        existing_customer = self.customer_repository.find({"phone_number": phone_number})
        if existing_customer:
            raise AppException.ResourceExists(
                context={
                    "controller.create": f"customer with phone number {phone_number} exists"  # noqa
                }
            )
        try:
            customer = self.customer_repository.create(user_data)
        except AppException.OperationError as e:
            raise AppException.OperationError(context={"controller.create": e.context})
        user_data = {
            "username": str(customer.id),
            "password": str(random.randint(1000, 9999)),
            "phone_number": user_data.get("phone_number"),
            "status": customer.status.value,
            "group": "nova-customer-gp",
        }
        # Create user in auth service
        auth_result = self.auth_service.create_user(user_data)
        self.customer_repository.update_by_id(
            customer.id,
            {"auth_service_id": auth_result},
        )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        return Result({"id": customer.id}, 201)

    def confirm_token(self, obj_data):
        assert obj_data, "missing data of object"

        customer_id = obj_data.get("id")
        validate_uuid(customer_id)
        otp = obj_data.get("token")
        customer = self.customer_repository.find({"id": customer_id, "otp_token": otp})
        if not customer:
            raise AppException.BadRequest(
                context={"controller.confirm_otp": "invalid user id or otp token passed"}
            )

        if utc.localize(datetime.now()) > customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                context={"controller.confirm_otp": "otp token has expired"}
            )
        password_token = secrets.token_urlsafe(16)
        updated_customer = self.customer_repository.update_by_id(
            customer.id,
            {
                "auth_token": password_token,
                "auth_token_expiration": datetime.now() + timedelta(minutes=5),
            },
        )
        token_data = {
            "confirmation_token": updated_customer.auth_token,
            "id": updated_customer.id,
        }
        return Result(token_data, 200)

    def add_information(self, obj_data):
        assert obj_data, "missing data of object to update"

        obj_id = obj_data.pop("id")
        validate_uuid(obj_id)
        password_token = obj_data.get("confirmation_token")
        customer = self.customer_repository.find({"id": obj_id})
        if not customer:
            raise AppException.BadRequest("Invalid customer")
        elif customer.auth_token != password_token:
            raise AppException.BadRequest("Something went wrong, please try again")

        obj_data["auth_token"] = secrets.token_urlsafe(16)
        obj_data["auth_token_expiration"] = datetime.now() + timedelta(minutes=10)

        try:
            customer = self.customer_repository.update_by_id(obj_id, obj_data)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context={
                    "controller.update": f"customer with id {obj_id} does not exists"  # noqa
                }
            )
        user_data = keycloak_fields(obj_id, obj_data)
        auth = self.auth_service.update_user(user_data)
        token_data = {"password_token": customer.auth_token, "id": auth}

        return Result(token_data, 200)

    def resend_token(self, obj_data):
        obj_id = obj_data.get("id")
        validate_uuid(obj_id)
        customer = self.customer_repository.find_by_id(obj_id)
        if not customer:
            raise AppException.BadRequest("Invalid customer")
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        return Result({"id": customer.id}, 200)

    def login(self, obj_credential):
        assert obj_credential, "missing credentials of object"

        phone_number = obj_credential.get("phone_number")
        pin = obj_credential.get("pin")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(
                context={
                    "controller.login": f"customer with phone number {phone_number} does not exists"  # noqa
                }
            )
        if customer.status.value not in ["blocked", "disabled"]:
            access_token = self.auth_service.get_token(
                {"username": customer.id, "password": pin}
            )
            self.update(str(customer.id), {"status": "first_time"})
            return Result(access_token, 200)
        raise AppException.NotFoundException(
            context={
                "controller.login": f"account {phone_number} has been {customer.status.value}"  # noqa
            }
        )

    def update(self, obj_id, obj_data):
        assert obj_id, "missing id of object to update"
        assert obj_data, "missing data of object to update"
        validate_uuid(obj_id)
        try:
            customer = self.customer_repository.update_by_id(obj_id, obj_data)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context={
                    "controller.update": f"customer with id {obj_id} does not exists"  # noqa
                }
            )
        user_data = keycloak_fields(obj_id, obj_data)
        self.auth_service.update_user(user_data)

        return Result(customer, 200)

    def add_pin(self, obj_data):
        assert obj_data, "Missing data of object"

        pin = obj_data.get("pin")
        password_token = obj_data.get("password_token")
        customer = self.customer_repository.find({"auth_token": password_token})
        if not customer:
            raise AppException.NotFoundException(
                context={"controller.reset_password": "customer does not exists"}
            )
        customer = self.customer_repository.update_by_id(customer.id, {"pin": pin})
        self.auth_service.reset_password(
            {"username": str(customer.id), "new_password": pin}
        )
        return Result({"id": customer.id}, 200)

    def forgot_password(self, obj_phone):
        assert obj_phone, "missing phone number of object"
        phone_number = obj_phone.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})

        if not customer:
            raise AppException.NotFoundException(
                context={
                    "controller.forgot_password": f"customer with phone number {phone_number} does not exists"  # noqa
                }
            )
        # otp = random.randint(100000, 999999)
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        return Result({"id": customer.id}, 200)

    def reset_password(self, obj_data):
        assert obj_data, "Missing data of object"

        customer_id = obj_data.get("id")
        validate_uuid(customer_id)
        new_pin = obj_data.get("new_pin")
        auth_token = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context={
                    "controller.reset_password": f"customer with id {customer_id} does not exists"  # noqa
                    # noqa
                }
            )
        if not customer.auth_token:
            raise AppException.ExpiredTokenException("token expired")
        elif customer.auth_token != auth_token:
            raise AppException.ValidationException("Invalid token")

        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )

        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": None, "auth_token_expiration": None, "pin": new_pin},
        )

        return Result({"detail": "Pin reset done successfully"}, 200)

    def change_password(self, obj_data):
        assert obj_data, "missing data of object"

        customer_id = obj_data.get("customer_id")
        validate_uuid(customer_id)
        new_pin = obj_data.get("new_pin")
        old_pin = obj_data.get("old_pin")
        try:
            self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context={
                    "controller.change_password": f"customer with id {customer_id} does not exists"  # noqa
                    # noqa
                }
            )

        self.auth_service.get_token({"username": customer_id, "password": old_pin})
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {
                "username": customer_id,
                "new_password": new_pin,
            }
        )
        return Result({"detail": "Content reset done successfully"}, 200)

    def pin_process(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        if customer.pin:
            raise AppException.BadRequest(f"pin already set for account {phone_number}")
        otp_token = 6666
        # otp_token = random.randint(1000, 9999)
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp_token, "otp_token_expiration": otp_token_expiration},
        )
        return Result({"id": customer.id}, 200)

    def reset_pin_process(self, data):
        customer_data = {}
        customer_id = data.get("id")
        validate_uuid(customer_id)
        otp_pin = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("user does not exist")
        if customer.otp_token != otp_pin:
            raise AppException.Unauthorized("Wrong otp, please try again")
        password_token_expiration = datetime.now() + timedelta(minutes=5)
        password_token = secrets.token_urlsafe(16)
        self.customer_repository.update_by_id(
            customer.id,
            {
                "otp": None,
                "otp_expiration": None,
                "auth_token": password_token,
                "auth_token_expiration": password_token_expiration,
            },
        )
        customer_data["full_name"] = customer.full_name
        customer_data["id"] = customer.id
        customer_data["password_token"] = password_token
        return Result(customer_data, 200)

    def process_reset_pin(self, data):
        customer_id = data.get("customer_id")
        validate_uuid(customer_id)
        password_token = data.get("password_token")
        new_pin = data.get("pin")
        customer = self.customer_repository.find_by_id(customer_id)

        if not customer:
            raise AppException.NotFoundException("user does not exist")
        if customer.auth_token != password_token:
            raise AppException.Unauthorized("Something went wrong, please try again")
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )
        return Result(customer, 200)

    def request_pin(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(
                context={
                    "controller.reqeust_pin": f"customer with phone number {phone_number} does not exists"  # noqa
                }
            )
        # otp_token = random.randint(1000, 9999)
        otp = 6666
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_token_expiration},
        )
        return Result({"id": customer.id}, 200)

    def reset_phone_request(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(
                context={
                    "controller.change_phone_number": f"customer with phone number {phone_number} does not exists"  # noqa
                }
            )
        otp = 666666
        # otp = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        return Result({"id": customer.id}, 200)

    def reset_phone(self, data):
        phone_number = data.get("new_phone_number")
        auth_token = data.get("token")
        existing_customer = self.customer_repository.find({"phone_number": phone_number})
        if existing_customer:
            raise AppException.ResourceExists(
                f"Customer with phone number {phone_number} exists"
            )
        customer = self.customer_repository.find_by_id(data.get("customer_id"))
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        if customer.auth_token != auth_token:
            raise AppException.BadRequest("Invalid token")
        otp_token = 666666
        # otp_token = random.randint(100000, 999999)
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {
                "otp_token": otp_token,
                "otp_token_expiration": otp_token_expiration,
            },
        )
        data = {"id": customer.id, "phone_number": phone_number}
        return Result(data, 200)

    def request_phone_reset(self, data):
        customer_id = data.get("customer_id")
        validate_uuid(customer_id)
        phone_number = data.get("phone_number")
        otp = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        if not customer.otp_token or customer.otp_token != otp:
            raise AppException.ExpiredTokenException("Invalid OTP")
        self.update(customer_id, {"phone_number": phone_number})
        return Result({"detail": "Phone reset done successfully"}, 200)

    def get_customer(self, obj_id):
        validate_uuid(obj_id)
        customer = self.customer_repository.get_by_id(obj_id)
        return Result(customer, 200)

    def password_otp_confirmation(self, data):
        customer_data = {}
        customer_id = data.get("id")
        validate_uuid(customer_id)
        otp = data.get("token")
        customer = self.customer_repository.find({"id": customer_id, "otp_token": otp})
        if not customer:
            raise AppException.BadRequest(
                context={"controller.confirm_otp": "invalid user id or otp token passed"}
            )

        if utc.localize(datetime.now()) > customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                context={"controller.confirm_otp": "otp token has expired"}
            )
        auth_token = random.randint(100000, 999999)
        auth_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {
                "otp_token": None,
                "auth_token": auth_token,
                "auth_token_expiration": auth_token_expiration,
            },
        )
        customer_data["id"] = customer.id
        customer_data["token"] = str(auth_token)
        return Result(customer_data, 200)

    def delete(self, obj_id):
        assert obj_id, "missing id of object to delete"
        validate_uuid(obj_id)
        try:
            result = self.customer_repository.update_by_id(
                obj_id, {"status": "disabled"}
            )
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context={
                    "controller.delete": f"customer with id {obj_id} does not exists"
                }
            )
        data = {
            "username": obj_id,
            "status": result.status.value,
        }
        self.auth_service.update_user(data)
        return Result({}, 204)
