import os
from unittest.mock import patch

import fakeredis
from flask_testing import TestCase

from app import APP_ROOT, create_app, db
from app.controllers import CustomerController
from app.events import EventSubscriptionHandler
from app.models import CustomerHistoryModel, CustomerModel
from app.repositories import CustomerRepository, RegistrationRepository
from app.schema import CustomerSchema
from config import Config
from tests.utils.mock_auth_service import MockAuthService
from tests.utils.mock_ceph_storage_service import MockStorageService

from .utils.test_data import CustomerTestData, KeycloakTestData
from .utils.test_event_subscription_data import EventSubscriptionTestData


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app("config.TestingConfig")
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa: E501
        self.refresh_token = self.access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.setup_patches()
        self.instantiate_classes(self.redis)
        return app

    def instantiate_classes(self, redis_service):
        self.customer_schema = CustomerSchema()
        self.customer_repository = CustomerRepository(
            redis_service=redis_service, customer_schema=self.customer_schema
        )
        self.registration_repository = RegistrationRepository()
        self.auth_service = MockAuthService()
        self.object_storage = MockStorageService()
        self.customer_controller = CustomerController(
            customer_repository=self.customer_repository,
            registration_repository=self.registration_repository,
            auth_service=self.auth_service,
            object_storage=self.object_storage,
        )
        self.event_subscription_handler = EventSubscriptionHandler(
            customer_controller=self.customer_controller
        )
        self.customer_test_data = CustomerTestData()
        self.keycloak_test_data = KeycloakTestData()
        self.event_subscription_test_data = EventSubscriptionTestData()

    def setup_patches(self):
        self.redis_patcher = patch(
            "app.services.redis_service.redis_conn", fakeredis.FakeStrictRedis()
        )
        self.addCleanup(self.redis_patcher.stop)
        self.redis = self.redis_patcher.start()
        self.randint_patcher = patch(
            "app.controllers.customer_controller.random.randint", self.randint
        )
        self.addCleanup(self.randint_patcher.stop)
        self.randint_patcher.start()
        jwt_decode = patch("app.utils.auth.jwt.decode")
        self.addCleanup(jwt_decode.stop)
        jwt_decode.start()
        utc_patcher = patch(
            "app.controllers.customer_controller.utc.localize", self.utc_side_effect
        )
        self.addCleanup(utc_patcher.stop)
        utc_patcher.start()
        kafka_sms_patcher = patch(
            "app.notifications.sms_notification_handler.publish_to_kafka",
            self.dummy_kafka_method,
        )
        self.addCleanup(kafka_sms_patcher.stop)
        kafka_sms_patcher.start()
        kafka_email_patcher = patch(
            "app.notifications.email_notification_handler.publish_to_kafka",
            self.dummy_kafka_method,
        )
        self.addCleanup(kafka_email_patcher.stop)
        kafka_email_patcher.start()
        kafka_event_patcher = patch(
            "app.events.event_notification_handler.publish_to_kafka",
            self.dummy_kafka_method,
        )
        self.addCleanup(kafka_event_patcher.stop)
        kafka_event_patcher.start()

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()
        self.customer_model = CustomerModel(**self.customer_test_data.existing_customer)
        self.customer_history_model = CustomerHistoryModel(
            **self.customer_test_data.existing_customer_history
        )
        db.session.add(self.customer_model)
        db.session.add(self.customer_history_model)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()

        file = f"{Config.SQL_DB_NAME}.sqlite3"
        file_path = os.path.join(APP_ROOT, file)
        os.remove(file_path)

    def dummy_kafka_method(self, topic, value):
        return True

    def utc_side_effect(self, args):
        return args

    def randint(self, *args):
        return "666666"
