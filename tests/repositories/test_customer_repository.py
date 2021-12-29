import uuid
from core.exceptions import AppException
from app.utils import IDEnum
from tests.utils.base_test_case import BaseTestCase
from app.repositories import CustomerRepository, LeadRepository


class TestCustomerRepository(BaseTestCase):
    auth_service_id = str(uuid.uuid4())
    lead_repository = LeadRepository()
    customer_repository = CustomerRepository()
    from datetime import datetime

    customer_data = {
        "phone_number": "00233242583061",
        "full_name": "John",
        "birth_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_expiry_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_type": "passport",
        "id_number": "4829h9445839",
        "auth_service_id": auth_service_id,
    }

    def test_1_create(self):
        customer = self.customer_repository.create(self.customer_data)
        self.assertEqual(customer.full_name, "John")
        self.customer_repository.delete(customer.id)

    def test_2_update(self):
        customer = self.customer_repository.create(self.customer_data)
        self.assertEqual(customer.full_name, "John")
        updated_customer = self.customer_repository.update_by_id(
            customer.id, {"full_name": "John Joe"}
        )
        self.assertEqual(updated_customer.full_name, "John Joe")
        self.customer_repository.delete(customer.id)

    def test_3_delete(self):
        customer = self.customer_repository.create(self.customer_data)
        customer_search = self.customer_repository.find_by_id(customer.id)

        self.assertEqual(customer_search.id, customer.id)
        self.assertEqual(customer_search.id_type, IDEnum.passport)

        self.customer_repository.delete(customer.id)

        with self.assertRaises(AppException.NotFoundException):
            self.customer_repository.find_by_id(customer.id)

    def test_4_required_fields(self):
        customer_data = {
            "full_name": "Doe",
            "id_type": "passport",
            "id_number": "4829h9445839",
        }

        with self.assertRaises(AppException.OperationError):
            self.customer_repository.create(customer_data)

    def test_5_duplicates(self):
        customer = self.customer_repository.create(self.customer_data)

        with self.assertRaises(AppException.OperationError):
            self.customer_repository.create(self.customer_data)
        self.customer_repository.delete(customer.id)
