import pinject
from flask import Blueprint, request

from app.controllers import CustomerController
from app.definitions.service_result import handle_result
from app.repositories import CustomerRepository, LeadRepository
from app.schema import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
    ConfirmTokenSchema,
    AddPinSchema,
)
from app.services import RedisService, AuthService
from app.utils import validator

customer = Blueprint("customer", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        CustomerController,
        CustomerRepository,
        RedisService,
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
          description: returns a customer
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
              schema: Customer
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.confirm_token(data)
    return handle_result(result, schema=CustomerSchema)


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
              schema: Customer
      tags:
          - Authentication
    """

    data = request.json
    result = customer_controller.add_pin(data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/accounts/<string:customer_id>", methods=["PATCH"])
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
                schema: CustomerUpdate
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


@customer.route("/accounts/<string:customer_id>")
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
      responses:
        '204':
          description: returns nil
      tags:
          - Customer
    """
    result = customer_controller.delete(customer_id)
    return handle_result(result)
