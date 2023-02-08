import pinject
from flask import Blueprint, request
from app.controllers import FaqController
from app.core.service_result import handle_result
from app.repositories import FaqRepository
from app.schema import FaqGetSchema, FaqSchema, FaqRequestArgSchema
from app.utils import arg_validator, auth_required, validator

faq = Blueprint("faq", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        FaqController,
        FaqRepository,
    ],
)
faq_controller: FaqController = obj_graph.provide(FaqController)


@faq.route("/faq", methods=["GET"])
def get_faq():
    """
    ---
    get:
      description: retrieve all question in the system
      responses:
        '200':
          description: returns details of all faq
          content:
            application/json:
              schema:
                type: array
                items: FaqGetSchema
      tags:
          - FAQ
    """
    result = faq_controller.all_faq()
    return handle_result(result, schema=FaqGetSchema, many=True)


@faq.route("/faq", methods=["POST"])
@validator(schema=FaqSchema)
def create_faq():
    """
    ---
    post:
      description: question
      requestBody:
        required: true
        content:
          application/json:
            schema: FaqSchema
      responses:
        '201':
          description: returns details of added question
          content:
            application/json:
              schema: FaqGetSchema
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
                    example: question with id ... exists
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
          - FAQ
    """
    data = request.json
    result = faq_controller.register_faq(data)
    return handle_result(result, schema=FaqGetSchema)


@faq.route("/faq/<string:faq_id>", methods=["PATCH"])
@arg_validator(schema=FaqRequestArgSchema, param="faq_id")
def update_faq(faq_id):
    """
    ---
    patch:
      description: update faq
      requestBody:
        required: true
        content:
          application/json:
            schema: FaqSchema
      parameters:
        - in: path
          name: faq_id
          required: true
          schema:
            type: string
            description: the faq id
      responses:
        '200':
          description: returns details updated question
          content:
            application/json:
              schema: FaqRequestArgSchema
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
          - FAQ
    """
    data = request.json
    result = faq_controller.update_faq(faq_id, data)
    return handle_result(result, schema=FaqGetSchema)


@faq.route("/faq/<string:faq_id>", methods=["DELETE"])
@arg_validator(schema=FaqRequestArgSchema, param="faq_id")
def delete_faq(faq_id):
    """
     ---
    delete:
      description: delete faq with id specified in path
      parameters:
        - in: path
          name: faq_id
          required: true
          schema:
            type: string
          description: the faq id
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
          - FAQ
    """
    result = faq_controller.delete_faq(faq_id)
    return handle_result(result, schema=FaqGetSchema)
