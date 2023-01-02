import pytest

from app.models import LoginAttemptModel
from tests.base_test_case import BaseTestCase


class TestLoginAttemptModel(BaseTestCase):
    @pytest.mark.model
    def test_login_attempt_model(self):
        self.assertEqual(LoginAttemptModel.query.count(), 1)
        result = LoginAttemptModel.query.get(self.login_attempt_model.id)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "phone_number"))
        self.assertTrue(hasattr(result, "request_ip_address"))
        self.assertTrue(hasattr(result, "failed_login_attempts"))
        self.assertTrue(hasattr(result, "failed_login_time"))
        self.assertTrue(hasattr(result, "expires_in"))
        self.assertTrue(hasattr(result, "lockout_expiration"))
        self.assertTrue(hasattr(result, "status"))
        self.assertTrue(hasattr(result, "created"))
        self.assertTrue(hasattr(result, "modified"))
        self.assertIsNotNone(result.created)
        self.assertIsNotNone(result.modified)
