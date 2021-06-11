from app.definitions.exceptions import AppException
from tests.base_test_case import BaseTestCase


class TestCustomerController(BaseTestCase):
    customer_data = {
        "phone_number": "00233242583061",
        "first_name": "John",
        "last_name": "Doe",
        "id_type": "passport",
        "id_number": "4829h9445839",
    }

    def test_create_customer(self):
        customer = self.customer_controller.create(self.customer_data)

        customer_search = self.customer_repository.find_by_id(customer.data.value.id)
        self.assertEqual(customer_search.id, customer.data.value.id)

    def test_edit_customer(self):
        customer = self.customer_controller.create(self.customer_data)

        updated_customer = self.customer_controller.update(
            customer.data.value.id,
            {
                "first_name": "Jane",
                "last_name": "Dew",
            },
        )

        updated_data = updated_customer.data.value

        self.assertEqual(updated_data.id, customer.data.value.id)
        self.assertEqual(updated_data.last_name, "Dew")
        self.assertEqual(updated_data.first_name, "Jane")

        customer_search = self.customer_repository.find_by_id(updated_data.id)

        self.assertEqual(customer_search.id, updated_data.id)
        self.assertEqual(customer_search.last_name, "Dew")

    def test_delete_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        self.customer_controller.delete(customer.id)

        with self.assertRaises(AppException.ResourceDoesNotExist):
            self.customer_repository.find_by_id(customer.id)

    def test_show_customer(self):
        customer = self.customer_repository.create(self.customer_data)
        customer_search = self.customer_controller.show(customer.id)

        customer_values = customer_search.data.value
        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.last_name, "Doe")
        self.assertEqual(customer_values.id_type, self.customer_data["id_type"])
