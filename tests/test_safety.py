import pyt
from app.models.safety_model import SafetyModel
from tests.base_test_case import BaseTestCase


class TestPromotionModel(BaseTestCase):
    @pytest.mark.model
    def test_safety_model(self):
        self.assertEqual(SafetyModel.query.count(), 0)


