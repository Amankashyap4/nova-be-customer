import re

from marshmallow import Schema, fields, pre_load, validate
from marshmallow_enum import EnumField

from app.enums import AccountStatusEnum, IDEnum, RegularExpression


class CustomerSchema(Schema):
    id = fields.UUID(allow_none=True)
    phone_number = fields.String()
    full_name = fields.String(allow_none=True)
    email = fields.String(allow_none=True)
    birth_date = fields.Date(allow_none=True)
    id_expiry_date = fields.Date(allow_none=True)
    id_type = EnumField(IDEnum, allow_none=True)
    id_number = fields.String(allow_none=True)
    status = EnumField(AccountStatusEnum, allow_none=True)
    profile_image = fields.String(allow_none=True)
    auth_service_id = fields.UUID(allow_none=True)
    retailer_id = fields.UUID(allow_none=True)
    level = fields.String(allow_none=True)
    last_login = fields.DateTime(allow_none=True)
    pre_signed_post = fields.Dict(allow_none=True)
    created = fields.DateTime()
    modified = fields.DateTime()

    class Meta:
        ordered = True
        fields = [
            "id",
            "phone_number",
            "full_name",
            "email",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
            "profile_image",
            "auth_service_id",
            "retailer_id",
            "status",
            "level",
            "last_login",
            "pre_signed_post",
            "created",
            "modified",
        ]

    @pre_load
    def international_format(self, field, **kwargs):
        split_regex = RegularExpression.phone_number.value.split("|")
        format_type = "|".join(split_regex[:2]), "|".join(split_regex[2:])
        phone_number = field.get("phone_number")
        if phone_number and re.fullmatch(format_type[0], phone_number):
            local_format = re.sub(r"\+?233", "0", phone_number)
            field["phone_number"] = local_format
            return field
        return field


class CustomerUpdateSchema(CustomerSchema):
    email = fields.Email()

    class Meta:
        fields = ["email"]


class CustomerSignUpSchema(CustomerSchema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.phone_number.value)
    )

    class Meta:
        fields = ["phone_number"]


class CustomerInfoSchema(CustomerSchema):
    id = fields.UUID()
    full_name = fields.String(validate=validate.Length(min=3))
    birth_date = fields.Date()
    id_expiry_date = fields.Date()
    id_type = EnumField(IDEnum)
    id_number = fields.String()
    confirmation_token = fields.String()

    class Meta:
        fields = [
            "id",
            "full_name",
            "birth_date",
            "id_expiry_date",
            "id_type",
            "id_number",
            "confirmation_token",
        ]


class UpdatePhoneSchema(Schema):
    phone_number = fields.String(
        required=True, validate=validate.Regexp(RegularExpression.phone_number.value)
    )
    token = fields.Str(required=True)


class CustomerRequestArgSchema(CustomerSchema):
    phone_number = fields.String(
        validate=validate.Regexp(RegularExpression.phone_number.value)
    )
    customer_id = fields.UUID()
    user_id = fields.UUID()
    page = fields.Integer()
    per_page = fields.Integer()

    class Meta:
        fields = ["phone_number", "customer_id", "user_id", "page", "per_page"]


class RetailerSignUpCustomerSchema(CustomerSchema):
    """
    This schema validates request data when a customer is onboarded by a retailer
    """

    phone_number = fields.Str(
        required=True, validate=validate.Regexp(RegularExpression.phone_number.value)
    )
    retailer_id = fields.UUID(required=True)

    class Meta:
        fields = ["phone_number", "retailer_id"]
