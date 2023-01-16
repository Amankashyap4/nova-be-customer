import pytest

from app.core import Result
from app.models.promotion_model import PromotionModel
from tests.base_test_case import BaseTestCase


class TestPromotionController(BaseTestCase):
    @pytest.mark.controller
    def test_index(self):
        result = self.promotion_controller.index()
        self.assertIsInstance(result, Result)
        self.assert200(result)
        self.assertIsInstance(result.value, list)
        self.assertIsInstance(result.value[0], PromotionModel)

    @pytest.mark.controller
    def test_register_promotion(self):
        result = self.promotion_controller.register(
            self.promotion_test_data.create_promotion
        )
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 201)
        self.assertTrue(result.value, PromotionModel)

    @pytest.mark.controller
    def test_delete_promotion(self):
        result = self.promotion_controller.delete(self.promotion_model.id)
        self.assertStatus(result, 204)
        self.assertIsInstance(result, Result)
        self.assertIsNone(result.value)

    @pytest.mark.controller
    def test_promotion_update(self):
        result = self.promotion_controller.update_promotion(
            obj_id=self.promotion_model.id,
            obj_data=self.promotion_test_data.update_promotion,
        )
        self.assertIsInstance(result, Result)
