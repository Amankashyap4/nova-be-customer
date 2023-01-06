import pytest

from app.models.promotion_model import PromotionModel
from tests.base_test_case import BaseTestCase


class TestSafetyRepository(BaseTestCase):
    @pytest.mark.repository
    def test_create(self):
        result = self.promotion_repository.create(self.promotion_test_data.create_promotion)
        self.assertIsInstance(result, PromotionModel)
        self.assertIsNotNone(result.id)
