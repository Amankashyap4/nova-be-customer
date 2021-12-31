import pinject
from flask import Blueprint, request

from app.controllers import CustomerController
from core.service_result import handle_result
from app.repositories import CustomerRepository, LeadRepository
from app.schema import (
    CustomerSchema,
    CustomerInfoSchema,
    CustomerSignUpSchema,
    CustomerUpdateSchema,
    ConfirmTokenSchema,
    AddPinSchema,
    UpdatePhoneSchema,
    ResendTokenSchema,
    LoginSchema,
    TokenSchema,
    PinChangeSchema,
    PinResetSchema,
    PinResetRequestSchema,
    TokenLoginSchema,
)
from app.services import AuthService
from core.utils import validator, auth_required

customer = Blueprint("customer", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        CustomerController,
        CustomerRepository,
        AuthService,
        LeadRepository,
    ],
)
customer_controller = obj_graph.provide(CustomerController)


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
      tags:
          - Authentication
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
      description: creates a new customer
      requestBody:
        required: true
        content:
            application/json:
                schema: ConfirmToken
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: ConfirmedTokenSchema
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.confirm_token(data)
    return handle_result(result)


@customer.route("/add-information", methods=["POST"])
@validator(schema=CustomerInfoSchema)
def add_information():
    """
    ---
    post:
      description: add new customer information
      requestBody:
        required: true
        content:
            application/json:
                schema: CustomerAddInfoSchema
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: ConformInfo
      tags:
          - Authentication
    """
    from datetime import datetime

    data = request.json
    if data.get("birth_date"):
        data["birth_date"] = datetime.strptime(data.get("birth_date"), "%Y-%m-%d")
    if data.get("id_expiry_date"):
        data["id_expiry_date"] = datetime.strptime(
            data.get("id_expiry_date"), "%Y-%m-%d"
        )
    result = customer_controller.add_customer_information(data)
    return handle_result(result)


@customer.route("/add-pin", methods=["POST"])
@validator(schema=AddPinSchema)
def add_pin():
    """
    ---
    post:
      description: creates a new customer
      requestBody:
        required: true
        content:
            application/json:
                schema: PinData
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: TokenSchema
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.add_pin(data)
    return handle_result(result, schema=TokenSchema)


@customer.route("/login", methods=["POST"])
@validator(schema=LoginSchema)
def login_user():
    """
    ---
    post:
      description: logs in a customer
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
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.login(data)
    return handle_result(result, schema=TokenLoginSchema)


@customer.route("/accounts/<string:customer_id>", methods=["PATCH"])
@validator(schema=CustomerUpdateSchema)
@auth_required()
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
                schema: CustomerUpdate
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns a customer
          content:
            application/json:
              schema: Customer
      tags:
          - Customer
    """

    data = request.json
    result = customer_controller.update(customer_id, data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/accounts/<string:customer_id>", methods=["GET"])
@auth_required()
def show_customer(customer_id):
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
          description: returns a customer
          content:
            application/json:
              schema: Customer
      tags:
          - Customer
    """
    result = customer_controller.show(customer_id)
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
                schema: PinResetRequest
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
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.request_password_reset(data)
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
                schema: PinReset
      responses:
        '205':
          description: returns nil
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.reset_password(data)
    return handle_result(result)


@customer.route("/change-password/<string:user_id>", methods=["POST"])
@validator(schema=PinChangeSchema)
@auth_required()
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
                schema: PinChange
      security:
        - bearerAuth: []
      responses:
        '205':
          description: returns nil
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
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.pin_process(data)
    return handle_result(result)


@customer.route("/request-reset-pin", methods=["POST"])
@validator(schema=ConfirmTokenSchema)
def request_reset_pin():
    """
    ---
    post:
      description: request to pin reset
      requestBody:
        required: true
        content:
            application/json:
                schema: ConfirmTokenSchema
      responses:
        '200':
          description: returns full_name, id, password_token
          content:
            application/json:
              schema: ResetPinProcess
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.reset_pin_process(data)
    return handle_result(result)


@customer.route("/reset-pin/<string:user_id>", methods=["POST"])
@validator(schema=AddPinSchema)
def reset_pin(user_id):
    """
    ---
    post:
      description: request to pin reset
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
          description: nil
      tags:
          - Authentication
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.process_reset_pin(data)
    return handle_result(result)


@customer.route("/reset-phone/<string:user_id>", methods=["POST"])
@validator(schema=PinResetRequestSchema)
@auth_required()
def reset_phone(user_id):
    """
    ---
    post:
      description: register new customer phone number
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
            schema: PinResetRequestSchema
      security:
        - bearerAuth: []
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
      tags:
          - Authentication
    """

    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.reset_phone(data)
    return handle_result(result)


@customer.route("/update-phone/<string:user_id>", methods=["POST"])
@validator(schema=UpdatePhoneSchema)
@auth_required()
def update_phone(user_id):
    """
    ---
    post:
      description: register new customer phone number
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: string
          description: The customer ID
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: UpdatePhoneSchema
      responses:
        '201':
          description: nil
      tags:
          - Authentication
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.request_phone_reset(data)
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
            schema: ResendTokenData
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


@customer.route("/accounts/<string:customer_id>", methods=["DELETE"])
@auth_required()
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
      tags:
          - Customer
    """
    result = customer_controller.delete(customer_id)
    return handle_result(result)
