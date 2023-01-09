from datetime import datetime, timedelta
import pytest
from flask import url_for
from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestSafetyRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_safety(self):
        with self.client:
            response = self.client.get(url_for("customer.get_safety"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_safety(self):
        with self.client:
            response = self.client.post(
                url_for("customer.create_safety"),
                json=self.safety_test_data.create_safety,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("title", response_data)
            self.assertIn("description", response_data)
            self.assertIn("image", response_data)

