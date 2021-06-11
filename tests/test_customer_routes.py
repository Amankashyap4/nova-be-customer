from app.definitions.exceptions import AppException
from tests.base_test_case import BaseTestCase


class TestCustomerRoutes(BaseTestCase):
    customer_data = {
        "phone_number": "00233242583061",
        "first_name": "John",
        "last_name": "Doe",
        "id_type": "passport",
        "id_number": "4829h9445839",
    }

    def test_create_route(self):
        with self.client:
            customer = self.client.post("/api/v1/customers/", json=self.customer_data)
            self.assertStatus(customer, 201)

    def test_create_route_error(self):
        with self.client:
            customer = self.client.post("/api/v1/customers/", json={})
            self.assertStatus(customer, 400)

    def test_update_route(self):
        customer = self.customer_repository.create(self.customer_data)
        self.assertEqual(customer.phone_number, self.customer_data["phone_number"])
        with self.client:
            customer_update = self.client.patch(
                f"/api/v1/customers/{customer.id}", json={"first_name": "Jane"}
            )

            self.assert200(customer_update)

        customer_search = self.customer_repository.find_by_id(customer.id)
        self.assertEqual(customer_search.first_name, "Jane")

    def test_delete_route(self):
        customer = self.customer_repository.create(self.customer_data)
        self.assertEqual(customer.phone_number, self.customer_data["phone_number"])

        with self.client:
            response = self.client.delete(f"/api/v1/customers/{customer.id}")
            self.assertStatus(response, 204)

        with self.assertRaises(AppException.ResourceDoesNotExist):
            self.customer_repository.find_by_id(customer.id)

    def test_show_route(self):
        customer = self.customer_repository.create(self.customer_data)
        self.assertEqual(customer.phone_number, self.customer_data["phone_number"])

        with self.client:
            response = self.client.get(f"/api/v1/customers/{customer.id}")
            self.assertStatus(response, 200)
            data = response.json

            self.assertEqual(
                data.get("first_name"), self.customer_data.get("first_name")
            )
