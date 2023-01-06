from app.core.repository import SQLBaseRepository
from app.models.promotion_model import PromotionModel
from app.schema.promotion_schema import PromotionSchema
from app.core.exceptions import AppException, HTTPException

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"


class PromotionRepository(SQLBaseRepository):

    model = PromotionModel

    def __init__(self, promotion_schema: PromotionSchema):
        self.promotion_schema = promotion_schema
        super().__init__()

    def create(self, obj_data: dict):
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        db_server_obj: PromotionModel = super().create(obj_data)
        return db_server_obj
