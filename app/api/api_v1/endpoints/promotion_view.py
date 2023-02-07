import pinject
from flask import Blueprint, request
from app.controllers import PromotionController
from app.core.service_result import handle_result
from app.repositories import PromotionRepository
from app.schema import PromotionGetSchema, PromotionSchema, PromotionRequestArgSchema
from app.utils import arg_validator, auth_required, validator

promotion = Blueprint("promotion", __name__)
obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        PromotionController,
        PromotionRepository,
    ],
)
promotion_controller: PromotionController = obj_graph.provide(PromotionController)



@promotion.route("/promotion", methods=["GET"])
def get_promotion():
    """
    ---
    get:
      description: retrieve all promotion in the system
      responses:
        '200':
          description: returns details of all promotion
          content:
            application/json:
              schema:
                type: array
                items: PromotionSchema
      tags:
          - Promotion
    """

    result = promotion_controller.index()
    return handle_result(result, schema=PromotionGetSchema, many=True)


@promotion.route("/promotion", methods=["POST"])
@validator(schema=PromotionSchema)
def create_promotion():
    """
    ---
    post:
      description: create promotion
      requestBody:
        required: true
        content:
          application/json:
            schema: PromotionSchema
      responses:
        '201':
          description: returns details of added promotion
          content:
            application/json:
              schema: PromotionSchema
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
                    example: promotion ... exists
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
          - Promotion
    """
    data = request.json
    result = promotion_controller.register(data)
    return handle_result(result, schema=PromotionGetSchema)


@promotion.route("/promotion/<string:promotion_id>", methods=["PATCH"])
@arg_validator(schema=PromotionRequestArgSchema, param="promotion_id")
def update_promotion(promotion_id):
    """
    ---
    patch:
      description: update promotion
      requestBody:
        required: true
        content:
          application/json:
            schema: PromotionSchema
      parameters:
        - in: path
          name: promotion_id
          required: true
          schema:
            type: string
            description: the promotion's id
      responses:
        '201':
          description: returns details updated promotion
          content:
            application/json:
              schema: PromotionSchema
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
          - Promotion
    """
    data = request.json
    result = promotion_controller.update_promotion(promotion_id, data)
    return handle_result(result, schema=PromotionGetSchema)


@promotion.route("/promotion/<string:promotion_id>", methods=["DELETE"])
@arg_validator(schema=PromotionRequestArgSchema, param="promotion_id")
def delete_promotion(promotion_id):
    """
    ---
    delete:
      description: delete promotion with id specified in path
      parameters:
        - in: path
          name: promotion_id
          required: true
          schema:
            type: string
          description: the promotion id
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
          - Promotion
    """
    result = promotion_controller.delete(promotion_id)
    return handle_result(result, schema=PromotionGetSchema)
