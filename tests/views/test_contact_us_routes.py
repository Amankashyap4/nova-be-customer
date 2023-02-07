from datetime import datetime, timedelta

import pytest
from flask import url_for

from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestContactUsRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_contact_us(self):
        with self.client:
            response = self.client.get(url_for("contact_us.get_contact_us"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_contact_us(self):
        with self.client:
            response = self.client.post(
                url_for("contact_us.create_contact_us"),
                json=self.contact_us_test_data.create_contact_us,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            self.assertIn("email", response_data)
            self.assertIn("subject", response_data)
            self.assertIn("compose_email", response_data)

    @pytest.mark.view
    def test_update_contact_us(self):
        data = self.contact_us_test_data.update_contact_data
        with self.client:
            response = self.client.patch(
                url_for(
                    "contact_us.update_contact_us",
                    contact_id=self.contact_us_model.id,
                ),
                headers=self.headers,
                json=data,
            )
            response_data = response.json
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response_data)
            self.assertIsInstance(response_data, dict)

    @pytest.mark.view
    def test_delete_contact_us(self):
        with self.client:
            self.contact_us_model.id = self.contact_us_model.id
            response = self.client.delete(
                url_for(
                    "contact_us.delete_contact_us",
                    contact_id=self.contact_us_model.id,
                ),
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 204)
