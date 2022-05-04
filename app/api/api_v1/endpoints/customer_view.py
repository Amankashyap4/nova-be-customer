import pinject
from flask import Blueprint, request

from app.controllers import CustomerController
from app.core.service_result import handle_result
from app.repositories import CustomerRepository, RegistrationRepository
from app.schema import (
    AddPinSchema,
    ConfirmTokenSchema,
    CustomerInfoSchema,
    CustomerRequestArgSchema,
    CustomerSchema,
    CustomerSignUpSchema,
    CustomerUpdateSchema,
    LoginSchema,
    PasswordOtpSchema,
    PinChangeSchema,
    PinResetRequestSchema,
    PinResetSchema,
    RefreshTokenSchema,
    RequestResetPinSchema,
    ResendTokenSchema,
    ResetPhoneSchema,
    TokenLoginSchema,
    UpdatePhoneSchema,
)
from app.services import AuthService, RedisService
from app.utils import arg_validator, auth_required, validator

customer = Blueprint("customer", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        CustomerController,
        CustomerRepository,
        RegistrationRepository,
        AuthService,
        RedisService,
    ],
)
customer_controller = obj_graph.provide(CustomerController)


@customer.route("/", methods=["GET"])
def get_customers():
    """
    ---
    get:
      description: register new customer phone number
      responses:
        '200':
          description: returns a customer id
          content:
            application/json:
              schema:
                type: array
                items: CustomerSchema
      tags:
          - Customer
    """

    result = customer_controller.index()
    return handle_result(result, schema=CustomerSchema, many=True)


@customer.route("account/register", methods=["POST"])
@validator(schema=CustomerSignUpSchema)
def create_customer_account():
    """
    ---
    post:
      description: register new customer phone number
      requestBody:
        required: true
        content:
          application/json:
            schema: CustomerSignUpSchema
      responses:
        '201':
          description: returns a customer id
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        '409':
          description: conflict
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ResourceExists
                  errorMessage:
                    type: str
                    example: Customer with phone number ... exists
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: NoBrokersAvailable
      tags:
          - Customer Registration
    """

    data = request.json
    result = customer_controller.register(data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/confirm-token", methods=["POST"])
@validator(schema=ConfirmTokenSchema)
def confirm_token():
    """
    ---
    post:
      description: confirm a new customer token
      requestBody:
        required: true
        content:
          application/json:
            schema: ConfirmTokenSchema
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: ConfirmedTokenSchema
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                    oneOf:
                      - type: object
                        properties:
                          token:
                            type: array
                            items:
                              type: str
                              example: String does not match expected pattern.
                      - type: Str
                        example: Invalid user.
                example:
                  app_exception: ValidationException
                  errorMessage:
                    token: ["String does not match expected pattern."]
      tags:
        - Customer Registration
    """

    data = request.json
    result = customer_controller.confirm_token(data)
    return handle_result(result)


@customer.route("/resend-token", methods=["POST"])
@validator(schema=ResendTokenSchema)
def resend_token():
    """
    ---
    post:
      description: creates a new token
      requestBody:
        required: true
        content:
          application/json:
            schema: ResendTokenSchema
      responses:
        '200':
          description: resends a token
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.resend_token(data)
    return handle_result(result)


@customer.route("/add-information", methods=["POST"])
@validator(schema=CustomerInfoSchema)
def add_information():
    """
    ---
    swagger: '2.0'
    post:
      tags:
          - Customer Registration
      description: add new customer information
      requestBody:
        required: true
        content:
            application/json:
                schema: CustomerInfoSchema
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: ConfirmInfo
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                    oneOf:
                      - type: object
                        properties:
                          full_name:
                            type: array
                            items:
                              type: str
                              value: Missing data for required field.
                      - type: Str
                        value: Invalid user.
                example:
                  app_exception: ValidationException
                  errorMessage:
                    token: ["Missing data for required field."]
        '500':
          description: returns an internal server error exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  error_message:
                    type: str
                    example: keycloak server connection error
    """
    data = request.json
    result = customer_controller.add_information(data)
    return handle_result(result)


@customer.route("/add-pin", methods=["POST"])
@validator(schema=AddPinSchema)
def add_pin():
    """
    ---
    post:
      description: create new customer
      requestBody:
        required: true
        content:
            application/json:
                schema: AddPinSchema
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: TokenSchema
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                    type: object
                    properties:
                      pin:
                        type: array
                        items:
                          type: str
                          example: String does not match expected pattern.
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist.
        '500':
          description: returns an internal server error exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  error_message:
                    type: str
                    example: keycloak server connection error
      tags:
          - Customer Registration
    """

    data = request.json
    result = customer_controller.add_pin(data)
    return handle_result(result)


@customer.route("/login", methods=["POST"])
@validator(schema=LoginSchema)
def login():
    """
    ---
    post:
      description: login a customer
      requestBody:
        required: true
        content:
            application/json:
                schema: LoginSchema
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: TokenLoginSchema
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                    type: object
                    properties:
                      pin:
                        type: array
                        items:
                          type: str
                          example: Length must be between 4 and 4.
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: Error in username or password
      tags:
        - Authentication
    """

    data = request.json
    result = customer_controller.login(data)
    return handle_result(result, schema=TokenLoginSchema)


@customer.route("/accounts/<string:customer_id>", methods=["PATCH"])
@auth_required()
@arg_validator(schema=CustomerRequestArgSchema, param="customer_id")
@validator(schema=CustomerUpdateSchema)
def update_customer(customer_id):
    """
    ---
    patch:
      description: updates a customer with id specified in path
      parameters:
        - in: path
          name: customer_id
          required: true
          schema:
            type: string
          description: The customer ID
      requestBody:
        required: true
        content:
            application/json:
                schema: CustomerUpdateSchema
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns a updated customer information
          content:
            application/json:
              schema: CustomerSchema
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Missing authentication token
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '500':
          description: returns an internal server error exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  error_message:
                    type: str
                    example: keycloak server connection error
      tags:
          - Customer
    """

    data = request.json
    result = customer_controller.update(customer_id, data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/accounts/<string:customer_id>", methods=["GET"])
@auth_required()
@arg_validator(schema=CustomerRequestArgSchema, param="customer_id")
def find_customer(customer_id):
    """
    ---
    get:
      description: returns a customer with id specified in path
      parameters:
        - in: path
          name: customer_id
          required: true
          schema:
            type: string
          description: The customer ID
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns a customer information
          content:
            application/json:
              schema: CustomerSchema
        '401':
          description: unauthorised
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Missing authentication token
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
      tags:
          - Customer
    """
    result = customer_controller.get_customer(customer_id)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/forgot-password", methods=["POST"])
@validator(schema=PinResetRequestSchema)
def forgot_password():
    """
    ---
    post:
      description: requests a reset of a customer's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetRequestSchema
      responses:
        '200':
          description: returns a uuid (customer's id)
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: NoBrokersAvailable
      tags:
          - Forgot-Password
    """
    data = request.json
    result = customer_controller.forgot_password(data)
    return handle_result(result)


@customer.route("/otp-conformation", methods=["POST"])
@validator(schema=PasswordOtpSchema)
def password_otp_confirmation():
    """
    ---
    post:
      description: confirms reset of a customer's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PasswordOtpSchema
      responses:
        '200':
          description: returns id, token
          content:
            application/json:
              schema: PasswordOtpSchema
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: BadRequest
                  errorMessage:
                    type: str
                    example: Wrong otp, please try again
      tags:
          - OTP confirmation for change Forgot password or change phone
    """
    data = request.json
    result = customer_controller.password_otp_confirmation(data)
    return handle_result(result)


@customer.route("/reset-password", methods=["POST"])
@validator(schema=PinResetSchema)
def reset_password():
    """
    ---
    post:
      description: confirms reset of a customer's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetSchema
      responses:
        '205':
          description: message
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail:
                    type: str
                    example: Pin reset done successfully
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                    oneOf:
                      - type: object
                        properties:
                          new_pin:
                            type: array
                            items:
                              type: str
                              example: String does not match expected pattern.
                      - type: Str
                        example: Invalid token.
                example:
                  app_exception: ValidationException
                  errorMessage:
                    new_pin: ["String does not match expected pattern."]
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: NoBrokersAvailable
      tags:
          - Forgot-Password
    """
    data = request.json
    result = customer_controller.reset_password(data)
    return handle_result(result)


@customer.route("/change-password/<string:user_id>", methods=["POST"])
@auth_required()
@arg_validator(schema=CustomerRequestArgSchema, param="user_id")
@validator(schema=PinChangeSchema)
def change_password(user_id):
    """
    ---
    post:
      description: changes a customer's password
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: The customer ID
      requestBody:
        required: true
        content:
            application/json:
                schema: PinChangeSchema
      security:
        - bearerAuth: []
      responses:
        '205':
          description: message
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail:
                    type: str
                    example: Content reset done successfully
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ValidationException
                  errorMessage:
                      type: object
                      properties:
                        new_pin:
                          type: array
                          items:
                            type: str
                            example: String does not match expected pattern.
                example:
                  app_exception: ValidationException
                  errorMessage:
                    new_pin: ["String does not match expected pattern."]
        '401':
          description: unauthorised
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Missing authentication token
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: Auth service error
      tags:
          - Authentication
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.change_password(data)
    return handle_result(result)


@customer.route("/request-pin-process", methods=["POST"])
@validator(schema=PinResetRequestSchema)
def pin_process():
    """
    ---
    post:
      description: change request to a customer's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetRequestSchema
      responses:
        '200':
          description: returns a uuid (customer's id)
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: NoBrokersAvailable
      tags:
          - Pin-Process
    """
    data = request.json
    result = customer_controller.pin_process(data)
    return handle_result(result)


@customer.route("/request-reset-pin", methods=["POST"])
@validator(schema=RequestResetPinSchema)
def request_reset_pin():
    """
    ---
    post:
      description: request to pin reset
      requestBody:
        required: true
        content:
            application/json:
                schema: RequestResetPinSchema
      responses:
        '200':
          description: returns full_name, id, password_token
          content:
            application/json:
              schema: ResetPinProcess
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Wrong otp, please try again
      tags:
          - Pin-Process
    """
    data = request.json
    result = customer_controller.reset_pin_process(data)
    return handle_result(result)


@customer.route("/reset-pin/<string:user_id>", methods=["POST"])
@arg_validator(schema=CustomerRequestArgSchema, param="user_id")
@validator(schema=AddPinSchema)
def reset_pin(user_id):
    """
    ---
    post:
      description: pin reset
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: The customer ID
      requestBody:
        required: true
        content:
            application/json:
                schema: AddPinSchema
      responses:
        '200':
          description: message
          content:
            application/json:
              schema: TokenSchema
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Something went wrong, please try again
        '500':
          description: returns an internal server error exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  error_message:
                    type: str
                    example: keycloak server connection error
      tags:
          - Pin-Process
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.process_reset_pin(data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/reset-phone-request", methods=["POST"])
@validator(schema=PinResetRequestSchema)
def reset_phone_request():
    """
    ---
    post:
      description: requests a reset of a customer's phone number
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetRequestSchema
      responses:
        '200':
          description: returns a uuid (customer's id)
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '500':
          description: internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: InternalServerError
                  errorMessage:
                    type: str
                    example: NoBrokersAvailable
      tags:
          - Customer Reset Phone
    """

    data = request.json
    result = customer_controller.reset_phone_request(data)
    return handle_result(result)


@customer.route("/reset-phone/<string:user_id>", methods=["POST"])
@arg_validator(schema=CustomerRequestArgSchema, param="user_id")
@validator(schema=ResetPhoneSchema)
def reset_phone(user_id):
    """
    ---
    post:
      description: register customer new phone number
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: The customer ID
      requestBody:
        required: true
        content:
          application/json:
            schema: ResetPhoneSchema
      responses:
        '201':
          description: returns a customer id
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '409':
          description: conflict
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ResourceExists
                  errorMessage:
                    type: str
                    example: Customer with phone number ... exists
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: BadRequest
                  errorMessage:
                    type: str
                    example: Invalid token
      tags:
          - Customer Reset Phone
    """

    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.reset_phone(data)
    return handle_result(result)


@customer.route("/update-phone/<string:user_id>", methods=["POST"])
@arg_validator(schema=CustomerRequestArgSchema, param="user_id")
@validator(schema=UpdatePhoneSchema)
def update_phone(user_id):
    """
    ---
    post:
      description: update customer's new phone number
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: The customer ID
      requestBody:
        required: true
        content:
          application/json:
            schema: UpdatePhoneSchema
      responses:
        '204':
          description: message
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail:
                    type: str
                    example: Phone reset done successfully
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: ExpiredTokenException
                  errorMessage:
                    type: str
                    example: Invalid token
      tags:
          - Customer Reset Phone
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.request_phone_reset(data)
    return handle_result(result)


@customer.route("/accounts/<string:customer_id>", methods=["DELETE"])
@auth_required()
@arg_validator(schema=CustomerRequestArgSchema, param="customer_id")
def delete_customer(customer_id):
    """
    ---
    delete:
      description: deletes a customer with id specified in path
      parameters:
        - in: path
          name: customer_id
          required: true
          schema:
            type: string
          description: The customer ID
      security:
        - bearerAuth: []
      responses:
        '204':
          description: returns nil
        '401':
          description: unauthorised
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Missing authentication token
        '404':
          description: not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: NotFoundException
                  errorMessage:
                    type: str
                    example: user does not exist
      tags:
          - Customer
    """
    result = customer_controller.delete(customer_id)
    return handle_result(result)


@customer.route("/accounts/refresh-token", methods=["POST"])
@validator(schema=RefreshTokenSchema)
def refresh_token():
    """
    ---
    post:
      description: refresh access token of customer
      requestBody:
        required: true
        content:
            application/json:
                schema: RefreshTokenSchema
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: RefreshTokenSchema
        '400':
          description: returns a bad request exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: KeyCloakAdminException
                  errorMessage:
                    oneOf:
                      type: array
                      items:
                        error:
                          type: str
                          example: invalid_grant
                        error_description:
                          type: str
                          example: Invalid refresh token
                example:
                  app_exception: KeyCloakAdminException
                  errorMessage: [
                    {
                      "error": "invalid_grant",
                      "error_description": "Invalid refresh token"
                    }
                  ]
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.refresh_token(data)
    return handle_result(result, schema=RefreshTokenSchema)


@customer.route("/accounts/query/<string:phone_number>", methods=["GET"])
@auth_required()
@arg_validator(schema=CustomerRequestArgSchema, param="phone_number")
def find_by_phone_number(phone_number):
    """
    ---
    get:
      description: retrieve customer info with phone number specified in path
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: phone_number
          required: true
          schema:
            type: string
          description: the customer's phone number
      responses:
        '200':
          description: returns customer's info
          content:
            application/json:
              schema: CustomerSchema
        '401':
          description: unauthorised
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  errorMessage:
                    type: str
                    example: Missing authentication token
      tags:
          - Customer
    """
    result = customer_controller.find_by_phone_number(phone_number)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/accounts/profile-images/", methods=["GET"])
def saved_images():
    result = customer_controller.customer_profile_images()
    return handle_result(result)


@customer.route("/accounts/profile-images/<string:customer_id>", methods=["GET"])
@arg_validator(schema=CustomerRequestArgSchema, param="customer_id")
def saved_image(customer_id):
    result = customer_controller.customer_profile_image(customer_id)
    return handle_result(result)
