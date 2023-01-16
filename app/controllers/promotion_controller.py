from app.core import Result
from app.core.exceptions import AppException
from app.repositories.promotion_repository import PromotionRepository

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"
ASSERT_LIST_OBJ = "object {} is not a list"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class PromotionController:
    def __init__(
        self,
        promotion_repository: PromotionRepository,
    ):
        self.promotion_repository = promotion_repository

    def index(self):

        result = self.promotion_repository.index()
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        promotion = self.promotion_repository.create(obj_data)
        return Result(promotion, 201)

    def update_promotion(self, obj_id: str, obj_data: dict):

        assert obj_id, ASSERT_OBJ.format("obj_id")
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        try:
            result = self.promotion_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(context="promotion id does not exist ")
        self.promotion_repository.update_by_id(obj_id=result.id, obj_in=obj_data)
        return Result(result, 201)

    def delete(self, obj_id: str):
        assert obj_id, ASSERT_OBJ.format("obj_id")

        try:
            result = self.promotion_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(context="promotion id does not exist ")

        self.promotion_repository.delete_by_id(obj_id=result.id)

        return Result(None, 204)
