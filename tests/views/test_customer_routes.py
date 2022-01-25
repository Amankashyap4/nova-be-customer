import uuid
import random

from app.controllers import CustomerController
from app.services import AuthService
from app.repositories import CustomerRepository, LeadRepository

from tests.utils.base_test_case import BaseTestCase

from unittest import mock

phone_number = random.randint(1000000000, 9999999999)


class TestCustomerRoutes(BaseTestCase):
    auth_service_id = str(uuid.uuid4())

    lead_repository = LeadRepository()
    customer_repository = CustomerRepository()
    customer_controller = CustomerController(
        lead_repository=lead_repository,
        customer_repository=customer_repository,
        auth_service=AuthService(),
    )

    customer_data = {
        "full_name": "John Doe",
        "id_type": "passport",
        "id_number": "4829h9445839",
        "birth_date": "2021-06-22",
        "id_expiry_date": "2021-06-22",
    }
    pin_add = {"pin": "6666", "password_token": "7Y01WprMsxGSmoX1pf85Rw"}
    token_info = {}

    def test_a_create_route(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/account/register",
                json={"phone_number": str(phone_number)},
            )
            self.assertStatus(response, 201)
            data = response.json
            return data

    def test_b_confirm_token(self):
        """
        testcase for token conformation.
        """
        # self.test_a_create_route()
        lead = self.customer_controller.register({"phone_number": str(phone_number)})
        leader = self.lead_repository.find_by_id(obj_id=lead.value.get("id"))
        token_data = {"id": lead.value.get("id"), "token": leader.otp}
        with self.client:
            response = self.client.post(
                "/api/v1/customers/confirm-token", json=token_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            return data

    def test_c_add_information(self):
        """
        testcase for add user information
        """
        conformation_data = self.test_b_confirm_token()
        cust_data = {**self.customer_data, **conformation_data}
        with self.client:
            response = self.client.post(
                "/api/v1/customers/add-information", json=cust_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            return data

    @mock.patch("app.services.keycloak_service.AuthService.create_user")
    def test_d_add_pin(self, mock_create_user):
        """testcase to add pin"""
        token_info = self.test_c_add_information()

        mock_create_user.side_effect = self.auth_service.create_user
        self.pin_add["password_token"] = token_info.get("password_token")
        with self.client:
            response = self.client.post("/api/v1/customers/add-pin", json=self.pin_add)
            self.assertEqual(response.status_code, 200)

            data = response.json
            self.assertIn("access_token", data.keys())
            self.assertIn("refresh_token", data.keys())
            return data

    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    def test_e_token_login(self, mock_get_token):
        self.test_d_add_pin()
        mock_get_token.side_effect = self.auth_service.get_token
        with self.client:
            response = self.client.post(
                "/api/v1/customers/login",
                json={
                    "pin": "6666",
                    "phone_number": str(phone_number),
                },
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertIn("access_token", response.json.keys())
            self.assertIn("refresh_token", response.json.keys())
            self.assertEqual(str(phone_number), data.get("phone_number"))
            return data

    # @mock.patch("app.services.keycloak_service.AuthService.get_token")
    # @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    # @mock.patch("core.utils.auth.requests.get")
    # @mock.patch("core.utils.auth.jwt.decode")
    # def test_f_change_password(
    #     self, mock_jwt, mock_request, mock_reset_password, mock_get_token
    # ):
    #     mock_reset_password.side_effect = self.auth_service.reset_password
    #     mock_get_token.side_effect = self.auth_service.get_token
    #     mock_request.side_effect = [{"public_key": "keycloakpublickey"}]
    #
    #     logged_in_user = self.test_e_token_login()
    #     id = logged_in_user.get("id")
    #     self.required_roles["preferred_username"] = id
    #     mock_jwt.side_effect = self.required_roles_side_effect
    #     access_token = logged_in_user.get("access_token")
    #     with self.client:
    #         response = self.client.post(
    #             "/api/v1/customers/change-password/{}".format(id),
    #             headers={"Authorization": f"Bearer {access_token}"},
    #             json={"new_pin": "1414", "old_pin": "6666"},
    #         )
    #         self.assert_status(response, 205)
    #
    # @mock.patch("app.services.keycloak_service.AuthService.get_token")
    # @mock.patch("app.services.keycloak_service.AuthService.update_user")
    # @mock.patch("core.utils.auth.requests.get")
    # @mock.patch("core.utils.auth.jwt.decode")
    # def test_g_update_name(
    #     self, mock_jwt, mock_request, mock_update_password, mock_get_token
    # ):
    #     mock_update_password.side_effect = self.auth_service.update_user
    #     mock_get_token.side_effect = self.auth_service.get_token
    #     mock_request.side_effect = [{"public_key": "keycloakpublickey"}]
    #
    #     logged_in_user = self.test_e_token_login()
    #     id = logged_in_user.get("id")
    #     self.required_roles["preferred_username"] = id
    #     mock_jwt.side_effect = self.required_roles_side_effect
    #     access_token = logged_in_user.get("access_token")
    #
    #     with self.client:
    #         response = self.client.patch(
    #             "/api/v1/customers/accounts/{}".format(id),
    #             headers={"Authorization": f"Bearer {access_token}"},
    #             json={"full_name": "shashikant"},
    #         )
    #         self.assert_status(response, 200)
    #         data = response.json
    #         self.assertEqual("shashikant", data.get("full_name"))

    def test_h_forgot_password(self):
        self.test_d_add_pin()
        with self.client:
            response = self.client.post(
                "/api/v1/customers/forgot-password",
                json={"phone_number": str(phone_number)},
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_i_reset_password(self, mock_reset_password):
        mock_reset_password.side_effect = self.auth_service.reset_password
        data = self.test_h_forgot_password()
        customer = self.customer_repository.find_by_id(data.get("id"))
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-password",
                json={
                    "new_pin": "6666",
                    "token": customer.auth_token,
                    "id": data.get("id"),
                },
            )
            self.assert_status(response, 205)

    def test_j_pin_request(self):
        """
        pin process request
        """
        self.test_d_add_pin()
        with self.client:
            response = self.client.post(
                "/api/v1/customers/request-pin-process",
                json={"phone_number": str(phone_number)},
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    def test_k_request_reset_pin(self):
        """
        reset pin process
        """
        data = self.test_j_pin_request()
        customer = self.customer_repository.find_by_id(data.get("id"))
        with self.client:
            response = self.client.post(
                "/api/v1/customers/request-reset-pin",
                json={"id": customer.id, "token": customer.otp_token},
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_l_reset_pin(self, mock_reset_password):
        """reset pin"""
        # reset_password
        data = self.test_k_request_reset_pin()
        mock_reset_password.side_effect = self.auth_service.reset_password
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-pin/{}".format(data.get("id")),
                json={"password_token": data["password_token"], "pin": "6666"},
            )
            self.assert_status(response, 200)

    # @mock.patch("app.services.keycloak_service.AuthService.delete_user")
    # @mock.patch("app.services.keycloak_service.AuthService.get_token")
    # @mock.patch("core.utils.auth.requests.get")
    # @mock.patch("core.utils.auth.jwt.decode")
    # def test_m_remove_user(
    #     self, mock_jwt, mock_request_get, mock_delete_user, mock_get_token
    # ):
    #     mock_delete_user.side_effect = self.auth_service.delete_user
    #     mock_get_token.side_effect = self.auth_service.get_token
    #     mock_request_get.side_effect = [{"public_key": "keycloakpublickey"}]
    #     logged_in_user = self.test_e_token_login()
    #     id = logged_in_user.get("id")
    #     self.required_roles["preferred_username"] = id
    #     mock_jwt.side_effect = self.required_roles_side_effect
    #     access_token = logged_in_user.get("access_token")
    #     with self.client:
    #         response = self.client.delete(
    #             "/api/v1/customers/accounts/{}".format(id),
    #             headers={"Authorization": f"Bearer {access_token}"},
    #         )
    #         self.assert_status(response, 204)

    def test_m_forgot_password(self):
        """
        reset pin process
        """
        data = self.test_j_pin_request()
        customer = self.customer_repository.find_by_id(data.get("id"))
        with self.client:
            response = self.client.post(
                "/api/v1/customers/forgot-password",
                json={"phone_number": customer.phone_number},
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    def test_n_conform_pin(self):
        """
        reset pin process
        """
        data = self.test_m_forgot_password()
        customer = self.customer_repository.find_by_id(data.get("id"))
        with self.client:
            response = self.client.post(
                "/api/v1/customers/otp-conformation",
                json={"id": customer.id, "token": customer.auth_token},
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    @mock.patch("app.services.keycloak_service.AuthService.reset_password")
    def test_o_reset_pin(self, mock_reset_password):
        """
        reset pin process
        """
        mock_reset_password.side_effect = self.auth_service.reset_password
        data = self.test_n_conform_pin()
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-password",
                json={
                    "id": data.get("id"),
                    "token": data.get("token"),
                    "new_pin": "6666",
                },
            )
            self.assert_status(response, 205)
            data = response.json
            return data

    def test_o_request_reset_phone(self):
        """
        reset pin process
        """
        self.test_d_add_pin()
        customer = self.customer_repository.find({"phone_number": str(phone_number)})
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-phone-request",
                json={"phone_number": str(phone_number)},
            )
            self.assert_status(response, 200)
            data = response.json
            data["token"] = customer.auth_token
            return data

    def test_p_reset_phone(self):
        """
        reset phone
        """
        data = self.test_o_request_reset_phone()
        new_phone_number = random.randint(1000000000, 9999999999)
        customer = self.customer_repository.find({"phone_number": str(phone_number)})
        with self.client:
            response = self.client.post(
                f"/api/v1/customers/reset-phone/{customer.id}",
                json={
                    "new_phone_number": str(new_phone_number),
                    "token": data.get("token"),
                },
            )
            self.assert_status(response, 200)
            data = response.json
            return data

    def test_pq_reset_phone(self):
        """
        reset phone
        """
        data = self.test_o_request_reset_phone()
        customer = self.customer_repository.find({"phone_number": str(phone_number)})
        with self.client:
            response = self.client.post(
                f"/api/v1/customers/reset-phone/{customer.id}",
                json={
                    "new_phone_number": str(phone_number),
                    "token": data.get("token"),
                },
            )
            self.assert_status(response, 409)
            data = response.json
            return data

    def test_q_update_phone(self):
        """
        reset phone
        """
        data = self.test_p_reset_phone()
        customer = self.customer_repository.find_by_id(data)
        with self.client:
            response = self.client.post(
                f"/api/v1/customers/update-phone/{customer.id}",
                json={"token": customer.auth_token},
            )
            self.assert_status(response, 204)
