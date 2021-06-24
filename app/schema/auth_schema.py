from marshmallow import fields, Schema


class ConfirmTokenSchema(Schema):
    token = fields.Str(required=True)
    id = fields.UUID(required=True)


class AddPinSchema(Schema):
    pin = fields.Str(required=True)
    password_token = fields.Str(required=True)


class ResendTokenSchema(Schema):
    id = fields.UUID(required=True)
