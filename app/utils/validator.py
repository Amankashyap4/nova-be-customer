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
