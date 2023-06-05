from app.core import Result
from app.core.exceptions import AppException
from app.repositories import OwnedOtherBrandCylinderRepository, CustomerRepository

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"
ASSERT_LIST_OBJ = "object {} is not a list"
ASSERT_OBJECT_IS_DICT = "object data not a dict"


class OwnedOtherBrandCylinderController:
    def __init__(
        self,
        owned_other_brand_cylinder_repository: OwnedOtherBrandCylinderRepository,
        customer_repository: CustomerRepository,
    ):
        self.owned_other_brand_cylinder_repository = owned_other_brand_cylinder_repository
        self.customer_repository = customer_repository
    def all_other_brand_cylinders(self):
        result = self.owned_other_brand_cylinder_repository.index()
        return Result(result, 200)

    def get_other_brand_cylinders(self,obj_id):
        try:
            result = self.owned_other_brand_cylinder_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=f"cylinders with id {obj_id} does not exist"
            )
        return Result(result, 200)

    def create_other_brand_cylinders(self, obj_data):
        assert obj_data, ASSERT_OBJECT_IS_DICT
        try:
            result = self.customer_repository.find(
                {"id": obj_data.get("customer_id")})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="customer id does not exist ")

        data = self.owned_other_brand_cylinder_repository.create(obj_data)
        return Result(data, 201)

    def delete_other_brand_cylinder(self,obj_id):
        assert obj_id, ASSERT_OBJ.format("obj_id")

        try:
            result = self.owned_other_brand_cylinder_repository.find({"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="cylinder id does not exist"
            )

        self.owned_other_brand_cylinder_repository.delete_by_id(obj_id=result.id)

        return Result(None, 204)

    def update_other_brand_cylinders(self, obj_id: str, obj_data: dict):
        assert obj_id, ASSERT_OBJ.format("obj_id")
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")
        try:
            result = self.owned_other_brand_cylinder_repository.find(
                {"id": obj_id})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="cylinder id does not exist ")
        try:
            customer_id = obj_data.get("customer_id")
            if customer_id:
                customer = self.customer_repository.find({"id": obj_data.get("customer_id")})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message="customer id does not exist ")

        self.owned_other_brand_cylinder_repository.update_by_id(obj_id=result.id,obj_in=obj_data)
        return Result(result, 200)

