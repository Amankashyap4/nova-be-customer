from app.core.repository import SQLBaseRepository
from app.models.faq_model import FaqModel
from app.schema.faq_schema import FaqSchema

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"


class FaqRepository(SQLBaseRepository):

    model = FaqModel

    def __init__(self, faq_schema: FaqSchema):
        self.faq_schema = faq_schema
        super().__init__()

    def create(self, obj_data: dict):
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        db_server_obj: FaqModel = super().create(obj_data)
        return db_server_obj
