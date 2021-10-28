import uuid
from unittest import mock

from app.services import AuthService
from core.exceptions import AppException
from tests.utils.base_test_case import BaseTestCase


class MockResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class TestAuthService(BaseTestCase):
    _auth_service = AuthService()

    mock_groups = [
        {"id": str(uuid.uuid4()), "name": "customer"},
        {"id": str(uuid.uuid4()), "name": "distributor"},
    ]

    @mock.patch("app.services.keycloak_service.requests.post")
    def test_get_token(self, mock_request):
        # mock post request result
        mock_request.side_effect = self.get_token_post_mock
        result = self._auth_service.get_token(
            {"username": "myusername", "password": "mypassword"}
        )
        self.assertIn("access_token", result)

    @mock.patch("app.services.keycloak_service.requests.post")
    def test_refresh_token(self, mock_request):
        mock_request.side_effect = self.get_token_post_mock
        result = self._auth_service.refresh_token(self.refresh_token)
        self.assertIn("access_token", result)

    @mock.patch("app.services.keycloak_service.AuthService.get_token")
    @mock.patch("app.services.keycloak_service.AuthService.keycloak_post")
    @mock.patch(
        "app.services.keycloak_service.AuthService.get_keycloak_user",
        return_value={"id": str(uuid.uuid4())},
    )
    @mock.patch(
        "app.services.keycloak_service.AuthService.get_all_groups",
        return_value=mock_groups,
    )
    @mock.patch("app.services.keycloak_service.AuthService.assign_group")
    def test_create_user(
        self,
        mock_assign_group,
        mock_get_all_groups,
        mock_get_keycloak_user,
        mock_keycloak_post,
        mock_get_token,
    ):
        mock_get_token.side_effect = self.get_token_mock
        result = self._auth_service.create_user(
            {
                "email": "me@example.com",
                "username": str(uuid.uuid4()),
                "firstname": "john",
                "lastname": "doe",
                "password": "p@$$w0rd",
                "group": "customer",
            }
        )
        self.assertIn("access_token", result)

    @mock.patch("app.services.keycloak_service.requests.get")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_get_all_groups(self, mock_headers, mock_request):
        mock_request.side_effect = self.get_groups_side_effect
        result = self._auth_service.get_all_groups()
        self.assertIsInstance(result, list)

    @mock.patch("app.services.keycloak_service.requests.get")
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_get_keycloak_user(self, mock_headers, mock_request):
        mock_request.side_effect = self.get_keycloak_user_side_effect
        result = self._auth_service.get_keycloak_user(str(uuid.uuid4()))
        self.assertIn("id", result)

    @mock.patch(
        "app.services.keycloak_service.requests.put",
        return_value=MockResponse(status_code=200, json=None),
    )
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_assign_group(self, mock_headers, mock_request):
        result = self._auth_service.assign_group(
            str(uuid.uuid4()), {"id": str(uuid.uuid4()), "name": "customer"}
        )
        self.assertTrue(result)

    @mock.patch(
        "app.services.keycloak_service.AuthService.keycloak_put", return_value=True
    )
    def test_reset_password(self, mock_request):
        result = self._auth_service.reset_password(
            {"user_id": str(uuid.uuid4()), "new_password": "2343"}
        )
        self.assertTrue(result)

    @mock.patch(
        "app.services.keycloak_service.requests.post",
        return_value=MockResponse(status_code=200, json=None),
    )
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_post(self, mock_headers, mock_request):
        result = self._auth_service.keycloak_post(
            "localhost:3000/users", {"name": "john"}
        )
        self.assertTrue(result)

    @mock.patch(
        "app.services.keycloak_service.requests.post",
        return_value=MockResponse(status_code=400, json={"errorMessage": "user exists"}),
    )
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_post_error(self, mock_headers, mock_request):
        with self.assertRaises(AppException.KeyCloakAdminException):
            self._auth_service.keycloak_post("localhost:3000/users", {"name": "john"})

    @mock.patch(
        "app.services.keycloak_service.requests.put",
        return_value=MockResponse(status_code=200, json=None),
    )
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_put(self, mock_headers, mock_request):
        result = self._auth_service.keycloak_put(
            "localhost:3000/users", {"name": "john"}
        )
        self.assertTrue(result)

    @mock.patch(
        "app.services.keycloak_service.requests.put",
        return_value=MockResponse(status_code=400, json={"errorMessage": "user exists"}),
    )
    @mock.patch("app.services.keycloak_service.AuthService.get_keycloak_headers")
    def test_keycloak_put_error(self, mock_headers, mock_request):
        with self.assertRaises(AppException.KeyCloakAdminException):
            self._auth_service.keycloak_put("localhost:3000/users", {"name": "john"})

    @mock.patch("app.services.keycloak_service.requests.post")
    def test_get_keycloak_access_token(self, mock_request):
        mock_request.side_effect = self.get_token_post_mock
        result = self._auth_service.get_keycloak_access_token()
        self.assertIsInstance(result, str)

    # side effect methods
    def get_keycloak_user_side_effect(self, *args, **kwargs):
        return MockResponse(status_code=200, json=[{"id": uuid.uuid4()}])

    def get_groups_side_effect(self, *args, **kwargs):
        return MockResponse(status_code=200, json=self.mock_groups)

    def get_token_post_mock(self, *args, **kwargs):
        return MockResponse(
            status_code=200,
            json={
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            },
        )

    def get_token_mock(self, *args, **kwargs):
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}
