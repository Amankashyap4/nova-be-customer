from app.core import Result
from app.core.exceptions import AppException
from app.repositories.safety_repository import SafetyRepository

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"
ASSERT_LIST_OBJ = "object {} is not a list"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class SafetyController:

    def __init__(
        self,
        safety_repository: SafetyRepository,
    ):
        self.safety_repository = safety_repository

    def index(self):

        result = self.safety_repository.index()
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        safety = self.safety_repository.create(obj_data)
        return Result(safety, 201)

    def update_safety(self, obj_id: str, obj_data: dict):

        assert obj_id, ASSERT_OBJ.format("obj_id")
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        try:
            result = self.safety_repository.find(
                {
                    "id": obj_id
                }
            )
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context="safety id does not exist "
            )
        self.safety_repository.update_by_id(
            obj_id=result.id,
            obj_in=obj_data
        )
        return Result(result, 201)

    def delete(self, obj_id: str):
        assert obj_id, ASSERT_OBJ.format("obj_id")

        try:
            result = self.safety_repository.find(
                {
                    "id": obj_id
                }
            )
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                context="safety id does not exist "
            )

        self.safety_repository.delete(obj_id=result.id)

        return Result(None, 204)
