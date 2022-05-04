import os
from unittest.mock import patch

import fakeredis
from botocore.exceptions import ClientError
from flask_testing import TestCase

from app import APP_ROOT, create_app, db
from app.controllers import CustomerController
from app.models import CustomerModel
from app.repositories import CustomerRepository, RegistrationRepository
from config import Config
from tests.utils.mock_auth_service import MockAuthService

from .utils.test_data import CustomerTestData, KeycloakTestData


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
        self.customer_repository = CustomerRepository(redis_service=redis_service)
        self.registration_repository = RegistrationRepository()
        self.auth_service = MockAuthService()
        self.customer_controller = CustomerController(
            customer_repository=self.customer_repository,
            registration_repository=self.registration_repository,
            auth_service=self.auth_service,
        )
        self.customer_test_data = CustomerTestData()
        self.keycloak_test_data = KeycloakTestData()

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

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()
        self.customer_model = CustomerModel(**self.customer_test_data.existing_customer)
        db.session.add(self.customer_model)
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

    def botocore_client_error(self, *args, **kwargs):
        raise ClientError(error_response={}, operation_name="client_error")

    def botocore_client_list(self, *args, **kwargs):
        return {
            "Contents": [
                {
                    "ETag": "9be06213594c993e1957ed3980f8a3a0",
                    "Key": str(self.customer_model.id),
                    "LastModified": "Wed, 04 May 2022 15:19:59 GMT",
                    "Owner": {"DisplayName": "Nova Project", "ID": "nova"},
                    "Size": 3812,
                    "StorageClass": "STANDARD",
                }
            ]
        }

        # def decode_token(self, token, key, algorithms, audience, issuer):  # noqa
        #     return {
        #         "resource_access": {Config.KEYCLOAK_CLIENT_ID: {"roles": ["retailer"]}},
        #         "preferred_username": self.customer_model.id,
        #     }

    def utc_side_effect(self, args):  # noqa
        return args

    def randint(self, *args):
        return "666666"
