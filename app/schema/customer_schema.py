from marshmallow import Schema, fields, validate

ID_TYPE = ["national id", "drivers license", "passport", "voters id"]
CONSUMER_STATUS = ["active", "inactive", "blocked"]


class CustomerSchema(Schema):
    id = fields.Str()
    phone_number = fields.Str(required=True, validate=validate.Length(min=10))
    first_name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True, validate=validate.Length(min=2))
    id_type = fields.Str(required=True, validate=validate.OneOf(
        ID_TYPE
    ))
    id_number = fields.Str(required=True, validate=validate.Length(min=5))
    status = fields.Str(required=True, validate=validate.OneOf(
        CONSUMER_STATUS
    ))
    otp = fields.Str(validate=validate.Length(min=6, max=6))
    created = fields.DateTime(required=True)
    modified = fields.DateTime(required=True)

    class Meta:
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "id_type",
            "id_number",
            "status",
            "otp",
            "created",
            "modified"
        ]


class CustomerCreateSchema(Schema):
    phone_number = fields.Str(required=True, validate=validate.Length(min=10))
    first_name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True, validate=validate.Length(min=2))
    id_type = fields.Str(required=True, validate=validate.OneOf(
        ID_TYPE
    ))
    id_number = fields.Str(required=True, validate=validate.Length(min=5))
    status = fields.Str(validate=validate.OneOf(
        CONSUMER_STATUS
    ))

    class Meta:
        fields = [
            "phone_number",
            "first_name",
            "last_name",
            "id_type",
            "id_number",
            "status",
            "otp",
            "created",
            "modified"
        ]


class CustomerUpdateSchema(Schema):
    phone_number = fields.Str(validate=validate.Length(min=10))
    first_name = fields.Str(validate=validate.Length(min=2))
    last_name = fields.Str(validate=validate.Length(min=2))
    id_type = fields.Str(validate=validate.OneOf(
        ["national id", "drivers license", "passport", "voters id"]
    ))
    id_number = fields.Str(validate=validate.Length(min=5))
    status = fields.Str(validate=validate.OneOf(
        ["active", "inactive", "blocked"]
    ))

    class Meta:
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "id_type",
            "id_number",
            "status",
            "otp",
            "created",
            "modified"
        ]
