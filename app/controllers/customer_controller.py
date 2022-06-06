import random
import secrets
from datetime import datetime, timedelta

import pytz
from loguru import logger

from app.core import Result
from app.core.exceptions import AppException
from app.core.notifications.notifier import Notifier
from app.events import EventNotificationHandler, ServiceEventPublishing
from app.notifications import SMSNotificationHandler
from app.repositories import CustomerRepository, RegistrationRepository
from app.schema import CustomerSchema
from app.services import AuthService, ObjectStorage
from app.utils import keycloak_fields

utc = pytz.UTC
OBJECT = "customer"
ASSERT_OBJECT_DATA = "missing object data"
ASSERT_OBJECT_ID = "missing object id"


class CustomerController(Notifier):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        registration_repository: RegistrationRepository,
        auth_service: AuthService,
        object_storage: ObjectStorage,
    ):
        self.customer_repository = customer_repository
        self.registration_repository = registration_repository
        self.auth_service = auth_service
        self.object_storage = object_storage

    def index(self):
        result = self.customer_repository.index()
        for user in result:
            user.profile_image = self.object_storage.download_object(user.profile_image)
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA
        assert "phone_number" in obj_data, "phone number missing"

        phone_number = obj_data.get("phone_number")
        query_data = {"phone_number": phone_number}
        try:
            self.customer_repository.find(query_data)
        except AppException.NotFoundException:
            try:
                registered_customer = self.registration_repository.find(query_data)
            except AppException.NotFoundException:
                register_customer = self.registration_repository.create(query_data)
            else:
                self.registration_repository.delete(registered_customer.id)
                register_customer = self.registration_repository.create(query_data)
        else:
            raise AppException.ResourceExists(
                context=f"{OBJECT} with phone number {phone_number} exists"
            )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.registration_repository.update_by_id(
            register_customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[register_customer.phone_number],
                details={"verification_code": otp},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": register_customer.id}, 201)

    def confirm_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA

        customer_id = obj_data.get("id")
        otp = obj_data.get("token")
        try:
            registered_customer = self.registration_repository.find(
                {"id": customer_id, "otp_token": otp}
            )
        except AppException.NotFoundException:
            raise AppException.BadRequest(
                context="invalid user id or otp token passed",
            )

        if utc.localize(datetime.now()) > registered_customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(
                context="otp token has expired",
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
        assert obj_data, ASSERT_OBJECT_DATA

        obj_id = obj_data.pop("id")
        password_token = obj_data.pop("confirmation_token", None)

        try:
            registered_customer = self.registration_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.BadRequest(
                context=f"{OBJECT} with id {obj_id} does not exist"
            )
        else:
            if registered_customer.auth_token != password_token:
                raise AppException.BadRequest(context="invalid confirmation token")

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
        token_data = {"password_token": customer.auth_token, "id": customer.id}

        self.notify(
            EventNotificationHandler(
                publish=ServiceEventPublishing.new_customer.name,
                data=customer,
                schema=CustomerSchema,
            )
        )

        return Result(token_data, 200)

    def resend_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA

        obj_id = obj_data.get("id")
        customer = None
        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            try:
                self.registration_repository.find_by_id(obj_id)
            except AppException.NotFoundException:
                raise AppException.BadRequest(
                    context=f"unregistered {OBJECT}",
                )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        if customer:
            user = self.customer_repository.update_by_id(
                obj_id,
                {"otp_token": otp, "otp_token_expiration": otp_expiration},
            )
        else:
            user = self.registration_repository.update_by_id(
                obj_id,
                {"otp_token": otp, "otp_token_expiration": otp_expiration},
            )
        self.notify(
            SMSNotificationHandler(
                recipients=[user.phone_number],
                details={"verification_code": otp},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": obj_id}, 200)

    def login(self, obj_credential):
        assert obj_credential, ASSERT_OBJECT_DATA

        phone_number = obj_credential.get("phone_number")
        pin = obj_credential.get("pin")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        if customer.status.value not in ["blocked", "disabled"]:
            access_token = self.auth_service.get_token(
                {"username": customer.id, "password": pin}
            )
            if customer.status.value == "inactive":
                self.customer_repository.update_by_id(
                    str(customer.id), {"status": "first_time"}
                )
                user_data = keycloak_fields(str(customer.id), {"status": "first_time"})
                self.auth_service.update_user(user_data)
            customer.access_token = access_token.get("access_token")
            customer.refresh_token = access_token.get("refresh_token")
            return Result(customer, 200)
        raise AppException.NotFoundException(
            context=f"account {phone_number} has been {customer.status.value}",
        )

    def update(self, obj_id, obj_data):
        assert obj_id, ASSERT_OBJECT_ID
        assert obj_data, ASSERT_OBJECT_DATA

        profile_ext = obj_data.get("profile_image")
        if profile_ext not in [None, "null"]:
            obj_data["profile_image"] = f"{obj_id}.{profile_ext}"

        try:
            customer = self.customer_repository.update_by_id(obj_id, obj_data)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {obj_id} does not exists",
            )

        user_data = keycloak_fields(obj_id, obj_data)
        self.auth_service.update_user(user_data)

        # generate ceph server url to save profile image
        customer.pre_signed_post = self.object_storage.create_object(
            customer.profile_image
        )
        # #
        # # # generate ceph server url to retrieve profile image
        customer.profile_image = self.object_storage.download_object(
            customer.profile_image
        )

        return Result(customer, 200)

    def add_pin(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA

        pin = obj_data.get("pin")
        password_token = obj_data.get("password_token")
        try:
            customer = self.customer_repository.find({"auth_token": password_token})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(context="invalid password token")
        customer = self.customer_repository.update_by_id(customer.id, {"pin": pin})
        self.auth_service.reset_password(
            {"username": str(customer.id), "new_password": pin}
        )
        token = self.auth_service.get_token({"username": customer.id, "password": pin})
        token["id"] = customer.id
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={},
                meta={"type": "sms_notification", "subtype": "add_pin"},
            )
        )
        return Result(token, 200)

    def forgot_password(self, obj_phone):
        assert obj_phone, ASSERT_OBJECT_DATA

        phone_number = obj_phone.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"verification_code": otp},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": customer.id}, 200)

    def reset_password(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA

        customer_id = obj_data.get("id")
        new_pin = obj_data.get("new_pin")
        auth_token = obj_data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists"
            )
        if not customer.auth_token:
            raise AppException.ExpiredTokenException(context="password token not set")
        elif customer.auth_token != auth_token:
            raise AppException.ValidationException(context="Invalid token")

        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )

        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": None, "auth_token_expiration": None, "pin": new_pin},
        )

        return Result({"detail": "Pin reset done successfully"}, 200)

    def change_password(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA

        customer_id = obj_data.get("customer_id")
        new_pin = obj_data.get("new_pin")
        old_pin = obj_data.get("old_pin")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists"
            )

        self.auth_service.get_token({"username": customer_id, "password": old_pin})
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {
                "username": customer_id,
                "new_password": new_pin,
            }
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={},
                meta={"type": "sms_notification", "subtype": "change_password"},
            )
        )
        return Result({"detail": "Content reset done successfully"}, 200)

    def pin_process(self, data):
        assert data, ASSERT_OBJECT_DATA

        phone_number = data.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        if customer.pin:
            raise AppException.BadRequest(
                context=f"pin already set for account {phone_number}"
            )
        otp_token = 6666
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp_token, "otp_token_expiration": otp_token_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"verification_code": otp_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": customer.id}, 200)

    def reset_pin_process(self, data):
        assert data, ASSERT_OBJECT_DATA

        customer_data = {}
        customer_id = data.get("id")
        otp_pin = data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists"
            )
        if customer.otp_token != otp_pin:
            raise AppException.Unauthorized(
                context="invalid otp, please try again",
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
        assert data, ASSERT_OBJECT_DATA

        customer_id = data.get("customer_id")
        password_token = data.get("password_token")
        new_pin = data.get("pin")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists"
            )
        if customer.auth_token != password_token:
            raise AppException.Unauthorized(context="invalid token")
        self.customer_repository.update_by_id(customer_id, {"pin": new_pin})
        self.auth_service.reset_password(
            {"username": customer_id, "new_password": new_pin}
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={},
                meta={"type": "sms_notification", "subtype": "reset_pin"},
            )
        )
        return Result(customer, 200)

    def reset_phone_request(self, data):
        assert data, ASSERT_OBJECT_DATA

        phone_number = data.get("phone_number")
        try:
            customer = self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with phone number {phone_number} does not exists"
            )
        otp = 666666
        otp_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp, "otp_token_expiration": otp_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={"verification_code": otp},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": customer.id}, 200)

    def reset_phone(self, data):
        assert data, ASSERT_OBJECT_DATA

        phone_number = data.get("new_phone_number")
        auth_token = data.get("token")
        customer_id = data.get("customer_id")
        try:
            self.customer_repository.find({"phone_number": phone_number})
        except AppException.NotFoundException:
            try:
                customer = self.customer_repository.find_by_id(customer_id)
            except AppException.NotFoundException:
                raise AppException.NotFoundException(
                    context=f"{OBJECT} with id {customer_id} does not exists"
                )
        else:
            raise AppException.ResourceExists(
                context=f"{OBJECT} with phone number {phone_number} exists"
            )
        if customer.auth_token != auth_token:
            raise AppException.BadRequest(context="Invalid token")

        otp_token = 666666
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {
                "otp_token": otp_token,
                "otp_token_expiration": otp_token_expiration,
            },
        )
        data = {"id": customer.id, "phone_number": phone_number}
        self.notify(
            SMSNotificationHandler(
                recipients=[phone_number],
                details={"verification_code": otp_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result(data, 200)

    def request_phone_reset(self, data):
        customer_id = data.get("customer_id")
        phone_number = data.get("phone_number")
        otp = data.get("token")
        try:
            customer = self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists"
            )
        if not customer.otp_token or customer.otp_token != otp:
            raise AppException.BadRequest(context="Invalid token")
        self.customer_repository.update_by_id(
            customer_id, {"phone_number": phone_number}
        )
        user_data = keycloak_fields(customer_id, {"phone_number": phone_number})
        self.auth_service.update_user(user_data)
        # self.update(customer_id, {"phone_number": phone_number})
        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={},
                meta={"type": "sms_notification", "subtype": "change_phone"},
            )
        )
        return Result({"detail": "Phone reset done successfully"}, 200)

    def get_customer(self, obj_id):
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.get_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {obj_id} does not exists"
            )

        # generate ceph server url for retrieving profile image
        customer.profile_image = self.object_storage.download_object(
            customer.profile_image
        )
        return Result(customer, 200)

    def password_otp_confirmation(self, data):
        assert data, ASSERT_OBJECT_DATA

        customer_data = {}
        customer_id = data.get("id")
        otp = data.get("token")
        try:
            customer = self.customer_repository.find(
                {"id": customer_id, "otp_token": otp}
            )
        except AppException.NotFoundException:
            raise AppException.BadRequest(context="invalid user id or otp token passed")

        if utc.localize(datetime.now()) > customer.otp_token_expiration:
            raise AppException.ExpiredTokenException(context="otp token has expired")

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
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"customer with id {obj_id} does not exists",
            )
        self.customer_repository.delete(customer.id)
        self.auth_service.delete_user(obj_id)

        self.notify(
            SMSNotificationHandler(
                recipients=[customer.phone_number],
                details={},
                meta={"type": "sms_notification", "subtype": "delete_account"},
            )
        )
        return Result({}, 204)

    def refresh_token(self, obj_data):
        assert obj_data, ASSERT_OBJECT_DATA
        assert "id" in obj_data, ASSERT_OBJECT_ID

        customer_id = obj_data.get("id")
        refresh_token = obj_data.get("refresh_token")
        try:
            self.customer_repository.find_by_id(customer_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {customer_id} does not exists",
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
                context=f"{OBJECT} with phone number {phone_number} does not exist"
            )
        # generate ceph server url for retrieving profile image
        customer.profile_image = self.object_storage.download_object(
            customer.profile_image
        )
        return Result(customer, 200)

    # noinspection PyMethodMayBeStatic
    def customer_profile_images(self):

        profile_images = self.object_storage.list_objects()
        return Result(profile_images, 200)

    # noinspection PyMethodMayBeStatic
    def customer_profile_image(self, obj_id):
        assert obj_id, ASSERT_OBJECT_ID

        try:
            customer = self.customer_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context=f"{OBJECT} with id {obj_id} does not exist"
            )
        profile_images = self.object_storage.get_object(customer.profile_image)
        return Result(profile_images, 200)

    # below methods handles event subscription for the service
    def first_time_deposit(self, obj_data):
        customer_id = obj_data.get("customer_id")
        level = obj_data.get("product_name")
        try:
            self.customer_repository.update_by_id(customer_id, {"level": level})
        except AppException.NotFoundException:
            logger.error(
                f"event first time deposit with error: customer with id {customer_id} does not exist"  # noqa
            )
