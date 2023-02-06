import pytest

from app.core import Result
from app.models.faq_model import FaqModel
from tests.base_test_case import BaseTestCase


class TestFaqController(BaseTestCase):
    @pytest.mark.controller
    def test_all_faq(self):
        result = self.faq_controller.all_faq()
        self.assertIsInstance(result, Result)
        self.assert200(result)
        self.assertIsInstance(result.value, list)
        self.assertIsInstance(result.value[0], FaqModel)

    @pytest.mark.controller
    def test_register_faq(self):
        result = self.faq_controller.register_faq(self.faq_test_data.create_faq)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 201)
        self.assertTrue(result.value, FaqModel)

    @pytest.mark.controller
    def test_update_faq(self):
        result = self.faq_controller.update_faq(
            obj_id=self.faq_model.id,
            obj_data=self.faq_test_data.update_faq,
        )
        self.assertIsInstance(result, Result)

    @pytest.mark.controller
    def test_delete_faq(self):
        result = self.faq_controller.delete_faq(self.faq_model.id)
        self.assertStatus(result, 204)
        self.assertIsInstance(result, Result)
        self.assertIsNone(result.value)
