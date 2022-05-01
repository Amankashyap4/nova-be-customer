import pytest
from flask import url_for

from tests.base_test_case import BaseTestCase


class TestAuthService(BaseTestCase):
    @pytest.mark.auth_service
    def test_auth_no_token(self):
        with self.client:
            response = self.client.get(
                url_for("customer.find_customer", customer_id=self.customer_model.id),
            )
            response_data = response.json
            print()
            self.assertIsInstance(response_data, dict)
            self.assertIn("app_exception", response_data)
            self.assertIn("Unauthorized", response_data.values())
