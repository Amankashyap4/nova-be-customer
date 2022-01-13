import uuid
import random
from core.exceptions import AppException
from app.utils import IDEnum
from tests.utils.base_test_case import BaseTestCase
from app.repositories import CustomerRepository, LeadRepository


class TestCustomerController(BaseTestCase):

    auth_service_id = str(uuid.uuid4())

    from datetime import datetime

    lead_repository = LeadRepository()
    customer_repository = CustomerRepository()
    phone_number = random.randint(1000000000, 9999999999)

    customer_data = {
        "phone_number": str(phone_number),
        "full_name": "John",
        "birth_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_expiry_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_type": "passport",
        "id_number": "4829h94458312",
        "auth_service_id": auth_service_id,
    }

    def test_1_edit_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        updated_customer = self.customer_repository.update_by_id(
            customer.id,
            {"full_name": "Jane"},
        )

        updated_data = updated_customer

        self.assertEqual(updated_data.id, customer.id)
        self.assertEqual(updated_data.full_name, "Jane")

        customer_search = self.customer_repository.find_by_id(updated_data.id)

        self.assertEqual(customer_search.id, updated_data.id)
        self.assertEqual(customer_search.full_name, "Jane")
        self.customer_repository.delete(customer.id)

    def test_2_delete_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        self.customer_repository.delete(customer.id)

        with self.assertRaises(AppException.NotFoundException):
            self.customer_repository.find_by_id(customer.id)

    def test_3_show_customer(self):
        customer = self.customer_repository.create(self.customer_data)
        customer_values = self.customer_repository.find_by_id(customer.id)

        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.full_name, "John")
        self.assertEqual(customer_values.id_type, IDEnum.passport)
        self.customer_repository.delete(customer.id)

    def test_4_find_by_phone(self):
        customer = self.customer_repository.create(self.customer_data)

        customer_values = self.customer_repository.find(
            {"phone_number": customer.phone_number}
        )

        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.full_name, "John")
        self.assertEqual(customer_values.id_type, IDEnum.passport)
        self.customer_repository.delete(customer.id)
