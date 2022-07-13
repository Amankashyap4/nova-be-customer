import pytest
from flask import current_app

from tests.base_test_case import BaseTestCase


class TestEventSubscriptionHandler(BaseTestCase):
    @pytest.mark.event
    def test_first_time_deposit(self):
        data = self.event_subscription_test_data.first_time_deposit.copy()
        data["details"]["customer_id"] = self.customer_model.id
        result = self.event_subscription_handler.event_handler(data)
        self.assertIsNone(result)
        self.assertIsNotNone(self.customer_model.level)
        self.assertEqual(self.customer_model.level, data["details"]["product_name"])

    @pytest.mark.event
    def test_new_customer_order(self):
        data = self.event_subscription_test_data.new_customer_order.copy()
        data["details"]["order_by_id"] = self.customer_model.id
        result = self.event_subscription_handler.event_handler(data)
        self.assertIsNone(result)

    @pytest.mark.event
    def test_unhandled_event(self):
        with self.assertLogs(logger=current_app.logger, level="CRITICAL") as log:
            self.event_subscription_handler.event_handler(
                self.event_subscription_test_data.unhandled_event
            )
        self.assertEqual(len(log.output), 1)
        self.assertIn("event unhandled", log.output[0])
