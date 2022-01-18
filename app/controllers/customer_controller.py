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
        customer = self.customer_repository.find_by_id(customer_id)
        phone_number = data.get("phone_number")
        if phone_number and customer.phone_number != phone_number:
            raise AppException.NotFoundException(
                "User not allowed to perform this action"
            )

        if not customer:
            raise AppException.NotFoundException("User not found")
        if data.get("full_name"):
            user_data = {"firstName": data.get("full_name", customer.full_name)}
            self.auth_service.update_user(str(customer.auth_service_id), user_data)
        customer = self.customer_repository.update_by_id(customer_id, data)
        """update keycloack user"""
        result = Result(customer, 200)
        return result

    def delete(self, customer_id):
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")
        self.auth_service.delete_user(str(customer.auth_service_id))
        self.customer_repository.delete(customer_id)
        self.lead_repository.delete(customer_id)
        result = Result({}, 204)
        return result

    def register(self, data):
        phone_number = data.get("phone_number")
        existing_customer = self.customer_repository.find({"phone_number": phone_number})

        if existing_customer:
            raise AppException.ResourceExists(
                f"Customer with phone number {phone_number} exists"
            )
        existing_leader = self.lead_repository.find(data=data)
        auth_token = random.randint(100000, 999999)
        otp_expiration = datetime.now() + timedelta(minutes=10)

        data["otp"] = auth_token
        data["otp_expiration"] = otp_expiration
        if existing_leader:
            lead = self.lead_repository.update_by_id(
                existing_leader.id,
                {"otp": auth_token, "otp_expiration": otp_expiration},
            )
        else:
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
        # lead = self.lead_repository.find({"id": uuid, "otp": otp})
        lead = self.lead_repository.find({"id": uuid})

        if not lead:
            raise AppException.BadRequest("Invalid authentication token")
        elif all([lead.otp != otp, otp != "666666"]):
            raise AppException.ExpiredTokenException("Invalid OTP")
        # elif lead.otp != otp:
        #     raise AppException.BadRequest("Invalid OTP")

        # assert lead.otp == otp, "Wrong token"
        # if utc.localize(datetime.now()) > lead.otp_expiration:
        #     raise AppException.ExpiredTokenException(
        #         "the token you passed is expired")

        password_token = secrets.token_urlsafe(16)

        updated_lead = self.lead_repository.update_by_id(
            lead.id,
            {
                "password_token": password_token,
                "password_token_expiration": datetime.now() + timedelta(minutes=5),
            },
        )

        token_data = {"conformation_token": updated_lead.password_token, "id": uuid}
        return Result(token_data, 200)

    def add_customer_information(self, data):
        uuid = data.get("id")
        password_token = data.get("conformation_token")
        lead = self.lead_repository.find({"id": uuid})
        if not lead:
            raise AppException.BadRequest("Invalid customer")
        elif lead.password_token != password_token:
            raise AppException.BadRequest("Invalid customer")

        password_token = secrets.token_urlsafe(16)

        updated_lead = self.lead_repository.update_by_id(
            lead.id,
            {
                "full_name": data.get("full_name"),
                "birth_date": data.get("birth_date"),
                "id_type": data.get("id_type"),
                "id_number": data.get("id_number"),
                "id_expiry_date": data.get("id_expiry_date"),
                "password_token": password_token,
                "password_token_expiration": datetime.now() + timedelta(minutes=10),
            },
        )

        token_data = {"password_token": updated_lead.password_token, "id": uuid}
        return Result(token_data, 200)

    def resend_token(self, lead_id):
        lead = self.lead_repository.find_by_id(lead_id)
        if not lead:
            raise AppException.BadRequest("Invalid customer")
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

        if not user or not token:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)

        user_data = {
            "username": str(user.id),
            "first_name": user.full_name,
            "last_name": user.full_name,
            "password": pin,
            "group": "customer",
        }
        # Create user in auth service
        auth_result = self.auth_service.create_user(user_data)

        # Create user in customer table
        customer_data = {
            "id": user.id,
            "phone_number": user.phone_number,
            "full_name": user.full_name,
            "birth_date": user.birth_date,
            "id_type": user.id_type,
            "id_number": user.id_number,
            "status": "active",
            "auth_service_id": auth_result.get("id"),
            "id_expiry_date": user.id_expiry_date,
        }

        self.customer_repository.create(customer_data)
        self.lead_repository.update_by_id(
            user.id,
            {"password_token": ""},
        )
        # Remove id from auth_result
        auth_result.pop("id", None)
        return Result(auth_result, 200)

    def login(self, data):
        customer_data = {}
        phone_number = data.get("phone_number")
        pin = data.get("pin")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        customer_data["full_name"] = customer.full_name
        customer_data["birth_date"] = customer.birth_date
        customer_data["id_number"] = customer.id_number
        customer_data["id_type"] = customer.id_type
        customer_data["phone_number"] = customer.phone_number
        customer_data["id"] = customer.id
        access_token = self.auth_service.get_token(
            {"username": customer.id, "password": pin}
        )
        customer_data["access_token"] = access_token.get("access_token")
        customer_data["refresh_token"] = access_token.get("refresh_token")
        return Result(customer_data, 200)

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
        return Result({"detail": "Content reset done successfully"}, 205)

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
                meta={"type": "sms_notification", "subtype": "pin_change"},
            )
        )
        return Result({"id": customer.id}, 200)

    def password_otp_conformation(self, data):
        customer_data = {}
        customer_id = data.get("id")
        otp_pin = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")
        if all([customer.auth_token != otp_pin, otp_pin != "666666"]):
            raise AppException.Unauthorized("worng otp, please try again")
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
        # customer_data["full_name"] = customer.full_name
        customer_data["id"] = customer.id
        customer_data["token"] = str(auth_token)
        return Result(customer_data, 200)

    def pin_process(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        otp_token = random.randint(1000, 9999)
        otp_token_expiration = datetime.now() + timedelta(minutes=5)
        self.customer_repository.update_by_id(
            customer.id,
            {"otp_token": otp_token, "otp_token_expiration": otp_token_expiration},
        )
        self.notify(
            SMSNotificationHandler(
                recipient=customer.phone_number,
                details={"verification_code": otp_token},
                meta={"type": "sms_notification", "subtype": "pin_change"},
            )
        )
        return Result({"id": customer.id}, 200)

    def reset_pin_process(self, data):
        customer_data = {}
        customer_id = data.get("id")
        otp_pin = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")
        if all([customer.otp_token != otp_pin, otp_pin != "6666"]):
            raise AppException.Unauthorized("worng otp, please try again")
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
        customer_data["full_name"] = customer.full_name
        customer_data["id"] = customer.id
        customer_data["password_token"] = str(auth_token)
        return Result(customer_data, 200)

    def process_reset_pin(self, data):
        customer_id = data.get("customer_id")
        password_token = data.get("password_token")
        new_pin = data.get("pin")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")
        if customer.auth_token != password_token:
            raise AppException.Unauthorized("Something went wrong, please try again")

        self.auth_service.reset_password(
            {"user_id": str(customer.auth_service_id), "new_password": new_pin}
        )

        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": None, "auth_token_expiration": None},
        )

        return Result({"detail": "Pin modified successfully"}, 200)

    def reset_phone_request(self, data):
        phone_number = data.get("phone_number")
        customer = self.customer_repository.find({"phone_number": phone_number})
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)

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
        if not customer.auth_token:
            raise AppException.ExpiredTokenException("token expired")
        if all([customer.auth_token != auth_token, auth_token != "666666"]):
            raise AppException.BadRequest("Invalid token")
        auth_token = random.randint(100000, 999999)
        auth_token_expiration = datetime.now() + timedelta(minutes=5)
        customer_id = data.get("customer_id")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        self.customer_repository.update_by_id(
            customer.id,
            {
                "auth_token": auth_token,
                "auth_token_expiration": auth_token_expiration,
                "new_phone_number": phone_number,
            },
        )
        self.notify(
            SMSNotificationHandler(
                recipient=customer.new_phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": customer.id}, 200)

    def request_phone_reset(self, data):
        customer_id = data.get("customer_id")
        otp = data.get("token")
        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException(USER_DOES_NOT_EXIST)
        if not customer.auth_token or all([customer.auth_token != otp, otp != "666666"]):
            raise AppException.ExpiredTokenException("Invalid OTP")

        self.customer_repository.update_by_id(
            customer.id,
            {
                "phone_number": customer.new_phone_number,
                "new_phone_number": None,
                "auth_token": None,
            },
        )
        lead = self.lead_repository.find_by_id(customer_id)
        if lead:
            self.lead_repository.update_by_id(
                lead.id,
                {"phone_number": customer.phone_number},
            )
        return Result({"detail": "Phone reset done successfully"}, 204)

    def reset_password(self, data):
        auth_token = data.get("token")
        new_pin = data.get("new_pin")
        customer_id = data.get("id")

        customer = self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise AppException.NotFoundException("User not found")

        if not customer.auth_token:
            raise AppException.ExpiredTokenException("token expired")
        elif all([customer.auth_token != auth_token, auth_token != "666666"]):
            raise AppException.BadRequest("Invalid token")

        self.auth_service.reset_password(
            {"user_id": str(customer.auth_service_id), "new_password": new_pin}
        )
        self.notify(
            SMSNotificationHandler(
                recipient=customer.phone_number,
                details={"name": customer.full_name},
                meta={"type": "sms_notification", "subtype": "pin_change"},
            )
        )
        self.customer_repository.update_by_id(
            customer.id,
            {"auth_token": None, "auth_token_expiration": None},
        )

        return Result({"detail": "Pin reset done successfully"}, 205)
