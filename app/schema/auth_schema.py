from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from app.enums import IDEnum, regex_type


class ConfirmTokenSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=4, max=6))
    id = fields.UUID(required=True)


class RequestResetPinSchema(Schema):
    token = fields.Str(required=True, validate=validate.Regexp(regex_type().get("pin")))
    id = fields.UUID(required=True)


class ConfirmedTokenSchema(Schema):
    confirmation_token = fields.Str(required=True)
    id = fields.UUID(required=True)


class AddPinSchema(Schema):
    pin = fields.Str(required=True, validate=validate.Regexp(regex_type().get("pin")))
    password_token = fields.Str(required=True)


class ResendTokenSchema(Schema):
    id = fields.UUID(required=True)


class PinChangeSchema(Schema):
    old_pin = fields.String(
        required=True, validate=validate.Regexp(regex_type().get("pin"))
    )
    new_pin = fields.String(
        required=True, validate=validate.Regexp(regex_type().get("pin"))
    )


class PinResetRequestSchema(Schema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(regex_type().get("phone_number"))
    )


class PinRequestSchema(Schema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(regex_type().get("phone_number"))
    )


class ResetPhoneSchema(Schema):
    new_phone_number = fields.Str()
    token = fields.String(required=True)


class PinResetSchema(Schema):
    token = fields.String(
        required=True, validate=validate.Regexp(regex_type().get("token"))
    )
    new_pin = fields.String(
        required=True, validate=validate.Regexp(regex_type().get("pin"))
    )
    id = fields.UUID(required=True)


class PasswordOtpSchema(Schema):
    token = fields.String(
        required=True, validate=validate.Regexp(regex_type().get("token"))
    )
    id = fields.UUID(required=True)


class LoginSchema(Schema):
    phone_number = fields.Str(validate=validate.Regexp(regex_type().get("phone_number")))
    pin = fields.Str(validate=validate.Length(min=4, max=4))


class TokenSchema(Schema):
    id = fields.UUID()
    access_token = fields.Str()
    refresh_token = fields.Str()


class TokenLoginSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    fullname = fields.Str()
    id_number = fields.Str()
    id_type = EnumField(IDEnum)
    phone_number = fields.Str()
    id = fields.UUID(required=True)


class ResetPinProcess(Schema):
    full_name = fields.Str()
    password_token = fields.Str()
    id = fields.UUID(required=True)


class ConfirmInfo(Schema):
    password_token = fields.Str()
    id = fields.UUID(required=True)


class RefreshTokenSchema(Schema):
    id = fields.UUID(required=True)
    refresh_token = fields.Str(required=True)
    access_token = fields.Str(dump_only=True)
