from dataclasses import dataclass

import requests
from requests import exceptions

import config
from app.core.exceptions import AppException
from app.core.service_interfaces.auth_service_interface import AuthServiceInterface

CLIENT_ID = config.Config.KEYCLOAK_CLIENT_ID or ""
CLIENT_SECRET = config.Config.KEYCLOAK_CLIENT_SECRET or ""
URI = config.Config.KEYCLOAK_URI or ""
REALM = config.Config.KEYCLOAK_REALM or ""
REALM_PREFIX = "/auth/realms/"
AUTH_ENDPOINT = "/protocol/openid-connect/token/"
REALM_URL = "/auth/admin/realms/"
OPENID_CONFIGURATION_ENDPOINT = "/.well-known/openid-configuration"


@dataclass
class AuthService(AuthServiceInterface):
    """
    This class is an intermediary between this service and the IAM service i.e Keycloak.
    It makes authentication and authorization api calls to the IAM service on
    behalf of the application. Use this class when authenticating an entity
    """

    roles = []

    def get_token(self, request_data):
        """
        Login to keycloak and return token
        :param request_data: {dict} a dictionary containing username and password
        :return: {dict} a dictionary containing token and refresh token
        """
        assert request_data, "Missing request data to login"
        assert isinstance(request_data, dict), "request data should be a dict"

        data = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": request_data.get("username"),
            "password": request_data.get("password"),
        }

        # create keycloak uri for token login
        url = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT

        keycloak_response = self.send_request_to_keycloak(
            method="post", url=url, data=data
        )

        if keycloak_response.status_code != 200:
            raise AppException.KeyCloakAdminException(
                {"access_token": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )

        tokens_data: dict = keycloak_response.json()
        result = {
            "access_token": tokens_data.get("access_token"),
            "refresh_token": tokens_data.get("refresh_token"),
        }

        return result

    def refresh_token(self, refresh_token):
        """
        :param refresh_token: a {str} containing the refresh token
        :return: {dict} a dictionary containing the token and refresh token
        """
        assert refresh_token, "Missing refresh token"
        assert isinstance(refresh_token, str)

        request_data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        url = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT
        keycloak_response = self.send_request_to_keycloak(
            method="post", url=url, data=request_data
        )

        if keycloak_response.status_code != 200:
            raise AppException.KeyCloakAdminException(
                {"refresh_token": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )

        data: dict = keycloak_response.json()
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
        }

    def create_user(self, request_data: dict):
        assert request_data, "Missing request data to be saved"
        assert isinstance(request_data, dict)
        data = {
            "email": request_data.get("email", request_data.get("username")),
            "username": request_data.get("username"),
            "firstName": request_data.get("first_name", "null"),
            "lastName": request_data.get("last_name", "null"),
            "attributes": {
                "phoneNumber": request_data.get("phone_number", "null"),
                "idType": request_data.get("id_type", "null"),
                "idNumber": request_data.get("id_number", "null"),
                "idExpiryDate": request_data.get("id_expiry_date", "null"),
                "profileImage": request_data.get("profile_image", "null"),
                "status": request_data.get("status", "null"),
            },
            "credentials": [
                {
                    "value": request_data.get("password"),
                    "type": "password",
                    "temporary": False,
                }
            ],
            "enabled": True,
            "emailVerified": True,
            "access": {
                "manageGroupMembership": True,
                "view": True,
                "mapRoles": True,
                "impersonate": True,
                "manage": True,
            },
        }

        endpoint: str = "/users"
        # create user
        self.keycloak_post(endpoint, data)
        # get user details from keycloak
        user = self.get_keycloak_user(request_data.get("username"))
        user_id: str = user.get("id")

        # assign user to group
        group = request_data.get("group")
        iam_groups = self.get_all_groups()
        required_groups = list(filter(lambda x: x.get("name") == group, iam_groups))
        if len(required_groups) == 0:
            raise AppException.OperationError(
                f"group {group} does not exist in IAM service"
            )
        group_data = required_groups[0]
        # assign user to a group
        self.assign_group(user_id, group_data)
        return user_id

    def update_user(self, request_data: dict):
        assert request_data, "Missing request data to update user with"
        assert isinstance(request_data, dict), "request data is not a dict"

        user = self.get_keycloak_user(request_data.get("username"))
        for field in request_data:
            if field in user:
                user[field] = request_data[field]
            elif field in user.get("attributes"):
                user.get("attributes")[field] = request_data.get(field)
        endpoint: str = f"/users/{user.get('id')}"
        # update user on keycloak
        self.keycloak_put(endpoint, user)
        # get updated details from keycloak
        updated_user = self.get_keycloak_user(request_data.get("username"))
        return updated_user.get("username")

    def delete_user(self, user_id: str):
        assert user_id, "Missing id of user to be deleted"
        assert isinstance(user_id, str)

        # user id is set as username in auth service
        user = self.get_keycloak_user(user_id)

        endpoint: str = f"/users/{user.get('id')}"
        # delete user
        self.keycloak_delete(endpoint)
        return True

    def get_all_groups(self):
        url = URI + REALM_URL + REALM + "/groups"
        keycloak_response = self.send_request_to_keycloak(
            method="get", url=url, headers=self.get_keycloak_headers()
        )

        if keycloak_response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"realm_groups": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        return keycloak_response.json()

    def get_keycloak_user(self, username):
        """

        :param username: username of keycloak user which is normally the uuid
        of the user in the database
        :return:
        """
        assert username, "Missing username of keycloak user"

        url = URI + REALM_URL + REALM + "/users?username=" + username
        keycloak_response = self.send_request_to_keycloak(
            method="get", url=url, headers=self.get_keycloak_headers()
        )
        if keycloak_response.status_code != 200:
            raise AppException.KeyCloakAdminException(
                {"realm_user": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        user = keycloak_response.json()
        if len(user) == 0:
            return None
        else:
            return user[0]

    def assign_group(self, user_id, group):
        assert user_id, "Missing id of user to assign group"
        assert group, "Missing group to assign user to"

        endpoint = "/users/" + user_id + "/groups/" + group.get("id")
        url = URI + REALM_URL + REALM + endpoint
        keycloak_response = self.send_request_to_keycloak(
            method="put", url=url, headers=self.get_keycloak_headers()
        )

        if keycloak_response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"assign_group": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        return True

    def reset_password(self, data):
        assert data, "Missing data for password reset"

        username = data.get("username")
        new_password = data.get("new_password")
        user = self.get_keycloak_user(username)
        url = "/users/" + user.get("id") + "/reset-password"

        data = {"type": "password", "value": new_password, "temporary": False}

        self.keycloak_put(url, data)
        return True

    def keycloak_post(self, endpoint, data):
        """
        Make a POST request to Keycloak
        :param {string} endpoint Keycloak endpoint
        :data {object} data Keycloak data object
        :return {Response} request response object
        """
        assert endpoint, "Missing endpoint for post request"
        assert data, "Missing data for post request"

        url = URI + REALM_URL + REALM + endpoint
        headers = self.get_keycloak_headers()
        keycloak_response = self.send_request_to_keycloak(
            method="post", url=url, headers=headers, json=data
        )
        if keycloak_response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"keycloak_post_request": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        return keycloak_response

    def keycloak_put(self, endpoint, data):
        """
        Make a PUT request to Keycloak
        :param {string} endpoint Keycloak endpoint
        :data {object} data Keycloak data object
        :return {Response} request response object
        """
        assert endpoint, "Missing endpoint for put request"
        assert data, "Missing data for put request"

        url = URI + REALM_URL + REALM + endpoint
        keycloak_response = self.send_request_to_keycloak(
            method="put", url=url, headers=self.get_keycloak_headers(), json=data
        )

        if keycloak_response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"keycloak_put_request": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        return keycloak_response

    def keycloak_delete(self, endpoint):
        """
        Make a DELETE request to Keycloak
        :param {string} endpoint Keycloak endpoint
        :data {object} data Keycloak data object
        :return {Response} request response object
        """
        assert endpoint, "Missing endpoint for delete request"

        url = URI + REALM_URL + REALM + endpoint
        keycloak_response = self.send_request_to_keycloak(
            method="delete", url=url, headers=self.get_keycloak_headers()
        )

        if keycloak_response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"keycloak_delete_request": [keycloak_response.json()]},
                status_code=keycloak_response.status_code,
            )
        return keycloak_response

    def get_keycloak_headers(self):
        """
        login as an admin user into keycloak and use the access token as an
        authentication user.
        :return {object}  Object of keycloak headers
        """

        realm_admin = {
            "username": config.Config.KEYCLOAK_ADMIN_USER,
            "password": config.Config.KEYCLOAK_ADMIN_PASSWORD,
        }

        token = self.get_token(realm_admin)
        headers = {
            "Authorization": "Bearer " + token.get("access_token"),
            "Content-Type": "application/json",
        }

        return headers

    def realm_openid_configuration(self):
        """
        Returns all openid configuration url endpoints pertaining to admin realm.
        :return {object} url endpoints
        """
        url = URI + REALM_PREFIX + REALM + OPENID_CONFIGURATION_ENDPOINT
        keycloak_response = self.send_request_to_keycloak(method="get", url=url)

        # handle keycloak response
        if keycloak_response.status_code != requests.codes.ok:
            raise AppException.KeyCloakAdminException(
                {"realm_openid_config": [keycloak_response.json()]}, status_code=500
            )
        data = keycloak_response.json()
        return data

    # noinspection PyMethodMayBeStatic
    def send_request_to_keycloak(
        self, method=None, url=None, headers=None, json=None, data=None
    ):
        try:
            response = requests.request(
                method=method, url=url, headers=headers, json=json, data=data
            )
        except exceptions.ConnectionError:
            raise AppException.OperationError(
                context={f"{method} request error": "keycloak server connection error"}
            )
        except exceptions.HTTPError:
            raise AppException.OperationError(
                context={f"{method} request error": "keycloak server http error"}
            )
        except exceptions.Timeout:
            raise AppException.OperationError(
                context={f"{method} request error": "keycloak server connection timeout"}
            )
        except exceptions.RequestException:
            raise AppException.OperationError(
                context={
                    f"{method} request error": "error connecting to keycloak server"
                }
            )
        return response
