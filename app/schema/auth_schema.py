from marshmallow import fields, Schema


class ConfirmTokenSchema(Schema):
    token = fields.Str()
    id = fields.UUID()


class AddPinSchema(Schema):
    pin = fields.Str()
    id = fields.UUID()
