import uuid
from datetime import datetime, timedelta
from time import sleep

import pytest

from app.core import Result
from app.models.safety_model import SafetyModel
from tests.base_test_case import BaseTestCase



class TestSafetyController(BaseTestCase):
    @pytest.mark.controller
    def test_index(self):
        result = self.safety_controller.index()
        self.assertIsInstance(result, Result)
        self.assert200(result)
        self.assertIsInstance(result.value, list)
        self.assertIsInstance(result.value[0], SafetyModel)


    @pytest.mark.controller
    def test_register_safety(self):
        result = self.safety_controller.register(self.safety_test_data.create_safety)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 201)
        self.assertTrue(result.value, SafetyModel)

