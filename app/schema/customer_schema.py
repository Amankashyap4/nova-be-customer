from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from app import constants
from app.utils import StatusEnum, IDEnum


class CustomerSignUpSchema(Schema):
    phone_number = fields.Str(
        validate=validate.Regexp(constants.PHONE_NUMBER_REGEX),
        required=True,
    )

    class Meta:
        fields = [
            "phone_number",
        ]


class CustomerInfoSchema(Schema):
    id = fields.UUID()
    full_name = fields.Str(required=True, validate=validate.Length(min=2))
    birth_date = fields.Date(required=True)
    id_expiry_date = fields.Date(required=True)
    id_type = EnumField(IDEnum)
    id_number = (fields.Str(validate=validate.Length(min=5)),)
    conformation_token = (fields.Str(validate=validate.Length(min=5)),)

    class Meta:
        fields = [
            "id",
            "full_name",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
            "conformation_token",
        ]


class CustomerCreateSchema(Schema):
    pass


class UpdatePhoneSchema(Schema):
    token = fields.Str(required=True)


class CustomerSchema(Schema):

    id = fields.UUID()
    phone_number = fields.Str(validate=validate.Regexp(constants.PHONE_NUMBER_REGEX))
    full_name = fields.Str(validate=validate.Length(min=2))
    birth_date = fields.Date()
    id_expiry_date = fields.Date()
    id_type = EnumField(IDEnum)
    id_number = fields.Str(validate=validate.Length(min=5))
    status = EnumField(StatusEnum)
    created = fields.DateTime()
    modified = fields.DateTime()

    class Meta:
        fields = [
            "id",
            "phone_number",
            "full_name",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
            "status",
            "created",
            "modified",
        ]


class CustomerUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2))
    birth_date = fields.Date()
    id_expiry_date = fields.Date()
    id_type = EnumField(IDEnum)
    id_number = fields.Str(validate=validate.Length(min=5))

    class Meta:
        fields = [
            "full_name",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
        ]


class CustomerAddInfoSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2))
    birth_date = fields.Date()
    id_expiry_date = fields.Date()
    id_type = fields.Str(required=True)
    id_number = fields.Str(validate=validate.Length(min=5))
    id = fields.UUID()
    conformation_token = fields.Str(validate=validate.Length(min=5))

    class Meta:
        fields = [
            "full_name",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
            "id",
            "conformation_token",
        ]
