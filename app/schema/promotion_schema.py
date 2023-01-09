from marshmallow import Schema, fields


class PromotionSchema(Schema):
    tittle = fields.String()
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)


class PromotionRequestArgSchema(Schema):
    promotion_id = fields.UUID()

