from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from app.enums import IDEnum, RegularExpression


class ConfirmTokenSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=4, max=6))
    id = fields.UUID(required=True)


class RequestResetPinSchema(Schema):
    token = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.pin.value)
    )
    id = fields.UUID(required=True)


class ConfirmedTokenSchema(Schema):
    confirmation_token = fields.Str(required=True)
    id = fields.UUID(required=True)


class AddPinSchema(Schema):
    pin = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.pin.value)
    )
    password_token = fields.Str(required=True)


class ResendTokenSchema(Schema):
    id = fields.UUID(required=True)


class PinChangeSchema(Schema):
    old_pin = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.pin.value)
    )
    new_pin = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.pin.value)
    )


class PinResetRequestSchema(Schema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.phone_number.value)
    )


class PinRequestSchema(Schema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.phone_number.value)
    )


class ResetPhoneSchema(Schema):
    new_phone_number = fields.Str()
    token = fields.String(required=True)


class PinResetSchema(Schema):
    token = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.token.value)
    )
    new_pin = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.pin.value)
    )
    id = fields.UUID(required=True)


class PasswordOtpSchema(Schema):
    token = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.token.value)
    )
    id = fields.UUID(required=True)


class LoginSchema(Schema):
    phone_number = fields.Str(
        validate=validate.Regexp(RegularExpression.phone_number.value)
    )
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
