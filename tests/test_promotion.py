from urllib import response

import pytest

from app.core import Result
from app.models.promotion_model import PromotionModel
from app.repositories.promotion_repository import PromotionRepository
from tests.base_test_case import BaseTestCase


class TestPromotionModel(BaseTestCase):
    @pytest.mark.model
    def test_promotion_model(self):
        self.assertEqual(PromotionModel.query.count(), 0)



class TestPromotionRepository(BaseTestCase):
    @pytest.mark.repository
    def test_index(self):
        result = PromotionRepository.index()
        self.assertIsInstance(result,Result)
        self.assertStatus(result, 200)




