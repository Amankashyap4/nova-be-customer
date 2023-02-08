import os
from functools import wraps

import jwt
from flask import request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from app.core.exceptions import AppException


def auth_required(authorized_roles=None):
    from config import Config

    def authorize_user(func):
        """
        A wrapper to authorize an action using
        :param func: {function}` the function to wrap around
        :return:
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            authorization_header = request.headers.get("Authorization")
            if not authorization_header or len(authorization_header.split()) < 2:
                raise AppException.Unauthorized("Missing authentication token")
            token = authorization_header.split()[1]
            payload = decode_token(config=Config, token=token)
            user_role = authorized_clients(config=Config, payload=payload)
            if authorized_roles:
                resource_access_role = authorized_roles.split("|")
                if user_is_authorized(user_role, resource_access_role):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
            raise AppException.Unauthorized(error_message="operation unauthorized")

        return view_wrapper

    return authorize_user


def decode_token(config, token):
    try:
        payload = jwt.decode(
            token,
            key=os.getenv("JWT_PUBLIC_KEY"),
            algorithms=config.JWT_ALGORITHMS,
            audience="account",
            issuer=config.JWT_ISSUER,
        )
        return payload
    except ExpiredSignatureError as e:
        raise AppException.ExpiredTokenException(error_message=e.args)
    except InvalidTokenError as e:
        raise AppException.OperationError(error_message=e.args)
    except PyJWTError as e:
        raise AppException.OperationError(error_message=e.args)


def authorized_clients(config, payload):
    resource_access = payload.get("resource_access")
    for client in config.KEYCLOAK_CLIENT_ID:
        if client in resource_access.keys():
            user_role = resource_access.get(client).get("roles")
            return user_role
    return []


def user_is_authorized(user_role, resource_role):
    for role in resource_role:
        if role in user_role:
            return True
    return False
