from marshmallow import Schema, fields


class SafetySchema(Schema):
    title = fields.String()
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)


class SafetyRequestArgSchema(Schema):
    safety_id = fields.UUID()


class SafetyGetSchema(Schema):
    id = fields.UUID()
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)


class SafetyPatchSchema(Schema):
    title = fields.String()
    description = fields.String(allow_none=True)
    image = fields.String(allow_none=True)
