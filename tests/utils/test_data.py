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
            "value": "test@example.com",
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
        return {"email": "customer@update.com"}

    @property
    def cust_deposit(self):
        return {
            "customer_id": str(uuid.uuid4()),
            "type_id": "000",
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


class SafetyTestData:
    @property
    def create_safety(self):
        return {
            "title": "testing",
            "description": "testing",
            "image": "testing",
        }

    @property
    def existing_safety(self):
        return {
            "id": uuid.uuid4(),
            "title": "tittle1",
            "description": "description1",
            "image": "image1",
        }


class PromotionTestData:
    @property
    def create_promotion(self):
        return {
            "tittle": "testing",
            "description": "testing",
            "image": "testing",
        }

    @property
    def existing_promotion(self):
        return {
            "id": uuid.uuid4(),
            "tittle": "tittle1",
            "description": "description1",
            "image": "image1",
        }

    @property
    def update_promotion(self):
        return {"promotion": [{"id": uuid.uuid4(), "image": "image"}]}


class Contact_Us_TestData:
    @property
    def create_contact_us(self):
        return {
            "email": "string",
            "name": "string",
            "subject": "string",
            "compose_email": "string",
        }

    @property
    def existing_contact_us(self):
        return {
            "id": uuid.uuid4(),
            "email": "string",
            "name": "string",
            "subject": "string",
            "compose_email": "string",
        }

    @property
    def update_contact_us(self):
        return {"email": "email@abc"}

    @property
    def update_contact_data(self):
        return {"email": "email@abc"}


class FaqTestData:
    @property
    def create_faq(self):
        return {
            "question": "string",
            "answer": "string",
        }

    @property
    def existing_faq(self):
        return {
            "id": uuid.uuid4(),
            "question": "string",
            "answer": "string",
        }

    @property
    def update_faq(self):
        return {"question": "question1", "answer": "answer1"}
