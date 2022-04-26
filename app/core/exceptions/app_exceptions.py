from flask import Response, current_app, json
from sqlalchemy.exc import DBAPIError
from werkzeug.exceptions import HTTPException


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context, error_message):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context
        self.error_message = error_message
        if self.context:
            current_app.logger.error(context)
        if self.error_message:
            current_app.logger.debug(error_message)

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code = {self.status_code} - context = {self.context}"
        )


def app_exception_handler(exc):
    if isinstance(exc, DBAPIError):
        return Response(
            json.dumps(
                {"app_exception": "Database Error", "errorMessage": exc.orig.pgerror}
            ),
            status=400,
        )
    if isinstance(exc, HTTPException):
        return Response(
            json.dumps({"app_exception": "HTTP Error", "errorMessage": exc.description}),
            status=exc.code,
        )

    return Response(
        json.dumps({"app_exception": exc.exception_case, "errorMessage": exc.context}),
        status=exc.status_code,
        mimetype="application/json",
    )


class AppException:
    class OperationError(AppExceptionCase):
        """
        Generic Exception to catch failed operations
        """

        def __init__(self, context, error_message=None):

            status_code = 500
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class InternalServerError(AppExceptionCase):
        """
        Generic Exception to catch failed operations
        """

        def __init__(self, context="Internal Server Error", error_message=None):

            status_code = 500
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class ResourceExists(AppExceptionCase):
        """
        Resource Creation Failed Exception
        """

        def __init__(self, context, error_message=None):

            status_code = 409
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class ResourceDoesNotExist(AppExceptionCase):
        def __init__(self, context=None, error_message=None):
            """
            Resource does not exist
            """
            status_code = 404
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class NotFoundException(AppExceptionCase):
        def __init__(self, context="Resource does not exists", error_message=None):
            """
            Resource does not exist
            """
            status_code = 404
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class Unauthorized(AppExceptionCase):
        def __init__(self, context="Unauthorized", error_message=None):
            """
            Unauthorized
            :param context: extra dictionary object to give the error more context
            """
            status_code = 401
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class ValidationException(AppExceptionCase):
        """
        Resource Creation Failed Exception
        """

        def __init__(self, context, error_message=None):

            status_code = 400
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class KeyCloakAdminException(AppExceptionCase):
        def __init__(self, context=None, status_code=400, error_message=None):
            """
            Key Cloak Error. Error with regards to Keycloak authentication
            :param context: extra data to give the error more context
            """

            AppExceptionCase.__init__(self, status_code, context, error_message)

    class BadRequest(AppExceptionCase):
        def __init__(self, context=None, error_message=None):
            """
            Bad Request

            :param context:
            """
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class ExpiredTokenException(AppExceptionCase):
        def __init__(self, context=None, error_message=None):
            """
            Expired Token
            :param context:
            """

            status_code = 400
            AppExceptionCase.__init__(self, status_code, context, error_message)

    class ServiceRequestException(AppExceptionCase):
        def __init__(self, error_message=None, context="Service not available"):
            """
            Service is not available
            """
            status_code = 500
            AppExceptionCase.__init__(self, status_code, context, error_message)
