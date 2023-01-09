import pytest

from app.models.promotion_model import PromotionModel
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    @pytest.mark.model
    def test_customer_model(self):
        self.assertEqual(PromotionModel.query.count(), 1)
        result = PromotionModel.query.get(self.promotion_model.id)
        self.assertTrue(hasattr(result, "tittle"))
        self.assertTrue(hasattr(result, "description"))
        self.assertTrue(hasattr(result, "image"))



