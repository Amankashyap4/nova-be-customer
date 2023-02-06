import pytest

from app.core import Result
from app.models.contact_us_model import ContactUsModel
from tests.base_test_case import BaseTestCase


class TestContactUsController(BaseTestCase):
    @pytest.mark.controller
    def test_index(self):
        result = self.contact_us_controller.index()
        self.assertIsInstance(result, Result)
        self.assert200(result)
        self.assertIsInstance(result.value, list)
        self.assertIsInstance(result.value[0], ContactUsModel)

    @pytest.mark.controller
    def test_register_contact_us(self):
        result = self.contact_us_controller.register(
            self.contact_us_test_data.create_contact_us
        )
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 201)
        self.assertTrue(result.value, ContactUsModel)

    @pytest.mark.controller
    def test_contact_us_update(self):
        result = self.contact_us_controller.update_contact_us(
            obj_id=self.contact_us_model.id,
            obj_data=self.contact_us_test_data.update_contact_us,
        )
        self.assertIsInstance(result, Result)

    @pytest.mark.controller
    def test_delete_contact_us(self):
        result = self.contact_us_controller.delete(self.contact_us_model.id)
        self.assertStatus(result, 204)
        self.assertIsInstance(result, Result)
        self.assertIsNone(result.value)
