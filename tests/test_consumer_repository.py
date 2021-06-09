from tests.base_test_case import BaseTestCase


class TestConsumerRepository(BaseTestCase):
    customer_data = {
        "phone_number": "00233242583061",
        "first_name": "John",
        "last_name": "Doe",
        "id_type": "passport",
        "id_number": "4829h9445839",
    }

    def test_create(self):
        customer = self.customer_repository.create(
            self.customer_data
        )
        self.assertEqual(customer.first_name, "John")

