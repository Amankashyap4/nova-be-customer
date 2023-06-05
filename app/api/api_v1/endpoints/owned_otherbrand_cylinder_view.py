import pinject
from flask import Blueprint, request

from app.controllers.owned_otherbrand_cylinder_controller import \
    OwnedOtherBrandCylinderController
from app.core.service_result import handle_result
from app.repositories import OwnedOtherBrandCylinderRepository, CustomerRepository
from app.schema import OwnedOtherBrandCylinderRequestArgSchema, \
    OwnedOtherBrandCylinderPostSchema, OwnedOtherBrandCylinderGetSchema, CustomerSchema
from app.services import RedisService

from app.utils import arg_validator, auth_required, validator

owned_otherbrand_cylinder = Blueprint("owned_otherbrand_cylinder", __name__)
obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        OwnedOtherBrandCylinderController,
        OwnedOtherBrandCylinderRepository,
        CustomerRepository,
        RedisService,
        CustomerSchema,
    ],
)
owned_otherbrand_cylinder_controller: OwnedOtherBrandCylinderController = obj_graph.provide(OwnedOtherBrandCylinderController)

@owned_otherbrand_cylinder.route("/", methods=["GET"])
#@auth_required()
def get_all_owned_otherbrand_cylinder():
    """
    ---
    get:
      description: retrieve owned_otherbrand_cylinder details
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns pricing details
          content:
            application/json:
              schema: OwnedOtherBrandCylinderGetSchema
        '401':
          description: returns an unauthorized exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  error_message:
                    type: str
                    example: Missing authentication token
      tags:
          - Owned Other Brand Cylinders
    """
    result = owned_otherbrand_cylinder_controller.all_other_brand_cylinders()
    return handle_result(result, schema=OwnedOtherBrandCylinderGetSchema, many=True)

@owned_otherbrand_cylinder.route("/<string:cylinder_id>", methods=["GET"])
#@auth_required()
@arg_validator(schema=OwnedOtherBrandCylinderRequestArgSchema, param="cylinder_id")
def get_owned_otherbrand_cylinder(cylinder_id):
    """
    ---
    get:
      description: retrieve cylinder of cylinder with id specified in path
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: cylinder_id
          required: true
          schema:
            type: string
          description: cylinder's id
      responses:
        '200':
          description: returns cylinder info of cylinder with id specified in path
          content:
            application/json:
              schema: OwnedOtherBrandCylinderGetSchema
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
                          customer_id:
                            type: array
                            items:
                              type: str
                              example: Invalid UUID
                example:
                  app_exception: ValidationException
                  errorMessage:
                    location_id: ["Invalid UUID"]
        '401':
          description: returns an unauthorized exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  error_message:
                    type: str
                    example: Missing authentication token
      tags:
          - Owned Other Brand Cylinders
    """
    result = owned_otherbrand_cylinder_controller.get_other_brand_cylinders(cylinder_id)
    return handle_result(result, schema=OwnedOtherBrandCylinderGetSchema)


@owned_otherbrand_cylinder.route("/", methods=["POST"])
@validator(schema=OwnedOtherBrandCylinderPostSchema)
#auth_required()
def create_owned_otherbrand_cylinder():
    """
    ---
    post:
      description: owned_otherbrand_cylinde
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: OwnedOtherBrandCylinderPostSchema
      responses:
        '201':
          description: returns details of added _owned_otherbrand_cylinde
          content:
            application/json:
              schema: OwnedOtherBrandCylinderGetSchema
        '401':
          description: returns an unauthorized exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  error_message:
                    type: str
                    example: Missing authentication token
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
                    example: owned otherbrand cylinde  ... exists
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
          - Owned Other Brand Cylinders
    """
    data = request.json
    result = owned_otherbrand_cylinder_controller.create_other_brand_cylinders(data)
    return handle_result(result, schema=OwnedOtherBrandCylinderGetSchema)

@owned_otherbrand_cylinder.route("/<string:cylinder_id>", methods=["DELETE"])
@arg_validator(schema=OwnedOtherBrandCylinderRequestArgSchema, param="cylinder_id")
#@auth_required()
def delete_owned_otherbrand_cylinder(cylinder_id):
    """
    ---
    delete:
      description: delete aowned_otherbrand_cylinder
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: cylinder_id
          required: true
          schema:
            type: string
          description: the id of the order item
      responses:
        '204':
          description: returns none
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
                          order_item_id:
                          order_id:
                            type: array
                            items:
                              type: str
                              example: Not a valid UUID
                example:
                  app_exception: ValidationException
                  errorMessage:
                    order_id: ["Not a valid UUID"]
        '401':
          description: returns an unauthorized exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  error_message:
                    type: str
                    example: Missing authentication token
      tags:
          - Owned Other Brand Cylinders
    """
    result = owned_otherbrand_cylinder_controller.delete_other_brand_cylinder(cylinder_id)
    return handle_result(result)

@owned_otherbrand_cylinder.route("/<string:cylinder_id>", methods=["PATCH"])
@arg_validator(schema=OwnedOtherBrandCylinderRequestArgSchema, param="cylinder_id")
#@auth_required()
def update_owned_otherbrand_cylinder(cylinder_id):
    """
    ---
    patch:
      description: update owned_otherbrand_cylinder
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: OwnedOtherBrandCylinderPostSchema
      parameters:
        - in: path
          name: cylinder_id
          required: true
          schema:
            type: string
            description: the cylinder id
      responses:
        '200':
          description: returns details updated owned_otherbrand_cylinder
          content:
            application/json:
              schema: OwnedOtherBrandCylinderGetSchema
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
          '401':
          description: returns an unauthorized exception
          content:
            application/json:
              schema:
                type: object
                properties:
                  app_exception:
                    type: str
                    example: Unauthorized
                  error_message:
                    type: str
                    example: Missing authentication token
      tags:
          - Owned Other Brand Cylinders
    """

    data = request.json
    result = owned_otherbrand_cylinder_controller.update_other_brand_cylinders(cylinder_id, data)
    return handle_result(result, schema=OwnedOtherBrandCylinderGetSchema)
