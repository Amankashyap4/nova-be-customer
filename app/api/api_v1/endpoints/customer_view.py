import pinject
from flask import Blueprint, request

from app.controllers import CustomerController
from core.service_result import handle_result
from app.repositories import CustomerRepository, LeadRepository
from app.schema import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
    ConfirmTokenSchema,
    AddPinSchema,
    ResendTokenSchema,
    LoginSchema,
    TokenSchema,
    PinChangeSchema,
    PinResetSchema,
    PinResetRequestSchema,
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


@customer.route("accounts/", methods=["POST"])
@validator(schema=CustomerCreateSchema)
def create_customer():
    """
    ---
    post:
      description: creates a new customer
      requestBody:
        required: true
        content:
          application/json:
            schema: CustomerCreate
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
              schema:
                type: object
                properties:
                  id:
                    type: string
                    example: m8bQ5_P8o_4eojNs4xUB6w
      tags:
          - Authentication
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
              schema: TokenData
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.add_pin(data)
    return handle_result(result, schema=TokenSchema)


@customer.route("/token-login", methods=["POST"])
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
              schema: TokenData
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.login(data)
    return handle_result(result, schema=TokenSchema)


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


@customer.route("/change-password", methods=["POST"])
@validator(schema=PinChangeSchema)
@auth_required()
def change_password(user_id):
    """
    ---
    post:
      description: changes a customer's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinChange
      security:
        - bearerAuth: []
      responses:
        '204':
          description: returns nil
      tags:
          - Authentication
    """
    data = request.json
    data["customer_id"] = user_id
    result = customer_controller.change_password(data)
    return handle_result(result)


@customer.route("/request-reset", methods=["POST"])
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
        '204':
          description: returns nil
      tags:
          - Authentication
    """
    data = request.json
    result = customer_controller.reset_password(data)
    return handle_result(result)
