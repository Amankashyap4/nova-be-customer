import pytest

from app.models.contact_us_model import ContactUsModel
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    @pytest.mark.model
    def test_contact_us_model(self):
        self.assertEqual(ContactUsModel.query.count(), 1)
        result = ContactUsModel.query.get(self.contact_us_model.id)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "name"))
        self.assertTrue(hasattr(result, "email"))
        self.assertTrue(hasattr(result, "compose_email"))
        self.assertTrue(hasattr(result, "subject"))
