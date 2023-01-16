import pytest

from app.models.contact_us_model import ContactUsModel
from tests.base_test_case import BaseTestCase


class TestContactUsRepository(BaseTestCase):
    @pytest.mark.repository
    def test_create(self):
        result = self.contact_us_repository.create(
            self.contact_us_test_data.create_contact_us
        )
        self.assertIsInstance(result, ContactUsModel)
        self.assertIsNotNone(result.id)
