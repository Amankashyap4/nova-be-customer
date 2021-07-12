from marshmallow import fields, Schema, validate


class ConfirmTokenSchema(Schema):
    token = fields.Str(required=True)
    id = fields.UUID(required=True)


class AddPinSchema(Schema):
    pin = fields.Str(required=True)
    password_token = fields.Str(required=True)


class ResendTokenSchema(Schema):
    id = fields.UUID(required=True)


class LoginSchema(Schema):
    phone_number = fields.Str(
        validate=validate.Regexp(
            r"^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
        )
    )
    pin = fields.Str(validate=validate.Length(min=4, max=4))


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
