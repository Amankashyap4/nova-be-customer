import uuid
from unittest import mock
from core.exceptions import AppException
from tests.utils.base_test_case import BaseTestCase
from app.repositories import CustomerRepository, LeadRepository

import random

phone_number = random.randint(1000000000, 9999999999)


class TestCustomerRoutes(BaseTestCase):

    auth_service_id = str(uuid.uuid4())

    lead_repository = LeadRepository()
    customer_repository = CustomerRepository()

    customer_data = {}
    if not customer_data:
        customer_data = {
            "phone_number": str(phone_number)
        }

    token_data = {
        "id": "991d6ed53abc4fa4b579a2abcab4bbc7",
        "token": "893470"
    }
    customer_info = {
        "conformation_token": "9oU-vaHmauxi9sqkyZ1YsA",
        "id": "a1f271bf-b27d-4c3b-a78b-79a76af94701",
        "full_name": "gsm",
        "birth_date": "2021-06-22",
        "id_expiry_date": "2021-06-22",
        "id_type": "national_id",
        "id_number": "123456"
    }
    pin_add = {
        "pin": "6666",
        "password_token": "7Y01WprMsxGSmoX1pf85Rw"
    }
    user_data = {"full_name": "gsm",
                 "birth_date": "2021-06-22",
                 "id_expiry_date": "2021-06-22",
                 "id_type": "national_id",
                 "id_number": "123456"
                 }

    def test_a_create_route(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/account/", json=self.customer_data
            )
            self.assertStatus(response, 201)
            data = response.json
            self.user_data['id'] = data.get('id')

    def test_b_confirm_token(self):
        lead = self.lead_repository.find_by_id(self.user_data['id'])
        self.token_data['token'] = lead.otp
        self.token_data['id'] = lead.id
        with self.client:
            response = self.client.post(
                "/api/v1/customers/confirm-token", json=self.token_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.user_data['conformation_token'] = data.get('conformation_token')

    def test_c_add_information(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/add-information", json=self.user_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.pin_add['password_token'] = data.get('password_token')

    def test_d_confirm_add_pin(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/add-pin", json=self.pin_add
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            return data

    def test_e_token_login(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/token-login", json={
                    "pin": "6666",
                    "phone_number": self.customer_data.get('phone_number')
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.user_data["access_token"] = data.get('access_token')
            self.user_data["refresh_token"] = data.get('refresh_token')
            self.user_data['id'] = data.get('id')
            self.user_data['phone_number'] = data.get('phone_number')
            self.user_data['full_name'] = data.get('full_name')
            return data

    # def test_f_update_phone(self):
    #     with self.client:
    #         response = self.client.post(
    #             "/api/v1/customers/reset-phone/{}".format(self.user_data['id']),
    #             headers={
    #                 "Authorization": f"Bearer {self.user_data['access_token']}"},
    #             json={"phone_number": "9890225747"},
    #         )
    #         self.assert_status(response, 200)
    #         data = response.json
    #         self.user_data['id'] = data.get('id')
    #
    # def test_g_update_phone(self):
    #     customer = self.customer_repository.find_by_id(self.user_data['id'])
    #     with self.client:
    #         response = self.client.post(
    #             "/api/v1/customers/update-phone/{}".format(self.user_data['id']),
    #             headers={
    #                 "Authorization": f"Bearer {self.user_data['access_token']}"},
    #             json={"token": customer.auth_token},
    #         )
    #         self.assert_status(response, 204)

    def test_h_change_password(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/change-password/{}".format(
                    self.user_data['id']),
                headers={
                    "Authorization": f"Bearer {self.user_data['access_token']}"},
                json={"new_pin": "1414", "old_pin": "6666"},
            )
            self.assert_status(response, 205)
            data = response.json
            self.user_data['full_name'] = data.get('full_name')

    def test_i_update_name(self):
        with self.client:
            response = self.client.patch(
                "/api/v1/customers/accounts/{}".format(self.user_data['id']),
                headers={
                    "Authorization": f"Bearer {self.user_data['access_token']}"},
                json={"full_name": "shashikant"},
            )
            self.assert_status(response, 200)
            data = response.json
            self.user_data['full_name'] = data.get('full_name')

    def test_j_forgot_password(self):
        with self.client:
            response = self.client.post(
                "/api/v1/customers/forgot-password", json={
                    "phone_number": self.customer_data.get('phone_number')
                }
            )
            self.assert_status(response, 200)
            data = response.json
            self.user_data['id'] = data.get('id')

    def test_k_reset_password(self):
        customer = self.customer_repository.find_by_id(self.user_data.get('id'))
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-password", json={
                    "new_pin": "6666",
                    "token": customer.auth_token,
                    "id": self.user_data['id']
                }
            )
            self.assert_status(response, 205)
            data = response.json

    def test_l_pin_request(self):
        """
        pin process request
        """
        with self.client:
            response = self.client.post(
                "/api/v1/customers/pin-request", json={
                    "phone_number": self.customer_data.get("phone_number")
                }
            )
            self.assert_status(response, 200)
            data = response.json
            self.user_data['id'] = data.get('id')

    def test_m_request_reset_pin(self):
        """
        reset pin process
        """
        customer = self.customer_repository.find_by_id(self.user_data.get('id')
                                                       )
        with self.client:
            response = self.client.post(
                "/api/v1/customers/request-reset-pin", json={
                    "id": customer.id,
                    "token": customer.otp_token
                }
            )
            self.assert_status(response, 200)
            data = response.json
            self.user_data['id'] = data.get('id')
            self.user_data['password_token'] = data.get('password_token')

    def test_n_reset_pin(self):
        """reset pin"""
        with self.client:
            response = self.client.post(
                "/api/v1/customers/reset-pin/{}".format(
                    self.user_data.get('id')),
                json={"password_token": self.user_data['password_token'],
                      "pin": "6666"
                      },
            )
            self.assert_status(response, 200)


    def test_o_remove_user(self):
        with self.client:
            response = self.client.delete(
                "/api/v1/customers/accounts/{}".format(
                    self.user_data['id']),
                headers={
                    "Authorization": f"Bearer {self.user_data['access_token']}"
                }
            )
            self.assert_status(response, 204)
