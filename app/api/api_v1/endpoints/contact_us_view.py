import pinject
from flask import Blueprint, request
from app.controllers import ContactUsController
from app.core.service_result import handle_result
from app.repositories import ContactUsRepository
from app.schema import ContactUsGetSchema, ContactUsSchema, ContactUsRequestArgSchema
from app.utils import arg_validator, auth_required, validator

contact_us = Blueprint("contact_us", __name__)
obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        ContactUsController,
        ContactUsRepository,
    ],
)
contact_us_controller: ContactUsController = obj_graph.provide(ContactUsController)


@contact_us.route("/contact-us", methods=["GET"])
def get_contact_us():
    """
    ---
    get:
      description: retrieve all contact_us in the system
      responses:
        '200':
          description: returns details of all contact_us
          content:
            application/json:
              schema:
                type: array
                items: ContactUsSchema
      tags:
          - ContactUs
    """
    result = contact_us_controller.index()
    return handle_result(result, schema=ContactUsGetSchema, many=True)


@contact_us.route("/contact-us", methods=["POST"])
@validator(schema=ContactUsSchema)
def create_contact_us():
    """
    ---
    post:
      description: contact-us
      requestBody:
        required: true
        content:
          application/json:
            schema: ContactUsSchema
      responses:
        '201':
          description: returns details of added contact-us
          content:
            application/json:
              schema: ContactUsSchema
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
                    example: Contact us  ... exists
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
          - ContactUs
    """
    data = request.json
    result = contact_us_controller.register(data)
    return handle_result(result, schema=ContactUsGetSchema)


@contact_us.route("/contact-us/<string:contact_id>", methods=["PATCH"])
@arg_validator(schema=ContactUsRequestArgSchema, param="contact_id")
def update_contact_us(contact_id):
    """
    ---
    patch:
      description: update contact us
      requestBody:
        required: true
        content:
          application/json:
            schema: ContactUsSchema
      parameters:
        - in: path
          name: contact_id
          required: true
          schema:
            type: string
            description: the contact id
      responses:
        '200':
          description: returns details updated contact-us
          content:
            application/json:
              schema: ContactUsSchema
        '400':
          description: returns a bad request exception
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
                          service_type:
                            type: array
                            items:
                              type: str
                              example: Invalid enum member refil
                example:
                  app_exception: ValidationException
                  errorMessage:
                    service_type: ["Invalid enum member refil"]
      tags:
          - ContactUs
    """
    data = request.json
    result = contact_us_controller.update_contact_us(contact_id, data)
    return handle_result(result, schema=ContactUsGetSchema)


@contact_us.route("/contact-us/<string:contact_id>", methods=["DELETE"])
@arg_validator(schema=ContactUsRequestArgSchema, param="contact_id")
def delete_contact_us(contact_id):
    """
     ---
    delete:
      description: delete contact with id specified in path
      parameters:
        - in: path
          name: contact_id
          required: true
          schema:
            type: string
          description: the contact id
      responses:
        '204':
          description: returns Deleted
        '400':
          description: returns a bad request exception
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
                          order_id:
                            type: array
                            items:
                              type: str
                              example: Not a valid UUID
                example:
                  app_exception: ValidationException
                  errorMessage:
                    order_id: ["Not a valid UUID"]
      tags:
          - ContactUs
    """
    result = contact_us_controller.delete(contact_id)
    return handle_result(result, schema=ContactUsGetSchema)
