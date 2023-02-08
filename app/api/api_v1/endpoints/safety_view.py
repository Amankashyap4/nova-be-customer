import pinject
from flask import Blueprint, request
from app.controllers import SafetyController
from app.core.service_result import handle_result
from app.repositories import SafetyRepository
from app.schema import SafetyGetSchema, SafetySchema, SafetyRequestArgSchema, \
    SafetyPatchSchema
from app.utils import arg_validator, auth_required, validator

safety = Blueprint("safety", __name__)
obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        SafetyController,
        SafetyRepository,
    ],
)
safety_controller: SafetyController = obj_graph.provide(SafetyController)


@safety.route("/safety", methods=["GET"])
def get_safety():
    """
    ---
    get:
      description: retrieve all safety in the system
      responses:
        '200':
          description: returns details of all safety
          content:
            application/json:
              schema:
                type: array
                items: SafetySchema
      tags:
          - Safety
    """

    result = safety_controller.index()
    return handle_result(result, schema=SafetyGetSchema, many=True)


@safety.route("/safety", methods=["POST"])
@validator(schema=SafetySchema)
def create_safety():
    """
    ---
    post:
      description: safety
      requestBody:
        required: true
        content:
          application/json:
            schema: SafetySchema
      responses:
        '201':
          description: returns details of added Safety
          content:
            application/json:
              schema: SafetySchema
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
                    example: Customer with id ... exists
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
          - Safety
    """
    data = request.json
    result = safety_controller.register(data)
    return handle_result(result, schema=SafetyGetSchema)


@safety.route("/safety/<string:safety_id>", methods=["PATCH"])
@arg_validator(schema=SafetyRequestArgSchema, param="safety_id")
@validator(schema=SafetyPatchSchema)
def update_safety(safety_id):
    """
    ---
    patch:
      description: update safety
      requestBody:
        required: true
        content:
          application/json:
            schema: SafetySchema
      parameters:
        - in: path
          name: safety_id
          required: true
          schema:
            type: string
            description: the safety's id
      responses:
        '201':
          description: returns details updated promotion
          content:
            application/json:
              schema: SafetySchema
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
          - Safety
    """
    data = request.json
    result = safety_controller.update_safety(safety_id, data)
    return handle_result(result, schema=SafetyGetSchema)


@safety.route("/safety/<string:safety_id>", methods=["DELETE"])
@arg_validator(schema=SafetyRequestArgSchema, param="safety_id")
def delete_safety(safety_id):
    """
    ---
    delete:
      description: delete safety
      parameters:
        - in: path
          name: safety_id
          required: true
          schema:
            type: string
          description: the id of the safety
      responses:
        '204':
          description: return none
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
                          safety_id:
                            type: array
                            items:
                              type: str
                              example: Not a valid UUID
                example:
                  app_exception: ValidationException
                  errorMessage:
                    safety_id: ["Not a valid UUID"]
      tags:
          - Safety
    """
    result = safety_controller.delete(safety_id)
    return handle_result(result, schema=SafetyGetSchema)
