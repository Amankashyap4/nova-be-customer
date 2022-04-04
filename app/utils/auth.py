import inspect
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
            if not authorization_header:
                raise AppException.Unauthorized("Missing authentication token")
            token = authorization_header.split()[1]
            payload = decode_token(config=Config, token=token)
            # Get retailer roles from token
            available_roles = payload.get("resource_access").get(
                Config.KEYCLOAK_CLIENT_ID
            )
            user_role = available_roles.get("roles")
            if authorized_roles:
                resource_access_role = authorized_roles.split("|")
                if user_is_authorized(user_role, resource_access_role):
                    if "user_id" in inspect.getfullargspec(func).args:
                        kwargs["user_id"] = payload.get("preferred_username")
                    return func(*args, **kwargs)
            else:
                if "user_id" in inspect.getfullargspec(func).args:
                    kwargs["user_id"] = payload.get("preferred_username")
                return func(*args, **kwargs)
            raise AppException.Unauthorized(context="operation unauthorized")

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
        raise AppException.ExpiredTokenException(context=e.args)
    except InvalidTokenError as e:
        raise AppException.OperationError(context=e.args)
    except PyJWTError as e:
        raise AppException.OperationError(context=e.args)


def user_is_authorized(user_role, resource_role):
    for role in user_role:
        if role in resource_role:
            return True

    return False
