from app.core.repository import SQLBaseRepository
from app.models.contact_us_model import ContactUsModel
from app.schema.contact_us_schema import ContactUsSchema

ASSERT_OBJ = "missing object data {}"
ASSERT_DICT_OBJ = "object {} is not a dict"


class ContactUsRepository(SQLBaseRepository):

    model = ContactUsModel

    def __init__(self, contact_us_schema: ContactUsSchema):
        self.contact_us_schema = contact_us_schema
        super().__init__()

    def create(self, obj_data: dict):
        assert obj_data, ASSERT_OBJ.format("obj_data")
        assert isinstance(obj_data, dict), ASSERT_DICT_OBJ.format("obj_data")

        db_server_obj: ContactUsModel = super().create(obj_data)
        return db_server_obj
