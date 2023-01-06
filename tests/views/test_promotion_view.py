from datetime import datetime, timedelta
from unittest import mock

import pytest
from flask import url_for

from app.models import CustomerModel
from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestPromotionRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_promotion(self):
        with self.client:
            response = self.client.get(url_for("customer.get_promotion"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_promotion(self):
        with self.client:
            response = self.client.post(
                url_for("customer.create_promotion"),
                json=self.promotion_test_data.create_promotion,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("tittle", response_data)
            self.assertIn("description", response_data)
            self.assertIn("image", response_data)

