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


def arg_validator(schema, param):
    def validate_args(func):
        """
        A wrapper to validate uuid using marshmallow schema
        :param func: {function} the function to wrap around
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            errors = schema().validate(
                {arg: request.view_args.get(arg) for arg in param.split("|")}
            )

            if errors:
                raise AppException.ValidationException(context=errors)

            return func(*args, **kwargs)

        return view_wrapper

    return validate_args


def keycloak_fields(username, obj_data):
    """
    This function converts object fields to fields used by keycloak
    :param username: username of object
    :param obj_data: object fields you want to convert
    :return: object data with fields converted to keycloak format
    """

    obj_fields = {"username": username}

    for field in obj_data:
        auth_service_field = field.split("_")
        for index in range(len(auth_service_field)):
            if index > 0:
                auth_service_field[index] = auth_service_field[index].capitalize()
        obj_fields["".join(auth_service_field)] = obj_data.get(field)
    return obj_fields


def extract_valid_data(obj_data: dict, obj_validator):
    """
    This function extract data from an object given a validator
    :param obj_data: object data you want to validate
    :param obj_validator: pre-define data structure for data validation
    :return: valid data structure
    """

    valid_data = dict()
    for field in obj_validator:
        valid_data[field] = obj_data.get(field)
    return valid_data


def split_full_name(full_name: str):
    object_name = dict()
    if full_name:
        split_name = full_name.split(" ")
        for index, value in enumerate(split_name):
            if index == 0:
                object_name["first_name"] = value
            elif index == len(split_name) - 1:
                object_name["last_name"] = value
    return object_name
