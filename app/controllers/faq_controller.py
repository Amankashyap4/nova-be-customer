from app.core import Result
from app.core.exceptions import AppException
from app.repositories.faq_repository import FaqRepository

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"
ASSERT_LIST_OBJ = "object {} is not a list"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class FaqController:
    def __init__(
        self,
        faq_repository: FaqRepository,
    ):
        self.faq_repository = faq_repository

    def all_faq(self):
        result = self.faq_repository.index()
        return Result(result, 200)

    def register_faq(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        question = self.faq_repository.create(obj_data)
        return Result(question, 201)

    def update_faq(self, obj_id: str, obj_data: dict):

        assert obj_id, ASSERT_OBJ.format("obj_id")
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        try:
            result = self.faq_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(context="faq id does not exist ")
        self.faq_repository.update_by_id(obj_id=result.id, obj_in=obj_data)
        return Result(result, 200)

    def delete_faq(self, obj_id: str):
        assert obj_id, ASSERT_OBJ.format("obj_id")

        try:
            result = self.faq_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="promotion id does not exist"
            )

        self.faq_repository.delete_by_id(obj_id=result.id)

        return Result(None, 204)
