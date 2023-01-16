from marshmallow import Schema, fields


class ContactUsSchema(Schema):
    name = fields.String()
    email = fields.String()
    subject = fields.String()
    compose_email = fields.String()


class ContactUsRequestArgSchema(Schema):
    contact_id = fields.UUID()


class ContactUsGetSchema(Schema):
    id = fields.String(allow_none=True)
    name = fields.String(allow_none=True)
    email = fields.String(allow_none=True)
    subject = fields.String(allow_none=True)
    compose_email = fields.String(allow_none=True)
