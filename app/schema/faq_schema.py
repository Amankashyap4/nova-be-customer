from marshmallow import Schema, fields


class FaqSchema(Schema):
    question = fields.String(allow_none=True)
    answer = fields.String(allow_none=True)


class FaqRequestArgSchema(Schema):
    faq_id = fields.UUID()


class FaqGetSchema(Schema):
    id = fields.String(allow_none=True)
    question = fields.String(allow_none=True)
    answer = fields.String(allow_none=True)
