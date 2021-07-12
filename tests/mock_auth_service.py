from app.definitions.service_interfaces import AuthServiceInterface


class MockAuthService(AuthServiceInterface):
    tokens = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # noqa: E501
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # noqa: E501
    }

    def get_token(self, request_data):
        return self.tokens

    def refresh_token(self, refresh_token):
        return self.tokens

    def create_user(self, data):
        token = self.tokens
        token["id"] = "d9247e56-7ad4-434d-8524-606e69d784c3"
