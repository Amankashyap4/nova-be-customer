import random
import secrets
from datetime import datetime, timedelta

import pytz

from app.core import Result
from app.core.exceptions import AppException
from app.core.notifications.notifier import Notifier
from app.core.service_interfaces import AuthServiceInterface
from app.repositories import CustomerRepository, RegistrationRepository
from app.utils import keycloak_fields, object_download_url, object_upload_url

utc = pytz.UTC

USER_DOES_NOT_EXIST = "user does not exist"


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        registration_repository: RegistrationRepository,
        auth_service: AuthServiceInterface,
    ):
        self.customer_repository = customer_repository
        self.registration_repository = registration_repository
        self.auth_service = auth_service

    def index(self):
        result = self.customer_repository.index()
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, "missing data of object to be saved"
        assert "phone_number" in obj_data, "phone number missing"
        phone_number = obj_data.get("phone_number")
        query_data = {"phone_number": phone_number}
        existing_customer = self.customer_repository.find(query_data)
        if existing_customer:
            raise AppException.ResourceExists(
                context=f"customer with phone number {phone_number} exists",
                error_message={"controller.register": "existing customer"},
            )
        customer = self.registration_repository.find(query_data)
        if customer:
            self.registration_repository.delete(customer.id)

        try:
            register_customer = self.registration_repository.create(query_data)
        except AppException.OperationError as e:
            raise AppException.OperationError(
                context=e.context, error_message={"controller.register": e}
            )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.registration_repository.update_by_id(
            register_customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        return Result({"id": register_customer.id}, 201)

    def confirm_token(self, obj_data):
        assert obj_data, "missing data of object"

        customer_id = obj_data.get("id")
        otp = obj_data.get("token")
        registered_customer = self.registration_repository.find(
            {"id": customer_id, "otp_token": otp}
        )
        if not registered_customer:
            raise AppException.BadRequest(
                context="invalid user id or otp token passed",
                error_message={"controller.confirm_token": "invalid user"},
            )

        if utc.localize(datetime.now()) > registered_customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                context="otp token has expired",
                error_message={"controller.confirm_token": "token expiration"},
            )
        password_token = secrets.token_urlsafe(16)
        update_customer = self.registration_repository.update_by_id(
            registered_customer.id,
            {
                "auth_token": password_token,
                "auth_token_expiration": datetime.now() + timedelta(minutes=5),
            },
        )
        token_data = {
            "confirmation_token": update_customer.auth_token,
            "id": update_customer.id,
        }
        return Result(token_data, 200)

    def add_information(self, obj_data):
        assert obj_data, "missing data of object to update"

        obj_id = obj_data.pop("id")
        password_token = obj_data.pop("confirmation_token", None)
        registered_customer = self.registration_repository.find({"id": obj_id})
        if not registered_customer:
            raise AppException.BadRequest(
                context="Invalid customer",
                error_message={"controller.add_information": "unregistered customer"},
            )
        elif registered_customer.auth_token != password_token:
            raise AppException.BadRequest(
                context="Something went wrong, please try again",
                error_message={"controller.add_information": "wrong customer token"},
            )

        obj_data["auth_token"] = secrets.token_urlsafe(16)
        obj_data["auth_token_expiration"] = datetime.now() + timedelta(minutes=10)
        obj_data["phone_number"] = registered_customer.phone_number

        customer = self.customer_repository.create(obj_data)

        if obj_data.get("full_name"):
            fullname = obj_data.pop("full_name").split(" ")
            obj_data["first_name"] = fullname[0]
            obj_data["last_name"] = " ".join(fullname[1:])

        user_data = {
            "username": str(customer.id),
            "password": str(random.randint(1000, 9999)),
            "first_name": obj_data.get("first_name"),
            "last_name": obj_data.get("last_name"),
            "phone_number": obj_data.get("phone_number"),
            "id_type": obj_data.get("id_type"),
            "id_expiry_date": obj_data.get("id_expiry_date"),
            "id_number": obj_data.get("id_number"),
            "status": customer.status.value,
            "group": "nova-customer-gp",
        }
        # Create user in auth service
        auth_result = self.auth_service.create_user(user_data)

        # update customer in customer table
        self.customer_repository.update_by_id(
            customer.id,
            {"auth_service_id": auth_result},
        )
        token_data = {"password_token": customer.auth_token, "id": auth_result}

        return Result(token_data, 200)

    def resend_token(self, obj_data):
        obj_id = obj_data.get("id")
        registered_customer = None
        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            customer = None
        if not customer:
            try:
                registered_customer = self.registration_repository.find_by_id(obj_id)
            except AppException.NotFoundException:
                raise AppException.BadRequest(
                    context="Invalid customer",
                    error_message={"controller.resend_token": "invalid customer"},
                )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        if customer:
            self.customer_repository.update_by_id(
                customer.id,
                {"otp_token": otp, "otp_token_expiration": otp_expiration},
            )
        elif registered_customer:
            self.registration_repository.update_by_id(
                obj_id,
                {"otp_token": otp, "otp_token_expiration": otp_expiration},
            )

        return Result({"id": obj_id}, 200)

    def login(self, obj_credential):
        assert obj_credential, "missing credentials of object"
        customer_data = {}
        phone_number = obj_credential.get("phone_number")
        pin = obj_credential.get("pin")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(
                context=f"customer with phone number {phone_number} does not exists",
                error_message={
                    "controller.login": f"phone number {phone_number} does not exist"
                },
            )
        if customer.status.value not in ["blocked", "disabled"]:
            access_token = self.auth_service.get_token(
                {"username": customer.id, "password": pin}
            )
            self.update(str(customer.id), {"status": "first_time"})
            customer_data["full_name"] = customer.full_name
            customer_data["birth_date"] = customer.birth_date
            customer_data["id_number"] = customer.id_number
            customer_data["id_type"] = customer.id_type
            customer_data["phone_number"] = customer.phone_number
            customer_data["id"] = customer.id
            customer_data["access_token"] = access_token.get("access_token")
            customer_data["refresh_token"] = access_token.get("refresh_token")
            return Result(customer_data, 200)
        raise AppException.NotFoundException(
            context=f"account {phone_number} has been {customer.status.value}",
            error_message={"controller.login": "account disable or block"},
        )

    def update(self, obj_id, obj_data):
        assert obj_id, "missing id of object to update"
        assert obj_data, "missing data of object to update"

        if obj_data.get("profile_image"):
            obj_data["profile_image"] = f"{obj_id}.{obj_data.get('profile_image')}"

        try:
            customer = self.customer_repository.update_by_id(obj_id, obj_data)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {obj_id} does not exists",
                error_message={"controller.update": f"id {obj_id} does not exist"},
            )

        user_data = keycloak_fields(obj_id, obj_data)
        self.auth_service.update_user(user_data)

        # set pre-signed url to upload profile image
        object_upload_url(customer)

        # set pre-signed url to download profile image
        object_download_url(customer)

        return Result(customer, 200)

    def add_pin(self, obj_data):
        assert obj_data, "Missing data of object"

        pin = obj_data.get("pin")
        password_token = obj_data.get("password_token")
        customer = self.customer_repository.find({"auth_token": password_token})
        if not customer:
            raise AppException.NotFoundException(
                context="customer does not exists",
                error_message={"controller.add_pin": "invalid password token"},
            )
        customer = self.customer_repository.update_by_id(customer.id, {"pin": pin})
        self.auth_service.reset_password(
            {"username": str(customer.id), "new_password": pin}
        )
        token = self.auth_service.get_token({"username": customer.id, "password": pin})
        token["id"] = customer.id
        return Result(token, 200)

    def forgot_password(self, obj_phone):
        assert obj_phone, "missing phone number of object"
        phone_number = obj_phone.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})

        if not customer:
            raise AppException.NotFoundException(
                context=f"customer with phone number {phone_number} does not exists",
                error_message={
                    "controller.forgot_password": f"phone number {phone_number} does not exist"
                },
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
        new_pin = obj_data.get("new_pin")
        auth_token = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {customer_id} does not exists",
                error_message={
                    "controller.reset_password": f"id {customer_id} does not exist"
                },
            )
        if not customer.auth_token:
            raise AppException.ExpiredTokenException(
                context="token expired",
                error_message={"controller.reset_password": "auth token is None"},
            )
        elif customer.auth_token != auth_token:
            raise AppException.ValidationException(
                context="Invalid token",
                error_message={"controller.reset_password": "invalid token "},
            )

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
        new_pin = obj_data.get("new_pin")
        old_pin = obj_data.get("old_pin")
        try:
            self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {customer_id} does not exists",
                error_message={
                    "controller.change_password": f"id {customer_id} does not exist"
                },
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
            raise AppException.NotFoundException(
                context=USER_DOES_NOT_EXIST,
                error_message={
                    "controller.pin_process": f"phone number {phone_number} does not exist"
                },
            )
        if customer.pin:
            raise AppException.BadRequest(
                context=f"pin already set for account {phone_number}",
                error_message={
                    "controller.pin_process": f"pin set for account {phone_number}"
                },
            )
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
        otp_pin = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(
                context="user does not exist",
                error_message={
                    "controller.reset_pin_process": f"id {customer} does not exist"
                },
            )
        if customer.otp_token != otp_pin:
            raise AppException.Unauthorized(
                context="Wrong otp, please try again",
                error_message={
                    "controller.reset_pin_process": f"wrong token provided {otp_pin}"
                },
            )
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
        password_token = data.get("password_token")
        new_pin = data.get("pin")
        customer = self.customer_repository.find_by_id(customer_id)

        if not customer:
            raise AppException.NotFoundException(
                context="user does not exist",
                error_message={
                    "controller.process_reset_pin": f"id {customer_id} does not exist"
                },
            )
        if customer.auth_token != password_token:
            raise AppException.Unauthorized(
                context="Something went wrong, please try again",
                error_message={
                    "controller.process_reset_pin": f"invalid auth token {password_token}"
                },
            )
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
                context=f"customer with phone number {phone_number} does not exists",
                error_message={
                    "controller.request_pin": f"phone number {phone_number} does not exist"
                },
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
                context=f"customer with phone number {phone_number} does not exists",
                error_message={
                    "controller.reset_phone_request": f"phone number {phone_number} does not exist"  # noqa
                },
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
        customer_id = data.get("customer_id")
        if existing_customer:
            raise AppException.ResourceExists(
                context=f"customer with phone number {phone_number} exists",
                error_message={
                    "controller.reset_phone": f"phone number {phone_number} does not exist"
                },
            )
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(
                context=USER_DOES_NOT_EXIST,
                error_message={
                    "controller.reset_phone": f"id {customer_id} does not exist"
                },
            )
        if customer.auth_token != auth_token:
            raise AppException.BadRequest(
                context="Invalid token",
                error_message={
                    "controller.reset_phone": f"invalid auth token {auth_token}"
                },
            )
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
        phone_number = data.get("phone_number")
        otp = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(
                context=USER_DOES_NOT_EXIST,
                error_message={
                    "controller.request_phone_reset": f"id {customer_id} does not exist"
                },
            )
        if not customer.otp_token or customer.otp_token != otp:
            raise AppException.ExpiredTokenException(
                context="Invalid OTP",
                error_message={
                    "controller.request_phone_reset": f"invalid otp token {otp}"
                },
            )
        self.update(customer_id, {"phone_number": phone_number})
        return Result({"detail": "Phone reset done successfully"}, 200)

    def get_customer(self, obj_id):
        customer = self.customer_repository.get_by_id(obj_id)
        # set pre-signed url on object to download profile image
        object_download_url(customer)
        return Result(customer, 200)

    def password_otp_confirmation(self, data):
        customer_data = {}
        customer_id = data.get("id")
        otp = data.get("token")
        customer = self.customer_repository.find({"id": customer_id, "otp_token": otp})
        if not customer:
            raise AppException.BadRequest(
                context="invalid user id or otp token passed",
                error_message={
                    "controller.password_otp_confirmation": f"invalid token {otp} or id {customer_id}"  # noqa
                },
            )

        if utc.localize(datetime.now()) > customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                context="otp token has expired",
                error_message={
                    "controller.password_otp_confirmation": f"opt {otp} has expired"
                },
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
        try:
            result = self.customer_repository.update_by_id(
                obj_id, {"status": "disabled"}
            )
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {obj_id} does not exists",
                error_message={"controller.delete": f"id {obj_id} does not exist"},
            )
        data = {
            "username": obj_id,
            "status": result.status.value,
        }
        self.auth_service.update_user(data)
        return Result({}, 204)

    def refresh_token(self, obj_data):
        assert obj_data, "missing data of object"
        assert "id" in obj_data, "missing id of object"
        assert "refresh_token", "missing refresh token of object"

        customer_id = obj_data.get("id")
        refresh_token = obj_data.get("refresh_token")
        try:
            self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {customer_id} does not exists",
                error_message={
                    "controller.refresh_token": f"id {customer_id} does not exist"
                },
            )

        access_token = self.auth_service.refresh_token(refresh_token)
        access_token["id"] = customer_id
        return Result(access_token, 200)

    def find_by_phone_number(self, phone_number):
        assert phone_number, "missing data of object"

        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.BadRequest(
                context=f"customer with phone number {phone_number} does not exist",
                error_message={
                    "controller.find_by_phone_number": f"phone number {phone_number} does not exist"  # noqa
                },
            )

        return Result(customer, 200)
