import pinject as pinject
from flask import Blueprint, request

from app.controllers import CustomerController
from app.definitions.service_result import handle_result
from app.repositories import CustomerRepository
from app.schema import CustomerCreateSchema, CustomerSchema, \
    CustomerUpdateSchema
from app.utils import validator

customer = Blueprint("customer", __name__)

obj_graph = pinject.new_object_graph(
    modules=None, classes=[CustomerController, CustomerRepository]
)

customer_controller = obj_graph.provide(CustomerController)


@customer.route("/", methods=["POST"])
@validator(schema=CustomerCreateSchema)
def create():

    data = request.json
    result = customer_controller.create(data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/<string:customer_id>", methods=["PATCH"])
@validator(schema=CustomerUpdateSchema)
def update(customer_id):
    data = request.json
    result = customer_controller.update(customer_id, data)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/<string:customer_id>")
def show(customer_id):
    result = customer_controller.show(customer_id)
    return handle_result(result, schema=CustomerSchema)


@customer.route("/<string:customer_id>", methods=["DELETE"])
def delete(customer_id):
    result = customer_controller.delete(customer_id)
    return handle_result(result)
