import pytest

from app.models.faq_model import FaqModel
from tests.base_test_case import BaseTestCase


class TestFaqRepository(BaseTestCase):
    @pytest.mark.repository
    def test_create(self):
        result = self.faq_repository.create(
            self.faq_test_data.create_faq,
        )
        self.assertIsInstance(result, FaqModel)
        self.assertIsNotNone(result.id)
