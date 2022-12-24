import uuid

SERVICE_NAME = "test-service"
NAME = "test name"


class EventSubscriptionTestData:
    @property
    def cust_deposit(self):
        return {
            "service_name": SERVICE_NAME,
            "details": {
                "customer_id": "656f8140-3604-4b54-9149-d0473ac4ec23",
                "type_id": "S06",
            },
            "meta": {
                "event_action": "cust_deposit",
            },
        }

    @property
    def unhandled_event(self):
        return {
            "service_name": SERVICE_NAME,
            "details": {
                "id": str(uuid.uuid4()),
            },
            "meta": {
                "event_action": "unhandled",
            },
        }
