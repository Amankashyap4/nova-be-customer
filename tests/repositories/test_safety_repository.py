import pytest

from app.models.safety_model import SafetyModel
from tests.base_test_case import BaseTestCase


class TestSafetyRepository(BaseTestCase):
    @pytest.mark.repository
    def test_create(self):
        result = self.safety_repository.create(self.safety_test_data.create_safety)
        self.assertIsInstance(result, SafetyModel)
        self.assertIsNotNone(result.id)
