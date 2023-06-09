from datetime import datetime, timedelta
from unittest import mock

import pytest
from flask import url_for

from app.models import CustomerModel
from tests.base_test_case import BaseTestCase

expiration_time = datetime.now() + timedelta(minutes=5)


class TestCustomerRoutes(BaseTestCase):
    @pytest.mark.views
    def test_get_customers(self):
        with self.client:
            response = self.client.get(
                url_for("customer.get_customers"),
                query_string={"page": 1, "per_page": 1},
            )
            self.assert200(response)
            self.assertIsInstance(response.json, list)
            self.assertIsInstance(response.json[0], dict)

    @pytest.mark.views
    def test_create_customer_account(self):
        with self.client:
            response = self.client.post(
                url_for("customer.create_customer_account"),
                json=self.customer_test_data.register_customer,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertEqual(len(response_data), 1)
            self.assertIn("id", response_data)

    @pytest.mark.views
    def test_retailer_register_customer(self):
        with self.client:
            response = self.client.post(
                url_for("customer.retailer_register_customer"),
                json=self.customer_test_data.retailer_register_customer,
            )
            response_data = response.json
            self.assertStatus(response, 201)
            self.assertIsInstance(response_data, dict)
            self.assertEqual(len(response_data), 1)
            self.assertIn("id", response_data)

    @pytest.mark.views
    def test_confirm_token(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        with self.client:
            response = self.client.post(
                url_for("customer.confirm_token"),
                json={
                    "id": register.value.get("id"),
                    "token": "123456",
                },
            )
            response_data = response.json
            self.assert200(response)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)

    @pytest.mark.views
    def test_resend_token(self):
        with self.client:
            response = self.client.post(
                url_for("customer.resend_token"),
                json={"id": self.customer_model.id},
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIsNotNone(self.customer_model.otp_token)
            self.assertIsNotNone(self.customer_model.otp_token_expiration)
            self.assertIn("id", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.create_user")
    def test_add_information(self, mock_create_user):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "123456"}
        )
        data["confirmation_token"] = token.value.get("confirmation_token")
        mock_create_user.return_value = self.auth_service.create_user(
            self.customer_test_data.add_information
        )
        with self.client:
            response = self.client.post(
                url_for("customer.add_information"),
                json=data,
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIsNotNone(response_data.get("id"))
            self.assertIn("password_token", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_add_pin(self, mock_reset_password, mock_get_token):
        mock_reset_password.return_value = self.auth_service.reset_password(
            self.customer_model.id
        )
        mock_get_token.side_effect = self.auth_service.get_token
        with self.client:
            self.customer_model.auth_token = "auth_token"
            response = self.client.post(
                url_for("customer.add_pin"),
                json={"password_token": "auth_token", "pin": "0000"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.customer_model.verify_pin("1234"))
        self.assertTrue(self.customer_model.verify_pin("0000"))

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.update_user")
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    def test_login_customer(self, mock_get_token, mock_update_user):
        mock_get_token.side_effect = self.auth_service.get_token
        mock_update_user.return_value = self.auth_service.update_user(
            self.customer_test_data.update_customer
        )
        with self.client:
            response = self.client.post(
                url_for("customer.login"),
                json=self.customer_test_data.customer_credential,
            )
            response_data = response.json
            self.assert200(response)
            self.assertIsInstance(response_data, dict)
            self.assertIn("access_token", response_data)
            self.assertIn("refresh_token", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.update_user")
    def test_update_by_id(self, mock_update_user):
        mock_update_user.return_value = self.auth_service.update_user(
            self.customer_test_data.update_customer
        )
        with self.client:
            response = self.client.patch(
                url_for("customer.update_customer", customer_id=self.customer_model.id),
                json=self.customer_test_data.update_customer,
                headers=self.headers,
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIsNotNone(response_data.get("id"))
            self.assertNotIn("pin", response_data)
            self.assertNotEqual(
                response_data.get("status"),
                self.customer_test_data.existing_customer.get("status"),
            )

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.update_user")
    def test_set_profile_image(self, mock_update_user):
        mock_update_user.return_value = self.auth_service.update_user(
            self.customer_test_data.update_customer
        )
        with self.client:
            response = self.client.patch(
                url_for(
                    "customer.set_profile_image", customer_id=self.customer_model.id
                ),
                headers=self.headers,
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIsNotNone(response_data.get("id"))
            self.assertIn("pre_signed_post", response_data)

    @pytest.mark.views
    def test_find_customer(self):
        with self.client:
            response = self.client.get(
                url_for("customer.find_customer", customer_id=self.customer_model.id),
                headers=self.headers,
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertEqual(
                self.customer_model.phone_number,
                response_data.get("phone_number"),
            )

    @pytest.mark.views
    def test_forgot_password(self):
        with self.client:
            response = self.client.post(
                url_for("customer.forgot_password"),
                json={"phone_number": self.customer_model.phone_number},
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIsNotNone(self.customer_model.otp_token)
            self.assertIsNotNone(self.customer_model.otp_token_expiration)
            self.assertIn("id", response_data)

    @pytest.mark.views
    def test_password_otp_confirmation(self):
        with self.client:
            self.customer_model.otp_token = "123456"
            self.customer_model.otp_token_expiration = expiration_time
            response = self.client.post(
                url_for("customer.password_otp_confirmation"),
                json={
                    "id": self.customer_model.id,
                    "token": self.customer_model.otp_token,
                },
            )
            response_data = response.json
            self.assert200(response)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_reset_password(self, mock_reset_password):
        mock_reset_password.return_value = self.auth_service.reset_password(
            self.customer_model.id
        )
        with self.client:
            self.customer_model.auth_token = "123456"
            response = self.client.post(
                url_for("customer.reset_password"),
                json={
                    "id": self.customer_model.id,
                    "new_pin": "0000",
                    "token": "123456",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.customer_model.verify_pin("1234"))
        self.assertTrue(self.customer_model.verify_pin("0000"))

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_change_password(self, mock_reset_password, mock_get_token):
        mock_reset_password.return_value = self.auth_service.reset_password(
            self.customer_model.id
        )
        mock_get_token.return_value = self.auth_service.get_token(self.customer_model)
        data = {"old_pin": "1234", "new_pin": "0000"}
        with self.client:
            response = self.client.post(
                url_for("customer.change_password", customer_id=self.customer_model.id),
                json=data,
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.customer_model.verify_pin("1234"))
        self.assertTrue(self.customer_model.verify_pin("0000"))

    @pytest.mark.views
    def test_new_pin_request(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "123456"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        with self.client:
            response = self.client.post(
                url_for("customer.new_pin_request"),
                json=self.customer_test_data.register_customer,
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            register = CustomerModel.query.get(response_data.get("id"))
            self.assertIsNotNone(register.otp_token)
            self.assertIsNotNone(register.otp_token_expiration)

    @pytest.mark.views
    def test_verify_new_pin(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "123456"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        pin_process = self.customer_controller.new_pin_request(
            self.customer_test_data.register_customer
        )
        with self.client:
            response = self.client.post(
                url_for("customer.verify_new_pin"),
                json={"id": pin_process.value.get("id"), "token": "1234"},
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            self.assertIn("password_token", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_set_new_pin(self, mock_reset_password):
        mock_reset_password.return_value = self.auth_service.reset_password(
            self.customer_model.id
        )
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "123456"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        pin_process = self.customer_controller.new_pin_request(
            self.customer_test_data.register_customer
        )
        reset = self.customer_controller.verify_new_pin(
            {"id": pin_process.value.get("id"), "token": "1234"}
        )
        with self.client:
            response = self.client.post(
                url_for("customer.set_new_pin", customer_id=pin_process.value.get("id")),
                json={
                    "password_token": reset.value.get("password_token"),
                    "pin": "0000",
                },
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)

    @pytest.mark.views
    def test_change_phone_request(self):
        with self.client:
            response = self.client.post(
                url_for("customer.change_phone_request"),
                json={"phone_number": self.customer_model.phone_number},
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            self.assertIsNotNone(self.customer_model.otp_token)
            self.assertIsNotNone(self.customer_model.otp_token_expiration)

    @pytest.mark.views
    def test_verify_phone_change(self):
        with self.client:
            self.customer_controller.change_phone_request(
                {"phone_number": self.customer_model.phone_number}
            )
            token = self.customer_controller.password_otp_confirmation(
                {"id": self.customer_model.id, "token": "123456"}
            )
            response = self.client.post(
                url_for(
                    "customer.verify_phone_change", customer_id=self.customer_model.id
                ),
                json={
                    "new_phone_number": self.customer_test_data.register_customer.get(
                        "phone_number"
                    ),
                    "token": token.value.get("token"),
                },
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertIn("id", response_data)
            self.assertIn("phone_number", response_data)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.update_user")
    def test_change_phone(self, mock_update_user):
        mock_update_user.return_value = self.auth_service.update_user(
            self.customer_test_data.update_customer
        )
        with self.client:
            self.customer_controller.change_phone_request(
                {"phone_number": self.customer_model.phone_number}
            )
            token = self.customer_controller.password_otp_confirmation(
                {"id": self.customer_model.id, "token": "123456"}
            )
            self.customer_controller.verify_phone_change(
                {
                    "new_phone_number": self.customer_test_data.register_customer.get(
                        "phone_number"
                    ),
                    "customer_id": self.customer_model.id,
                    "token": token.value.get("token"),
                }
            )
            response = self.client.post(
                url_for("customer.change_phone", customer_id=self.customer_model.id),
                json={
                    "phone_number": self.customer_test_data.register_customer.get(
                        "phone_number"
                    ),
                    "token": "123456",
                },
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
            self.assertNotEqual(
                self.customer_model.phone_number,
                self.customer_test_data.existing_customer.get("phone_number"),
            )
            self.assertEqual(
                self.customer_model.phone_number,
                self.customer_test_data.register_customer.get("phone_number"),
            )

    @pytest.mark.views
    def test_find_by_phone_number(self):
        with self.client:
            response = self.client.get(
                url_for(
                    "customer.find_by_phone_number",
                    phone_number=self.customer_model.phone_number,
                ),
                headers=self.headers,
            )
            self.assert200(response)
            self.assertIsInstance(response.json, dict)

    @pytest.mark.views
    @mock.patch("app.services.keycloak_service.AuthService.refresh_token")
    def test_refresh_token(self, mock_refresh_token):
        data = {"id": self.customer_model.id, "refresh_token": self.refresh_token}
        mock_refresh_token.side_effect = self.auth_service.refresh_token
        with self.client:
            response = self.client.post(url_for("customer.refresh_token"), json=data)
            response_data = response.json
            self.assert200(response)
            self.assertIsInstance(response_data, dict)
            self.assertEqual(len(response_data), 3)
            self.assertIn("id", response_data)
            self.assertIn("access_token", response_data)
            self.assertIn("refresh_token", response_data)

    @pytest.mark.views
    @mock.patch("app.services.ceph_storage.CephObjectStorage.list")
    def test_saved_images(self, mock_storage):
        with self.client:
            mock_storage.side_effect = self.ceph_object_storage.list
            response = self.client.get(
                url_for("customer.saved_images"),
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, list)

    @pytest.mark.views
    @mock.patch("app.services.ceph_storage.CephObjectStorage.view")
    def test_saved_image(self, mock_storage):
        self.customer_model.profile_image = str(self.customer_model.id)
        with self.client:
            mock_storage.side_effect = self.ceph_object_storage.view
            response = self.client.get(
                url_for("customer.saved_image", customer_id=self.customer_model.id),
            )
            response_data = response.json
            self.assertStatus(response, 200)
            self.assertIsInstance(response_data, dict)
