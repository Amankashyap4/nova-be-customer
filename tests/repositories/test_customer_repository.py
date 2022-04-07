import pytest

from app.models import CustomerModel
from tests.base_test_case import BaseTestCase


class TestCustomerRepository(BaseTestCase):
    @pytest.mark.repository
    def test_index(self):
        result = self.customer_repository.index()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], CustomerModel)

    @pytest.mark.repository
    def test_create(self):
        result = self.customer_repository.create(self.customer_test_data.create_customer)
        self.assertIsInstance(result, CustomerModel)
        self.assertIsNotNone(result.id)

    @pytest.mark.repository
    def test_get_by_id(self):
        result = self.customer_repository.get_by_id(self.customer_model.id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CustomerModel)
        self.assertEqual(self.customer_model, result)

    @pytest.mark.repository
    def test_update_by_id(self):
        result = self.customer_repository.update_by_id(
            self.customer_model.id, self.customer_test_data.update_customer
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CustomerModel)
        self.assertEqual(
            result.email,
            self.customer_test_data.update_customer.get("email"),
        )

    @pytest.mark.repository
    def test_delete(self):
        result = self.customer_repository.delete(self.customer_model.id)
        self.assertIsNone(result)
        self.assertEqual(CustomerModel.query.count(), 0)
