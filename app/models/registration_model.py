import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func

from app import db


@dataclass
class RegistrationModel(db.Model):
    id: str
    phone_number: str
    otp_token: str
    otp_token_expiration: datetime.datetime
    created: datetime.datetime
    modified: datetime.datetime

    __tablename__ = "registrations"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String())
    otp_token = db.Column(db.String(), nullable=True)
    otp_token_expiration = db.Column(db.DateTime(timezone=True))
    auth_token = db.Column(db.String())
    auth_token_expiration = db.Column(db.DateTime(timezone=True))
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )