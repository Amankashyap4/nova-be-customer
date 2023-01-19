import pytest

from app.models.faq_model import FaqModel
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    @pytest.mark.model
    def test_faq_model(self):
        self.assertEqual(FaqModel.query.count(), 1)
        result = FaqModel.query.get(self.faq_model.id)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "question"))
        self.assertTrue(hasattr(result, "answer"))
