from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from app.enums import Cylinder_quality, CylinderSize, CylinderType


class OwnedOtherBrandCylinderRequestArgSchema(Schema):
    cylinder_id = fields.UUID()

class OwnedOtherBrandCylinderPostSchema(Schema):
    customer_id = fields.UUID()
    name = fields.String()
    age = fields.String()
    size = EnumField(CylinderSize)
    type = EnumField(CylinderType)
    company_name = fields.String()
    measuring_unit =fields.String()
    image_url =fields.String()
    status = fields.Boolean()
    cylinder_quality = EnumField(Cylinder_quality)

class OwnedOtherBrandCylinderGetSchema(Schema):
    id = fields.UUID()
    customer_id = fields.UUID()
    name = fields.String()
    age = fields.String()
    size = fields.String()
    type = fields.String()
    company_name = fields.String()
    measuring_unit =fields.String()
    image_url =fields.String()
    status = fields.Boolean()
    cylinder_quality = EnumField(Cylinder_quality)
