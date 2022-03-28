import jwt
import inspect
import requests

from functools import wraps
from flask import request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from core.exceptions import AppException


def auth_required(other_roles=None):
    def authorize_user(func):
        """
        A wrapper to authorize an action using
        :param func: {function}` the function to wrap around
        :return:
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            """line 25 to 32 shift in utf of keycloak service"""
            from config import Config

            uri = Config.KEYCLOAK_URI + "/auth/realms/" + Config.KEYCLOAK_REALM + "/"
            x = requests.get(uri)
            try:
                public_key = x.json()["public_key"]
            except Exception:
                public_key = "samplePublicKey"

            key = (
                "-----BEGIN PUBLIC KEY-----\n"
                + public_key
                + "\n-----END PUBLIC KEY-----"
            )

            authorization_header = request.headers.get("Authorization")
            if not authorization_header:
                raise AppException.Unauthorized("Missing authentication token")

            token = authorization_header.split()[1]
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=["HS256", "RS256"],
                    options={"verify_signature": False},
                )
                try:
                    available_roles = (
                        payload.get("resource_access")
                        .get(Config.KEYCLOAK_CLIENT_ID)
                        .get("roles")
                    )
                except Exception:
                    available_roles = []

                # Append service name to function name to form role
                # e.g customer_update_user

                service_name = Config.APP_NAME
                generated_role = service_name + "_" + func.__name__

                authorized_roles = []

                if other_roles:
                    authorized_roles = other_roles.split("|")

                authorized_roles.append(generated_role)

                if is_authorized(authorized_roles, available_roles):
                    if "user_id" in inspect.getfullargspec(func).args:
                        kwargs["user_id"] = payload.get("preferred_username")
                    return func(*args, **kwargs)
            except ExpiredSignatureError:
                raise AppException.ExpiredTokenException("Token Expired")
            except InvalidTokenError:
                raise AppException.OperationError("Invalid Token")
            except PyJWTError:
                raise AppException.OperationError("Error decoding token")
            raise AppException.Unauthorized(status_code=403)

        return view_wrapper

    return authorize_user


def is_authorized(access_roles, available_roles):
    for role in access_roles:
        if role in available_roles:
            return True

    return False
