import pytest

from app.models import CustomerModel
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    @pytest.mark.model
    def test_customer_model(self):
        self.assertEqual(CustomerModel.query.count(), 1)
        result = CustomerModel.query.get(self.customer_model.id)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "phone_number"))
        self.assertTrue(hasattr(result, "full_name"))
        self.assertTrue(hasattr(result, "email"))
        self.assertTrue(hasattr(result, "id_type"))
        self.assertTrue(hasattr(result, "id_number"))
        self.assertTrue(hasattr(result, "birth_date"))
        self.assertTrue(hasattr(result, "id_expiry_date"))
        self.assertTrue(hasattr(result, "hash_pin"))
        self.assertTrue(hasattr(result, "status"))
        self.assertTrue(hasattr(result, "otp_token"))
        self.assertTrue(hasattr(result, "otp_token_expiration"))
        self.assertTrue(hasattr(result, "auth_token"))
        self.assertTrue(hasattr(result, "auth_token_expiration"))
        self.assertTrue(hasattr(result, "auth_service_id"))
        self.assertTrue(hasattr(result, "profile_image"))
        self.assertTrue(hasattr(result, "created"))
        self.assertTrue(hasattr(result, "modified"))
        self.assertIsNotNone(result.created)
        self.assertIsNotNone(result.modified)
