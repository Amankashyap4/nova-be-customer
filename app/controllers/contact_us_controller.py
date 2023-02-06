from app.core import Result
from app.core.exceptions import AppException
from app.repositories.contact_us_repository import ContactUsRepository

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"
ASSERT_LIST_OBJ = "object {} is not a list"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class ContactUsController:
    def __init__(
        self,
        contact_us_repository: ContactUsRepository,
    ):
        self.contact_us_repository = contact_us_repository

    def index(self):

        result = self.contact_us_repository.index()
        return Result(result, 200)

    def register(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT

        contact_us = self.contact_us_repository.create(obj_data)
        return Result(contact_us, 201)

    def update_contact_us(self, obj_id: str, obj_data: dict):

        assert obj_id, ASSERT_OBJ.format("obj_id")
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        try:
            result = self.contact_us_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(context="contact_us id does not exist ")
        self.contact_us_repository.update_by_id(obj_id=result.id, obj_in=obj_data)
        return Result(result, 200)

    def delete(self, obj_id: str):
        assert obj_id, ASSERT_OBJ.format("obj_id")

        try:
            result = self.contact_us_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="contact_us id does not exist"
            )

        self.contact_us_repository.delete_by_id(obj_id=result.id)

        return Result(None, 204)
