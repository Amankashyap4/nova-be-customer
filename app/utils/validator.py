import uuid
from functools import wraps

from flask import request

from app.core.exceptions import AppException


def validator(schema):
    def validate_data(func):
        """
        A wrapper to validate data using marshmallow schema
        :param func: {function} the function to wrap around
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            errors = schema().validate(request.json)
            if errors:
                raise AppException.ValidationException(context=errors)

            return func(*args, **kwargs)

        return view_wrapper

    return validate_data


def validate_uuid(obj_id):
    if isinstance(obj_id, uuid.UUID):
        obj_id = str(obj_id)
    try:
        uuid.UUID(obj_id)
    except ValueError:
        raise AppException.ValidationException(
            context={"valueError": f"the id {obj_id} is inavlid"}
        )
    return True


def split_name(obj_data):

    if obj_data.get("full_name"):
        fullname = obj_data.pop("full_name").split(" ")
        obj_data["first_name"] = fullname[0]
        obj_data["last_name"] = " ".join(fullname[1:])
    return obj_data


def keycloak_fields(username, obj_data):
    obj_fields = {"username": username}

    for field in obj_data:
        auth_service_field = field.split("_")
        for index in range(len(auth_service_field)):
            if index > 0:
                auth_service_field[index] = auth_service_field[index].capitalize()
        obj_fields["".join(auth_service_field)] = obj_data.get(field)
    return obj_fields
