import os
from unittest.mock import patch

import fakeredis
from flask_testing import TestCase

from app import APP_ROOT, create_app, db
from app.controllers import CustomerController
from app.controllers.contact_us_controller import ContactUsController
from app.controllers.faq_controller import FaqController
from app.controllers.promotion_controller import PromotionController
from app.controllers.safety_controller import SafetyController
from app.events import EventSubscriptionHandler
from app.models import CustomerHistoryModel, CustomerModel, LoginAttemptModel
from app.models.contact_us_model import ContactUsModel
from app.models.faq_model import FaqModel
from app.models.promotion_model import PromotionModel
from app.models.safety_model import SafetyModel
from app.repositories import (
    CustomerRepository,
    LoginAttemptRepository,
    RegistrationRepository, OwnedOtherBrandCylinderRepository,
)
from app.repositories.contact_us_repository import ContactUsRepository
from app.repositories.faq_repository import FaqRepository
from app.repositories.promotion_repository import PromotionRepository
from app.repositories.safety_repository import SafetyRepository
from app.schema import CustomerSchema, OwnedOtherBrandCylinderGetSchema
from app.schema.contact_us_schema import ContactUsGetSchema
from app.schema.faq_schema import FaqSchema
from app.schema.promotion_schema import PromotionSchema
from app.schema.safety_schema import SafetySchema
from config import Config
from tests.utils.mock_auth_service import MockAuthService
from tests.utils.mock_ceph_storage_service import MockCephObjectStorage

from .utils.test_data import (
    Contact_Us_TestData,
    CustomerTestData,
    FaqTestData,
    KeycloakTestData,
    PromotionTestData,
    SafetyTestData,
)
from .utils.test_event_subscription_data import EventSubscriptionTestData
from .utils.test_login_attempt_data import LoginAttemptTestData


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
        self.safety_schema = SafetySchema()
        self.promotion_schema = PromotionSchema()
        self.contact_us_schema = ContactUsGetSchema()
        self.faq_schema = FaqSchema()
        self.owned_otherbrand_cylinder_schema = OwnedOtherBrandCylinderGetSchema()
        self.customer_repository = CustomerRepository(
            redis_service=redis_service, customer_schema=self.customer_schema
        )
        self.safety_repository = SafetyRepository()
        self.promotion_repository = PromotionRepository()
        self.contact_us_repository = ContactUsRepository()
        self.faq_repository = FaqRepository()
        self.owned_otherbrand_cylinder_repository = OwnedOtherBrandCylinderRepository()
        self.login_attempt_repository = LoginAttemptRepository()
        self.registration_repository = RegistrationRepository()
        self.auth_service = MockAuthService()
        self.ceph_object_storage = MockCephObjectStorage()
        self.customer_controller = CustomerController(
            customer_repository=self.customer_repository,
            registration_repository=self.registration_repository,
            login_attempt_repository=self.login_attempt_repository,
            auth_service=self.auth_service,
            ceph_object_storage=self.ceph_object_storage,
        )
        self.safety_controller = SafetyController(
            safety_repository=self.safety_repository,
        )
        self.promotion_controller = PromotionController(
            promotion_repository=self.promotion_repository,
        )
        self.contact_us_controller = ContactUsController(
            contact_us_repository=self.contact_us_repository,
        )
        self.faq_controller = FaqController(
            faq_repository=self.faq_repository,
        )
        self.event_subscription_handler = EventSubscriptionHandler(
            customer_controller=self.customer_controller
        )
        self.customer_test_data = CustomerTestData()
        self.safety_test_data = SafetyTestData()
        self.promotion_test_data = PromotionTestData()
        self.faq_test_data = FaqTestData()
        self.contact_us_test_data = Contact_Us_TestData()
        self.keycloak_test_data = KeycloakTestData()
        self.login_attempt_test_data = LoginAttemptTestData()
        self.event_subscription_test_data = EventSubscriptionTestData()

    def setup_patches(self):
        self.redis_patcher = patch(
            "app.services.redis_service.redis_conn", fakeredis.FakeStrictRedis()
        )
        self.addCleanup(self.redis_patcher.stop)
        self.redis = self.redis_patcher.start()
        self.random_choices_patcher = patch(
            "app.controllers.customer_controller.random.choices", self.random_choices
        )
        self.addCleanup(self.random_choices_patcher.stop)
        self.random_choices_patcher.start()
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
        bug_report = patch("app.utils.log_config.MailHandler.send_mail")
        self.addCleanup(bug_report.stop)
        bug_report.start()

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()
        self.customer_model = CustomerModel(**self.customer_test_data.existing_customer)
        self.customer_history_model = CustomerHistoryModel(
            **self.customer_test_data.existing_customer_history
        )
        self.login_attempt_model = LoginAttemptModel(
            **self.login_attempt_test_data.existing_attempt
        )
        self.safety_model = SafetyModel(**self.safety_test_data.create_safety)
        self.promotion_model = PromotionModel(
            **self.promotion_test_data.existing_promotion
        )
        self.contact_us_model = ContactUsModel(
            **self.contact_us_test_data.existing_contact_us
        )
        self.faq_model = FaqModel(**self.faq_test_data.existing_faq)
        db.session.add(self.customer_model)
        db.session.add(self.safety_model)
        db.session.add(self.promotion_model)
        db.session.add(self.contact_us_model)
        db.session.add(self.faq_model)
        db.session.add(self.customer_history_model)
        db.session.add(self.login_attempt_model)
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

    # noinspection PyMethodMayBeStatic
    def dummy_kafka_method(self, topic, value):
        return True

    # noinspection PyMethodMayBeStatic
    def utc_side_effect(self, args):
        return args

    # noinspection PyMethodMayBeStatic
    def random_choices(self, *args, **kwargs):
        return "123456"
