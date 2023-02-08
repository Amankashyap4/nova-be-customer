from datetime import datetime, timedelta
import pytest
from flask import url_for
from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestSafetyRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_safety(self):
        with self.client:
            response = self.client.get(url_for("safety.get_safety"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_safety(self):
        with self.client:
            response = self.client.post(
                url_for("safety.create_safety"),
                json=self.safety_test_data.create_safety,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("title", response_data)
            self.assertIn("description", response_data)
            self.assertIn("image", response_data)

    @pytest.mark.view
    def test_delete_safety(self):
        with self.client:
            self.safety_model.id = self.safety_model.id
            response = self.client.delete(
                url_for(
                    "safety.delete_safety",
                    safety_id=self.safety_model.id,
                ),
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 204)

    @pytest.mark.view
    def test_update_safety(self):
        data = self.safety_test_data.update_safety_data
        with self.client:
            response = self.client.patch(
                url_for(
                    "safety.update_safety",
                    safety_id=self.safety_model.id,
                ),
                headers=self.headers,
                json=data,
            )
            response_data = response.json
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response_data)
            self.assertIsInstance(response_data, dict)
