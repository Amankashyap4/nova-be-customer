import pytest

from app.models.safety_model import SafetyModel
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    @pytest.mark.model
    def test_safety_model(self):
        self.assertEqual(SafetyModel.query.count(), 1)
        result = SafetyModel.query.get(self.safety_model.id)
        self.assertTrue(hasattr(result, "title"))
        self.assertTrue(hasattr(result, "description"))
        self.assertTrue(hasattr(result, "image"))



