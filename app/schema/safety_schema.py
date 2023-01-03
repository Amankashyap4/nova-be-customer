from marshmallow import Schema, fields, pre_load, validate


class SafetySchema(Schema):
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)
