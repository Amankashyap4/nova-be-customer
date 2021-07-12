from app.definitions.exceptions import AppException
from app.utils import IDEnum
from tests.base_test_case import BaseTestCase


class TestCustomerController(BaseTestCase):
    customer_data = {
        "phone_number": "00233242583061",
        "first_name": "John",
        "last_name": "Doe",
        "id_type": "passport",
        "id_number": "4829h9445839",
        "auth_service_id": "d9247e56-7ad4-434d-8524-606e69d784c3",
    }

    def test_edit_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        updated_customer = self.customer_controller.update(
            customer.id,
            {
                "first_name": "Jane",
                "last_name": "Dew",
            },
        )

        updated_data = updated_customer.data.value

        self.assertEqual(updated_data.id, customer.id)
        self.assertEqual(updated_data.last_name, "Dew")
        self.assertEqual(updated_data.first_name, "Jane")

        customer_search = self.customer_repository.find_by_id(updated_data.id)

        self.assertEqual(customer_search.id, updated_data.id)
        self.assertEqual(customer_search.last_name, "Dew")

    def test_delete_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        self.customer_controller.delete(customer.id)

        with self.assertRaises(AppException.NotFoundException):
            self.customer_repository.find_by_id(customer.id)

    def test_show_customer(self):
        customer = self.customer_repository.create(self.customer_data)
        customer_search = self.customer_controller.show(customer.id)

        customer_values = customer_search.data.value
        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.last_name, "Doe")
        self.assertEqual(customer_values.id_type, IDEnum.passport)
