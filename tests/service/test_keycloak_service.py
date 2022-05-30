import uuid
from unittest import mock

import pytest

from app.core.exceptions import AppException
from app.services import AuthService
from tests.utils.mock_response import MockSideEffects

SERVER_URL = "localhost:8000"


class TestAuthService(MockSideEffects):
    _auth_service = AuthService()

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    def test_get_token(self, mock_requests):
        mock_requests.side_effect = self.get_token_response
        result = self._auth_service.get_token(
            {"username": "username", "password": "password"}
        )
        self.assertIsInstance(result, dict)
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.get_token(
                {"username": "username", "password": "password"}
            )
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    def test_refresh_token(self, mock_requests):
        mock_requests.side_effect = self.get_token_response
        result = self._auth_service.refresh_token(self.refresh_token)
        self.assertIsInstance(result, dict)
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.refresh_token(self.refresh_token)
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.AuthService.assign_group")
    @mock.patch("app.services.keycloak_service.AuthService.get_all_groups")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_user")
    @mock.patch("app.services.keycloak_service.AuthService.keycloak_post")
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    def test_create_user(
        self,
        mock_get_access_token,
        mock_keycloak_post,
        mock_get_keycloak_user,
        mock_get_all_groups,
        mock_assign_group,
    ):
        mock_get_access_token.side_effect = self.get_token_response
        mock_get_keycloak_user.return_value = {
            "id": str(uuid.uuid4()),
            "username": str(uuid.uuid4()),
        }
        mock_get_all_groups.return_value = self.mock_groups
        result = self._auth_service.create_user(self.keycloak_test_data.create_user)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        with self.assertRaises(AppException.OperationError) as group_error:
            mock_get_all_groups.return_value = {}
            self._auth_service.create_user(self.keycloak_test_data.create_user)
        self.assertTrue(group_error.exception)
        self.assert400(group_error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_user")
    def test_update_user(
        self,
        mock_get_keycloak_user,
        mock_get_access_token,
        mock_requests,
    ):
        mock_get_keycloak_user.return_value = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "username": str(uuid.uuid4()),
            "attributes": {"phone": "123456789"},
        }
        mock_requests.return_value = self.requests_response()
        result = self._auth_service.update_user(
            {"email": "me@example.com", "phone": "0000000000"}
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_user")
    def test_delete_user(self, mock_get_keycloak_user, mock_headers, mock_requests):
        mock_requests.return_value = self.requests_response()
        result = self._auth_service.delete_user(f"{SERVER_URL}/users")
        self.assertTrue(result)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.delete_user(f"{SERVER_URL}/users")
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_get_all_groups(self, mock_headers, mock_requests):
        mock_requests.side_effect = self.get_groups_response
        result = self._auth_service.get_all_groups()
        self.assertIsInstance(result, list)
        with self.assertRaises(AppException.KeyCloakAdminException) as group_error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.get_all_groups()
        self.assertTrue(group_error.exception)
        self.assert500(group_error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_get_keycloak_user(self, mock_headers, mock_requests):
        mock_requests.side_effect = self.get_keycloak_user_response
        result = self._auth_service.get_keycloak_user(str(uuid.uuid4()))
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        mock_requests.side_effect = self.no_keycloak_user_response
        response = self._auth_service.get_keycloak_user(str(uuid.uuid4()))
        self.assertIsNone(response)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.get_keycloak_user(str(uuid.uuid4()))
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_assign_group(self, mock_headers, mock_requests):
        mock_requests.side_effect = self.requests_response
        result = self._auth_service.assign_group(
            str(uuid.uuid4()), {"id": str(uuid.uuid4()), "name": "retailer"}
        )
        self.assertTrue(result)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.assign_group(
                str(uuid.uuid4()), {"id": str(uuid.uuid4()), "name": "retailer"}
            )
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_user")
    @mock.patch("app.services.keycloak_service.AuthService.keycloak_put")
    def test_reset_password(self, mock_keycloak_put, mock_get_keycloak_user):
        mock_keycloak_put.return_value = True
        result = self._auth_service.reset_password(
            {"username": str(uuid.uuid4()), "new_password": "2343"}
        )
        self.assertTrue(result)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    def test_keycloak_get_headers(self, mock_get_access_token):
        mock_get_access_token.side_effect = self.get_token
        result = self._auth_service.get_keycloak_headers()
        self.assertIsInstance(result, dict)
        self.assertIn("Authorization", result)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    @mock.patch("app.services.keycloak_service.requests.request")
    def test_keycloak_post(self, mock_requests, mock_get_access_token):
        self.status_code = 201
        mock_requests.side_effect = self.requests_response
        result = self._auth_service.keycloak_post(
            "localhost:3000/users", {"name": "john"}
        )
        self.assertEqual(result.status_code, 201)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_post_error(self, mock_headers, mock_requests):
        self.status_code = 400
        mock_requests.side_effect = self.requests_response
        with self.assertRaises(AppException.KeyCloakAdminException) as exist:
            self._auth_service.keycloak_post(f"{SERVER_URL}/users", {"name": "john"})
        self.assertTrue(exist.exception)
        self.assert400(exist.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_put(self, mock_headers, mock_requests):
        mock_requests.side_effect = self.requests_response
        result = self._auth_service.keycloak_put(
            "localhost:3000/users", {"name": "john"}
        )
        self.assertTrue(result)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_put_error(self, mock_headers, mock_request):
        self.status_code = 400
        mock_request.side_effect = self.requests_response
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            self._auth_service.keycloak_put(f"{SERVER_URL}/users", {"name": "john"})
        self.assertTrue(error.exception)
        self.assert400(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_delete(self, mock_headers, mock_requests):
        self.status_code = 204
        mock_requests.side_effect = self.requests_response
        result = self._auth_service.keycloak_delete(f"{SERVER_URL}/users")
        self.assertTrue(result)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    def test_realm_openid_config(self, mock_requests):
        mock_requests.side_effect = self.realm_openid_config
        response = self._auth_service.realm_openid_configuration()
        self.assertIsInstance(response, dict)
        with self.assertRaises(AppException.KeyCloakAdminException) as error:
            mock_requests.side_effect = self.keycloak_exception
            self._auth_service.realm_openid_configuration()
        self.assertTrue(error.exception)
        self.assert500(error.exception)

    @pytest.mark.auth_service
    @mock.patch("app.services.keycloak_service.requests.request")
    def test_request_exception(self, mock_request):
        with self.assertRaises(AppException.InternalServerError) as error:
            mock_request.side_effect = self.request_exception
            self._auth_service.get_token(
                {"username": "username", "password": "password"}
            )
        self.assertTrue(error.exception)
        self.assert500(error.exception)
