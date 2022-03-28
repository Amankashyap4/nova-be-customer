import uuid
import random
from core.exceptions import AppException
from app.utils import IDEnum
from tests.utils.base_test_case import BaseTestCase
from app.repositories import CustomerRepository, LeadRepository
from unittest import mock


class TestCustomerController(BaseTestCase):

    auth_service_id = str(uuid.uuid4())

    from datetime import datetime

    lead_repository = LeadRepository()
    customer_repository = CustomerRepository()
    phone_number = random.randint(1000000000, 9999999999)

    customer_data = {
        "phone_number": str(phone_number),
        "full_name": "John",
        "birth_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_expiry_date": datetime.strptime("2021-06-22", "%Y-%m-%d"),
        "id_type": "passport",
        "id_number": "4829h94458312",
        "auth_service_id": auth_service_id,
    }

    @mock.patch("app.services.keycloak_service.AuthService.create_user")
    def test_pin_process(self, mock_create_user):
        mock_create_user.side_effect = self.auth_service.create_user

        self.customer_data.pop("auth_service_id")
        phone_number = self.customer_data.get("phone_number")
        lead = self.customer_controller.register({"phone_number": phone_number})
        leader = self.lead_repository.find_by_id(obj_id=lead.value.get("id"))
        token_response = self.customer_controller.confirm_token(
            {"id": leader.id, "token": leader.otp}
        )
        self.customer_data["id"] = leader.id
        self.customer_data["conformation_token"] = token_response.value.get(
            "conformation_token"
        )

        self.customer_controller.add_customer_information(self.customer_data)
        # After adding information by the customer user wants to discontinue the process.
        # user requests pin process
        pin_process_data_response = self.customer_controller.pin_process(
            {"phone_number": str(phone_number)}
        )
        self.assertStatus(pin_process_data_response, 200)
        self.assertEqual(pin_process_data_response.value.get("id"), leader.id)
        leader = self.lead_repository.find_by_id(obj_id=lead.value.get("id"))
        leader.otp, pin_process_data_response.value.get("id")

        # reset request pin
        reset_process_response = self.customer_controller.reset_pin_process(
            {"id": leader.id, "token": leader.otp}
        )
        self.assertStatus(reset_process_response, 200)
        self.assertEqual(reset_process_response.value.get("full_name"), leader.full_name)
        password_token = reset_process_response.value.get("password_token")
        id = reset_process_response.value.get("id")
        response = self.customer_controller.process_reset_pin(
            {"customer_id": id, "password_token": password_token, "new_pin": 1234}
        )
        self.assertStatus(response, 200)

    # change_password
    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    def test_change_password(self, mock_reset_password, mock_get_token):  # noqa
        mock_reset_password.side_effect = self.auth_service.reset_password
        mock_get_token.side_effect = self.auth_service.get_token
        customer = self.customer_repository.create(self.customer_data)
        response = self.customer_controller.change_password(
            {"customer_id": customer.id, "new_pin": "6666", "old_pin": "1234"}
        )
        self.assertStatus(response, 205)

    def test_1_edit_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        updated_customer = self.customer_repository.update_by_id(
            customer.id,
            {"full_name": "Jane"},
        )

        updated_data = updated_customer

        self.assertEqual(updated_data.id, customer.id)
        self.assertEqual(updated_data.full_name, "Jane")

        customer_search = self.customer_repository.find_by_id(updated_data.id)

        self.assertEqual(customer_search.id, updated_data.id)
        self.assertEqual(customer_search.full_name, "Jane")
        self.customer_repository.delete(customer.id)

    def test_2_delete_customer(self):
        customer = self.customer_repository.create(self.customer_data)

        self.customer_repository.delete(customer.id)

        with self.assertRaises(AppException.NotFoundException):
            self.customer_repository.find_by_id(customer.id)

    def test_3_show_customer(self):
        customer = self.customer_repository.create(self.customer_data)
        customer_values = self.customer_repository.find_by_id(customer.id)

        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.full_name, "John")
        self.assertEqual(customer_values.id_type, IDEnum.passport)
        self.customer_repository.delete(customer.id)

    def test_4_find_by_phone(self):
        customer = self.customer_repository.create(self.customer_data)

        customer_values = self.customer_repository.find(
            {"phone_number": customer.phone_number}
        )

        self.assertEqual(customer_values.id, customer.id)
        self.assertEqual(customer_values.full_name, "John")
        self.assertEqual(customer_values.id_type, IDEnum.passport)
        self.customer_repository.delete(customer.id)
