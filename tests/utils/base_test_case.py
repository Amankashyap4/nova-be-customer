import os
from flask_testing import TestCase
from app import create_app, db
from app.controllers import CustomerController
from app.repositories import CustomerRepository, LeadRepository
from tests import MockAuthService
from config import Config
from unittest.mock import patch


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app("config.TestingConfig")
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI="sqlite:///"
            + os.path.join(app.instance_path, "test.db?check_same_thread=False"),
        )

        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa: E501
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        patcher = patch(
            "app.core.utils.auth.jwt.decode", self.required_roles_side_effect
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        self.customer_repository = CustomerRepository()
        self.lead_repository = LeadRepository()
        self.auth_service = MockAuthService()
        self.customer_controller = CustomerController(
            customer_repository=self.customer_repository,
            auth_service=self.auth_service,
            lead_repository=self.lead_repository,
        )
        return app

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()

        path = self.app.instance_path
        file = os.path.join(path, "test.db")
        os.remove(file)

    def dummy_kafka_method(self, topic, value):
        return True

    def required_roles_side_effect(  # noqa
        self, token, key, algorithms, audience, issuer
    ):
        return {
            "realm_access": {
                "roles": [
                    f"{Config.APP_NAME}_change_password",
                    f"{Config.APP_NAME}_delete_customer",
                    f"{Config.APP_NAME}_show_customer",
                    f"{Config.APP_NAME}_update_customer",
                ]
            },
        }
