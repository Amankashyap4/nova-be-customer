import uuid

from requests import exceptions as requests_exceptions

from tests.base_test_case import BaseTestCase


class MockResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class MockSideEffects(BaseTestCase):

    mock_groups = [
        {"id": str(uuid.uuid4()), "name": "nova-customer-gp"},
    ]
    status_code = 200
    json = None

    def requests_response(self, *args, **kwargs):
        return MockResponse(
            status_code=self.status_code,
            json={"error_description": "keycloak error"},
        )

    def get_token_response(self, *args, **kwargs):
        return MockResponse(
            status_code=200,
            json={
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            },
        )

    def get_token(self, *args, **kwargs):
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}

    def get_keycloak_user_response(self, *args, **kwargs):
        return MockResponse(status_code=200, json=[{"id": uuid.uuid4()}])

    def no_keycloak_user_response(self, *args, **kwargs):
        return MockResponse(status_code=200, json=[])

    def get_groups_response(self, *args, **kwargs):
        return MockResponse(status_code=200, json=self.mock_groups)

    def keycloak_exception(self, *args, **kwargs):
        return MockResponse(
            status_code=500,
            json={"error_description": "keycloak error"},
        )

    def request_exception(self, *args, **kwargs):
        raise requests_exceptions.RequestException

    def realm_openid_config(self, *args, **kwargs):
        return MockResponse(status_code=200, json={"url": "localhost"})
