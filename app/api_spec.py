"""OpenAPI v3 Specification"""

# apispec via OpenAPI
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

# Create an APISpec
from app.schema import (
    CustomerSchema,
    CustomerCreateSchema,
    CustomerUpdateSchema,
    ConfirmTokenSchema,
    AddPinSchema,
    ResendTokenSchema,
    LoginSchema,
    TokenSchema,
    PinChangeSchema,
    PinResetSchema,
    PinResetRequestSchema,
)

spec = APISpec(
    title="Nova Customer Service",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Security
api_key_scheme = {"type": "apiKey", "in": "header", "name": "X-API-Key"}
bearer_scheme = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
spec.components.security_scheme("ApiKeyAuth", api_key_scheme)
spec.components.security_scheme("bearerAuth", bearer_scheme)

# register schemas with spec
# example
spec.components.schema("Customer", schema=CustomerSchema)
spec.components.schema("CustomerCreate", schema=CustomerCreateSchema)
spec.components.schema("CustomerUpdate", schema=CustomerUpdateSchema)
spec.components.schema("ConfirmToken", schema=ConfirmTokenSchema)
spec.components.schema("PinData", schema=AddPinSchema)
spec.components.schema("ResendTokenData", schema=ResendTokenSchema)
spec.components.schema("LoginData", schema=LoginSchema)
spec.components.schema("TokenData", schema=TokenSchema)
spec.components.schema("PinChange", schema=PinChangeSchema)
spec.components.schema("PinReset", schema=PinResetSchema)
spec.components.schema("PinResetRequest", schema=PinResetRequestSchema)


# add swagger tags that are used for endpoint annotation
tags = [
    {"name": "Authentication", "description": "For customer authentication."},
    {"name": "Customer", "description": "Customer crud operation and others"},
]

for tag in tags:
    print(f"Adding tag: {tag['name']}")
    spec.tag(tag)
