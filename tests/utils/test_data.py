import datetime
import os
import uuid

APP_ROOT = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), ".."
)


class CustomerTestData:
    @property
    def existing_customer(self):
        return {
            "phone_number": "0500000000",
            "email": "test@example.com",
            "pin": "1234",
            "birth_date": datetime.datetime.utcnow().date(),
            "full_name": "string",
            "id_expiry_date": datetime.datetime.utcnow().date(),
            "id_number": "existing",
            "id_type": "national_id",
            "profile_image": f"{str(uuid.uuid4())}.jpg",
        }

    @property
    def existing_customer_history(self):
        return {
            "phone_number": "0500000000",
            "email": "test@example.com",
            "customer_id": uuid.uuid4(),
            "action": "phone_update",
            "valid_from": datetime.datetime.utcnow().date(),
            "valid_to": datetime.datetime.utcnow().date(),
        }

    @property
    def create_customer(self):
        return {
            "phone_number": "+233590000000",
            "email": "newtest@example.com",
            "pin": "1234",
            "birth_date": "2020-09-08",
            "full_name": "string",
            "id_expiry_date": "2020-09-08",
            "id_number": "create",
            "id_type": "national_id",
        }

    @property
    def register_customer(self):
        return {"phone_number": "0200000000"}

    @property
    def retailer_register_customer(self):
        return {
            "phone_number": "0200000000",
            "retailer_id": uuid.uuid4(),
        }

    @property
    def add_information(self):
        return {
            "birth_date": "2020-09-08",
            "full_name": "string",
            "id": uuid.uuid4(),
            "id_expiry_date": "2020-09-08",
            "id_number": "string",
            "id_type": "national_id",
        }

    @property
    def customer_credential(self):
        return {
            "phone_number": self.existing_customer.get("phone_number"),
            "pin": self.existing_customer.get("pin"),
        }

    @property
    def update_customer(self):
        return {"email": "customer@update.com", "profile_image": "jpg"}

    @property
    def first_time_deposit(self):
        return {
            "customer_id": str(uuid.uuid4()),
            "product_name": "6kg",
        }

    @property
    def new_customer_order(self):
        return {
            "id": str(uuid.uuid4()),
            "order_by_id": str(uuid.uuid4()),
            "order_status": "confirmed",
        }


class KeycloakTestData:
    @property
    def create_user(self):
        return {
            "email": "me@example.com",
            "username": str(uuid.uuid4()),
            "firstname": "john",
            "lastname": "doe",
            "password": "p@$$w0rd",
            "group": "nova-customer-gp",
        }
