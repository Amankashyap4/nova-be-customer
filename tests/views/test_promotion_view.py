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
            response = self.client.get(url_for("promotion.get_promotion"))
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_promotion(self):
        with self.client:
            response = self.client.post(
                url_for("promotion.create_promotion"),
                json=self.promotion_test_data.create_promotion,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertIn("tittle", response_data)
            self.assertIn("description", response_data)
            self.assertIn("image", response_data)

    @pytest.mark.view
    def test_delete_promotion(self):
        with self.client:
            self.promotion_model.id = self.promotion_model.id
            response = self.client.delete(
                url_for(
                    "promotion.delete_promotion",
                    promotion_id=self.promotion_model.id,
                ),
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 204)

    @pytest.mark.view
    def test_update_promotion(self):
        data = self.promotion_test_data.update_promotion_data
        with self.client:
            response = self.client.patch(
                url_for(
                    "promotion.update_promotion",
                    promotion_id=self.promotion_model.id,
                ),
                headers=self.headers,
                json=data,
            )
            response_data = response.json
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response_data)
            self.assertIsInstance(response_data, dict)
