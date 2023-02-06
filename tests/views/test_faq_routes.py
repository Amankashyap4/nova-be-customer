from datetime import datetime, timedelta

import pytest
from flask import url_for

from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestFaqRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_faq(self):
        with self.client:
            response = self.client.get(url_for("customer.get_faq"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_faq(self):
        with self.client:
            response = self.client.post(
                url_for("customer.create_faq"),
                json=self.faq_test_data.create_faq,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            self.assertIn("question", response_data)
            self.assertIn("answer", response_data)

    @pytest.mark.view
    def test_update_faq(self):
        data = self.faq_test_data.update_faq
        with self.client:
            response = self.client.patch(
                url_for(
                    "customer.update_faq",
                    faq_id=self.faq_model.id,
                ),
                headers=self.headers,
                json=data,
            )
            response_data = response.json
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response_data)
            self.assertIsInstance(response_data, dict)

    @pytest.mark.view
    def test_delete_faq(self):
        with self.client:
            self.faq_model.id = self.faq_model.id
            response = self.client.delete(
                url_for(
                    "customer.delete_faq",
                    faq_id=self.faq_model.id,
                ),
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 204)
