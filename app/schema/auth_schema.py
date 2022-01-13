from marshmallow import fields, Schema, validate
from app import constants


class ConfirmTokenSchema(Schema):
    # token = fields.Str(required=True, validate=validate.Regexp(r"\b[0-9]{6}\b"))
    token = fields.Str(required=True)
    id = fields.UUID(required=True)


class RequestResetPinSchema(Schema):
    # token = fields.Str(required=True, validate=validate.Regexp(r"\b[0-9]{4}\b"))
    token = fields.Str(required=True)
    id = fields.UUID(required=True)


class ConfirmedTokenSchema(Schema):
    conformation_token = fields.Str(required=True)
    id = fields.UUID(required=True)


class AddPinSchema(Schema):
    pin = fields.Str(required=True, validate=validate.Regexp(r"\b[0-9]{4}\b"))
    password_token = fields.Str(required=True)


class ResendTokenSchema(Schema):
    id = fields.UUID(required=True)


class PinChangeSchema(Schema):
    old_pin = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{4}\b"))
    new_pin = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{4}\b"))


class PinResetRequestSchema(Schema):
    phone_number = fields.Str(validate=validate.Regexp(constants.PHONE_NUMBER_REGEX))


class ResetPhoneSchema(Schema):
    new_phone_number = fields.Str(validate=validate.Regexp(constants.PHONE_NUMBER_REGEX))
    token = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{6}\b"))


class PinResetSchema(Schema):
    # token = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{6}\b"))
    token = fields.String(required=True)
    new_pin = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{4}\b"))
    id = fields.UUID(required=True)


class PasswordOtpSchema(Schema):
    # token = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{6}\b"))
    token = fields.String(required=True)
    id = fields.UUID(required=True)


class LoginSchema(Schema):
    phone_number = fields.Str(validate=validate.Regexp(constants.PHONE_NUMBER_REGEX))
    pin = fields.Str(validate=validate.Length(min=4, max=4))


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()


class TokenLoginSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    fullname = fields.Str()
    id_number = fields.Str()
    id_type = fields.Str()
    phone_number = fields.Str()
    id = fields.UUID(required=True)


class ResetPinProcess(Schema):
    full_name = fields.Str()
    password_token = fields.Str()
    id = fields.UUID(required=True)


class ConformInfo(Schema):
    password_token = fields.Str()
    id = fields.UUID(required=True)
