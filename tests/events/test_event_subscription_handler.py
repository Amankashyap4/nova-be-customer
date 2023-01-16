import uuid

import pytest
from flask import current_app

from app.enums import AccountStatusEnum
from tests.base_test_case import BaseTestCase


class TestEventSubscriptionHandler(BaseTestCase):
    @pytest.mark.event
    def test_first_time_deposit(self):
        data = self.event_subscription_test_data.cust_deposit.copy()
        data["details"]["customer_id"] = self.customer_model.id
        result = self.event_subscription_handler.event_handler(data)
        self.assertIsNone(result)
        self.assertIsNotNone(self.customer_model.level)
        self.assertEqual(self.customer_model.level, data["details"]["type_id"])
        self.assertEqual(self.customer_model.status, AccountStatusEnum.active)
        with self.assertLogs(logger=current_app.logger, level="CRITICAL") as log:
            data["details"]["customer_id"] = uuid.uuid4()
            self.event_subscription_handler.event_handler(data)
        self.assertEqual(len(log.output), 1)

    @pytest.mark.event
    def test_unhandled_event(self):
        with self.assertLogs(logger=current_app.logger, level="CRITICAL") as log:
            self.event_subscription_handler.event_handler(
                self.event_subscription_test_data.unhandled_event
            )
        self.assertEqual(len(log.output), 1)
        self.assertIn("event unhandled", log.output[0])
