from marshmallow import Schema, fields


class SafetySchema(Schema):
    title = fields.String()
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)


class PromotionRequestArgSchema(Schema):
    safety_id = fields.UUID()

