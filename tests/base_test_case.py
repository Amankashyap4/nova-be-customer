from flask_testing import TestCase
from app import create_app, db
from app.controllers import CustomerController
from app.repositories import CustomerRepository


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app("config.TestingConfig")
        self.customer_repository = CustomerRepository()
        self.customer_controller = CustomerController(
            customer_repository=self.customer_repository)
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
