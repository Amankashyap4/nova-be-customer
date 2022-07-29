import uuid

SERVICE_NAME = "test-service"
NAME = "test name"


class EventSubscriptionTestData:
    @property
    def first_time_deposit(self):
        return {
            "service_name": SERVICE_NAME,
            "details": {
                "customer_id": "656f8140-3604-4b54-9149-d0473ac4ec23",
                "cylinder_size": "6kg",
            },
            "meta": {
                "event_action": "first_time_deposit",
            },
        }

    @property
    def new_customer_order(self):
        return {
            "service_name": SERVICE_NAME,
            "details": {
                "id": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
                "order_by_id": str(uuid.uuid4()),
                "order_status": "confirmed",
            },
            "meta": {
                "event_action": "new_customer_order",
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
