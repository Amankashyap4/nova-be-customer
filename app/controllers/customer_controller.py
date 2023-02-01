import inspect
import random
import secrets
from datetime import datetime, timedelta

import pytz
from flask import current_app, request

from app.core import Result
from app.core.exceptions import AppException
from app.core.notifications.notifier import Notifier
from app.core.repository import SQLBaseRepository
from app.enums import AccountStatusEnum
from app.events import ServiceEventSubscription, extract_valid_data
from app.notifications import EmailNotificationHandler, SMSNotificationHandler
from app.repositories import (
    CustomerRepository,
    LoginAttemptRepository,
    RegistrationRepository,
)
from app.services import AuthService, ObjectStorage
from app.utils import keycloak_fields, split_full_name

utc = pytz.UTC
OBJECT = "customer"
ASSERT_OBJECT_DATA = "missing object data"
ASSERT_OBJECT_ID = "missing object id"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        registration_repository: RegistrationRepository,
        login_attempt_repository: LoginAttemptRepository,
        auth_service: AuthService,
        object_storage: ObjectStorage,
    ):
        self.customer_repository = customer_repository
        self.registration_repository = registration_repository
        self.login_attempt_repository = login_attempt_repository
        self.auth_service = auth_service
        self.object_storage = object_storage

    def index(self, query_param: dict):
        result = self.customer_repository.paginate(
            page=int(query_param.get("page", 1)),
            per_page=int(query_param.get("per_page", 10)),
        )
        for customer in result:
            customer.profile_image = self.object_storage.download_object(
                f"customer/{customer.profile_image}"
            )
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("phone_number")
        query_data = {"phone_number": phone_number}

        try:
            customer = self.customer_repository.find(query_data)
        except AppException.NotFoundException:
            try:
                register_customer = self.registration_repository.find(query_data)
            except AppException.NotFoundException:
                register_customer = self.registration_repository.create(obj_data)
        else:
            if not customer.pin:
                message = {
                    "error": f"{OBJECT} with phone number {phone_number} exists",
                    "password_token": customer.auth_token,
                }
            else:
                message = f"{OBJECT} with phone number {phone_number} exists"
            raise AppException.ResourceExists(error_message=message)

        self.send_otp(
            otp_length=6,
            customer_obj=register_customer,
            repository_object=self.registration_repository,
        )

        return Result({"id": register_customer.id}, 201)

    def confirm_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("id")
        otp = obj_data.get("token")
        try:
            registered_customer = self.registration_repository.find(
                {"id": customer_id, "otp_token": otp}
            )
        except AppException.NotFoundException:
            raise AppException.BadRequest(
                error_message="invalid user id or otp token passed",
            )

        if utc.localize(datetime.now()) > registered_customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                error_message="otp token has expired"
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
        assert obj_data, ASSERT_OBJECT_IS_DICT

        obj_id = obj_data.pop("id")
        password_token = obj_data.pop("confirmation_token", None)

        try:
            registered_customer = self.registration_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.BadRequest(
                error_message=f"{OBJECT} with id {obj_id} does not exist"
            )
        else:
            if registered_customer.auth_token != password_token:
                raise AppException.BadRequest(error_message="invalid confirmation token")

        obj_data["auth_token"] = secrets.token_urlsafe(16)
        obj_data["auth_token_expiration"] = datetime.now() + timedelta(minutes=10)
        obj_data["phone_number"] = registered_customer.phone_number
        obj_data["retailer_id"] = registered_customer.retailer_id

        customer = self.customer_repository.create(obj_data)

        customer_name = split_full_name(obj_data.get("full_name"))
        obj_data["first_name"] = customer_name.get("first_name")
        obj_data["last_name"] = customer_name.get("last_name")

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
            "retailer_id": str(customer.retailer_id),
            "group": "nova-customer-gp",
        }
        # Create user in auth service
        auth_result = self.auth_service.create_user(user_data)

        # update customer in customer table
        self.customer_repository.update_by_id(
            customer.id,
            {"auth_service_id": auth_result},
        )
        token_data = {"password_token": customer.auth_token, "id": customer.id}

        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": user_data.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "new_account"},
            )
        )

        return Result(token_data, 200)

    def resend_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        obj_id = obj_data.get("id")
        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            try:
                customer = self.registration_repository.find_by_id(obj_id)
            except AppException.NotFoundException:
                raise AppException.BadRequest(error_message=f"unregistered {OBJECT}")
            else:
                self.send_otp(
                    otp_length=6,
                    customer_obj=customer,
                    repository_object=self.registration_repository,
                )
        else:
            self.send_otp(
                otp_length=6,
                customer_obj=customer,
                repository_object=self.customer_repository,
            )

        return Result({"id": obj_id}, 200)

    def login(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("phone_number")
        pin = obj_data.get("pin")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            # reminder: log login attempt
            self.login_attempt(phone_number=phone_number, ip_address=request.remote_addr)
            raise AppException.NotFoundException(error_message="account does not exist")
        # reminder: check if account has been locked out
        self.verify_account_lockout(account=customer)
        # reminder: unlock account if locked out
        self.unlock_account(account=customer)
        # reminder: verify account status
        if customer.status in [AccountStatusEnum.disabled, AccountStatusEnum.blocked]:
            raise AppException.OperationError(
                error_message=f"account has been {customer.status.value}"
            )
        # reminder: check if pin is correct
        if not customer.verify_pin(pin):
            # reminder: log login attempt
            self.login_attempt(phone_number=phone_number, ip_address=request.remote_addr)
        # reminder: get token from auth service i.e keycloak
        access_token = self.auth_service.get_token(
            {"username": customer.id, "password": pin}
        )
        user_data = {"last_login": str(datetime.now())}
        if customer.status == AccountStatusEnum.inactive:
            user_data["status"] = AccountStatusEnum.first_time.value
        self.customer_repository.update_by_id(obj_id=customer.id, obj_in=user_data)
        # reminder: reset login attempt of account
        self.reset_login_attempt(phone_number=phone_number)
        # reminder: modify data keys to match auth server fields i.e keycloak
        user_data = self.auth_service.auth_service_field(
            account_id=str(customer.id),
            obj_data=user_data,
        )
        # reminder: update account details in auth server i.e keycloak
        self.auth_service.update_user(user_data)

        customer.access_token = access_token.get("access_token")
        customer.refresh_token = access_token.get("refresh_token")

        return Result(customer, 200)

    def update(self, obj_id, obj_data):
        assert obj_id, ASSERT_OBJECT_ID
        assert obj_data, ASSERT_OBJECT_IS_DICT

        try:
            customer = self.customer_repository.update_by_id(obj_id, obj_data)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {obj_id} does not exists",
            )

        user_data = keycloak_fields(obj_id, obj_data)
        self.auth_service.update_user(user_data)
        if customer.profile_image:
            # generate ceph server url to retrieve profile image
            customer.profile_image = self.object_storage.download_object(
                f"customer/{obj_id}"
            )

        return Result(customer, 200)

    def set_profile_image(self, obj_id):
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {obj_id} does not exists",
            )

        # generate ceph server url to save profile image
        customer.pre_signed_post = self.object_storage.save_object(f"customer/{obj_id}")

        self.update(obj_id, {"profile_image": obj_id})

        # generate ceph server url to retrieve profile image
        customer.profile_image = self.object_storage.download_object(
            f"customer/{obj_id}"
        )

        return Result(customer, 200)

    def add_pin(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        pin = obj_data.get("pin")
        password_token = obj_data.get("password_token")
        try:
            customer = self.customer_repository.find({"auth_token": password_token})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(error_message="invalid password token")
        customer = self.customer_repository.update_by_id(customer.id, {"pin": pin})
        self.auth_service.reset_password(
            {"username": str(customer.id), "new_password": pin}
        )
        token = self.auth_service.get_token({"username": customer.id, "password": pin})
        token["id"] = customer.id

        customer_name = split_full_name(customer.full_name)

        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": customer_name.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "new_pin"},
            )
        )

        return Result(token, 200)

    def forgot_password(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with phone number {phone_number} does not exist"
            )

        self.send_otp(
            otp_length=6,
            customer_obj=customer,
            repository_object=self.customer_repository,
        )

        return Result({"id": customer.id}, 200)

    def reset_password(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("id")
        new_pin = obj_data.get("new_pin")
        auth_token = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )
        if not customer.auth_token:
            raise AppException.ExpiredTokenException(
                error_message="password token not set"
            )
        elif customer.auth_token != auth_token:
            raise AppException.ValidationException(error_message="Invalid token")

        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )

        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": None, "auth_token_expiration": None, "pin": new_pin},
        )

        customer_name = split_full_name(customer.full_name)

        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": customer_name.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "reset_pin"},
            )
        )
        if customer.email:
            self.notify(
                EmailNotificationHandler(
                    recipients=[customer.email],
                    details={"first_name": customer_name.get("first_name", "Dear")},
                    meta={"type": "email_notification", "subtype": "reset_pin"},
                )
            )

        return Result({"detail": "Pin reset done successfully"}, 200)

    def change_password_request(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("id")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )

        self.send_otp(
            customer_obj=customer,
            otp_length=6,
            repository_object=self.customer_repository,
        )

        return Result({"id": customer.id}, 200)

    def change_password(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("customer_id")
        new_pin = obj_data.get("new_pin")
        old_pin = obj_data.get("old_pin")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )

        self.auth_service.get_token({"username": customer_id, "password": old_pin})
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {
                "username": customer_id,
                "new_password": new_pin,
            }
        )

        customer_name = split_full_name(customer.full_name)
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": customer_name.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "change_password"},
            )
        )
        if customer.email:
            self.notify(
                EmailNotificationHandler(
                    recipients=[customer.email],
                    details={"first_name": customer_name.get("first_name", "Dear")},
                    meta={"type": "email_notification", "subtype": "change_password"},
                )
            )

        return Result({"detail": "Content reset done successfully"}, 200)

    def new_pin_request(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        if customer.pin:
            raise AppException.BadRequest(
                error_message=f"pin already set for account {phone_number}"
            )
        self.send_otp(
            otp_length=4,
            customer_obj=customer,
            repository_object=self.customer_repository,
        )

        return Result({"id": customer.id}, 200)

    def verify_new_pin(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_data = {}
        customer_id = obj_data.get("id")
        otp_pin = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )
        if customer.otp_token != otp_pin:
            raise AppException.Unauthorized(
                error_message="invalid otp, please try again",
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

    def set_new_pin(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("customer_id")
        password_token = obj_data.get("password_token")
        new_pin = obj_data.get("pin")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )
        if customer.auth_token != password_token:
            raise AppException.Unauthorized(error_message="invalid token")
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )
        customer_name = split_full_name(customer.full_name)
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": customer_name.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "reset_pin"},
            )
        )
        if customer.email:
            self.notify(
                EmailNotificationHandler(
                    recipients=[customer.email],
                    details={"first_name": customer_name.get("first_name", "Dear")},
                    meta={"type": "email_notification", "subtype": "reset_pin"},
                )
            )

        return Result(customer, 200)

    def change_phone_request(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        self.send_otp(
            otp_length=6,
            customer_obj=customer,
            repository_object=self.customer_repository,
        )

        return Result({"id": customer.id}, 200)

    def verify_phone_change(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        phone_number = obj_data.get("new_phone_number")
        auth_token = obj_data.get("token")
        customer_id = obj_data.get("customer_id")
        try:
            self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            try:
                customer = self.customer_repository.find_by_id(customer_id)
            except AppException.NotFoundException:
                raise AppException.NotFoundException(
                    error_message=f"{OBJECT} with id {customer_id} does not exists"
                )
        else:
            raise AppException.ResourceExists(
                error_message=f"{OBJECT} with phone number {phone_number} exists"
            )
        if customer.auth_token != auth_token:
            raise AppException.BadRequest(error_message="invalid token")

        self.send_otp(
            otp_length=6,
            customer_obj=customer,
            repository_object=self.customer_repository,
        )

        return Result({"id": customer.id, "phone_number": phone_number}, 200)

    def change_phone(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("customer_id")
        phone_number = obj_data.get("phone_number")
        otp = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists"
            )
        if not customer.otp_token or customer.otp_token != otp:
            raise AppException.BadRequest(error_message="Invalid token")
        self.customer_repository.update_by_id(
            customer_id, {"phone_number": phone_number}
        )
        user_data = keycloak_fields(customer_id, {"phone_number": phone_number})
        self.auth_service.update_user(user_data)
        customer_name = split_full_name(customer.full_name)
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"first_name": customer_name.get("first_name", "Dear")},
                meta={"type": "sms_notification", "subtype": "change_phone"},
            )
        )
        if customer.email:
            self.notify(
                EmailNotificationHandler(
                    recipients=[customer.email],
                    details={"first_name": customer_name.get("first_name", "Dear")},
                    meta={"type": "email_notification", "subtype": "change_phone"},
                )
            )

        return Result({"detail": "Phone reset done successfully"}, 200)

    def get_customer(self, obj_id):
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.get_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {obj_id} does not exists"
            )

        # reminder: generate ceph server url for retrieving profile image
        customer.profile_image = self.object_storage.download_object(
            f"customer/{customer.profile_image}"
        )
        return Result(customer, 200)

    def password_otp_confirmation(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_data = {}
        customer_id = obj_data.get("id")
        otp = obj_data.get("token")
        try:
            customer = self.customer_repository.find(
                {"id": customer_id, "otp_token": otp}
            )
        except AppException.NotFoundException:
            raise AppException.BadRequest(
                error_message="invalid user id or otp token passed"
            )

        if utc.localize(datetime.now()) > customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                error_message="otp token has expired"
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

    def refresh_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        customer_id = obj_data.get("id")
        refresh_token = obj_data.get("refresh_token")
        try:
            self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {customer_id} does not exists",
            )

        token = self.auth_service.refresh_token(refresh_token)
        token["id"] = customer_id
        return Result(token, 200)

    def find_by_phone_number(self, phone_number):
        assert phone_number, ASSERT_OBJECT_DATA

        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with phone number {phone_number} does not exist"
            )
        # generate ceph server url for retrieving profile image
        customer.profile_image = self.object_storage.download_object(
            f"customer/{customer.profile_image}"
        )
        return Result(customer, 200)

    # noinspection PyMethodMayBeStatic
    def send_otp(
        self, otp_length: int, customer_obj, repository_object: SQLBaseRepository
    ):

        # otp = "".join(random.choices(digits, k=otp_length))
        if otp_length == 4:
            otp = 6666
        else:
            otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        repository_object.update_by_id(
            customer_obj.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )

        self.notify(
            SMSNotificationHandler(
                recipients=[customer_obj.phone_number],
                details={"verification_code": otp},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )

        return None

    def login_attempt(self, phone_number: str, ip_address: str):
        attempt_details = {
            "phone_number": phone_number,
            "request_ip_address": ip_address,
            "failed_login_attempts": 1,
            "failed_login_time": datetime.now(),
            "expires_in": datetime.now() + timedelta(minutes=1),
        }
        try:
            # reminder: check if an attempt exist
            record = self.login_attempt_repository.find(
                {"phone_number": phone_number, "status": AccountStatusEnum.active}
            )
        except AppException.NotFoundException:
            # reminder: create new attempt record
            self.login_attempt_repository.create(attempt_details)
        else:
            # reminder: check if attempt record has expired
            if utc.localize(datetime.now()) > record.expires_in:
                self.login_attempt_repository.update_by_id(
                    obj_id=record.id, obj_in={"status": AccountStatusEnum.inactive}
                )
                self.login_attempt_repository.create(attempt_details)
            else:
                # reminder: increment record counter
                self.login_attempt_repository.update_by_id(
                    obj_id=record.id,
                    obj_in={
                        "failed_login_attempts": sum((record.failed_login_attempts, 1)),
                        "failed_login_time": datetime.now(),
                    },
                )
                if record.failed_login_attempts > 4:
                    self.lock_account_out(record=record, phone_number=phone_number)
        return None

    def reset_login_attempt(self, phone_number: str):
        assert phone_number, ASSERT_OBJECT_DATA.format("phone_number")

        try:
            record = self.login_attempt_repository.find(
                {"phone_number": phone_number, "status": AccountStatusEnum.active}
            )
        except AppException.NotFoundException:
            return None
        else:
            self.login_attempt_repository.update_by_id(
                obj_id=record.id, obj_in={"status": AccountStatusEnum.inactive}
            )

        return None

    def lock_account_out(self, record, phone_number):
        try:
            self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            return None
        else:
            self.login_attempt_repository.update_by_id(
                obj_id=record.id,
                obj_in={"lockout_expiration": datetime.now() + timedelta(minutes=5)},
            )
        return None

    def unlock_account(self, account):
        try:
            record = self.login_attempt_repository.find(
                {
                    "phone_number": account.phone_number,
                    "status": AccountStatusEnum.active,
                }
            )
        except AppException.NotFoundException:
            return None
        else:
            account_lockout = record.lockout_expiration
            if account_lockout and utc.localize(datetime.now()) > account_lockout:
                self.login_attempt_repository.update_by_id(
                    obj_id=record.id, obj_in={"status": AccountStatusEnum.inactive}
                )
        return None

    def verify_account_lockout(self, account):
        try:
            record = self.login_attempt_repository.find(
                {
                    "phone_number": account.phone_number,
                    "status": AccountStatusEnum.active,
                }
            )
        except AppException.NotFoundException:
            return None
        else:
            account_lockout = record.lockout_expiration
            if account_lockout and utc.localize(datetime.now()) <= account_lockout:
                raise AppException.NotFoundException(
                    error_message="login attempts exceeded. account locked out"
                )
        return None

    # noinspection PyMethodMayBeStatic
    def customer_profile_images(self):

        profile_images = self.object_storage.list_objects(directory_name="customer")
        return Result(profile_images, 200)

    # noinspection PyMethodMayBeStatic
    def customer_profile_image(self, obj_id):
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"{OBJECT} with id {obj_id} does not exist"
            )
        profile_images = self.object_storage.get_object(
            f"customer/{customer.profile_image}"
        )
        return Result(profile_images, 200)

    # reminder: below methods handles event subscription for the service
    def cust_deposit(self, obj_data):
        data = extract_valid_data(
            obj_data=obj_data,
            validator=ServiceEventSubscription.cust_deposit.value,
        )
        try:
            self.update(
                obj_id=data.get("customer_id"),
                obj_data={
                    "level": data.get("type_id"),
                    "status": AccountStatusEnum.active.value,
                },
            )
        except (
            AppException.NotFoundException,
            AppException.KeyCloakAdminException,
            AppException.InternalServerError,
        ) as exc:
            current_app.logger.critical(
                {
                    "event": f"<{inspect.currentframe().f_back.f_code.co_name}>",
                    "data": obj_data,
                    "error": f"{exc}",
                }
            )
