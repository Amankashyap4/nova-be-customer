import pytest
from app.models.promotion_model import PromotionModel
from tests.base_test_case import BaseTestCase


class TestPromotionModel(BaseTestCase):
    @pytest.mark.model
    def test_promotion_model(self):
        self.assertEqual(PromotionModel.query.count(), 0)


