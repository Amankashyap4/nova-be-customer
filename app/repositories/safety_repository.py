from app.core.repository import SQLBaseRepository

from app.core.exceptions import AppException, HTTPException
from app.models.safety_model import SafetyModel
from app.schema.safety_schema import SafetySchema

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"


class SafetyRepository(SQLBaseRepository):

    model = SafetyModel

    def __init__(self, safety_schema: SafetySchema):
        self.safety_schema = safety_schema
        super().__init__()

    def create(self, obj_data: dict):
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        db_server_obj: SafetyModel = super().create(obj_data)
        return db_server_obj
