import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func

from app import db


@dataclass
class RegistrationModel(db.Model):
    """
    This class defines attributes of potential customers
    potential_customer: users who are not done with the registration process
    """

    id: str
    phone_number: str
    otp_token: str
    otp_token_expiration: datetime.datetime
    retailer_id: str
    created: datetime.datetime
    modified: datetime.datetime

    __tablename__ = "registrations"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String())
    otp_token = db.Column(db.String(), nullable=True)
    otp_token_expiration = db.Column(db.DateTime(timezone=True))
    auth_token = db.Column(db.String())
    auth_token_expiration = db.Column(db.DateTime(timezone=True))
    retailer_id = db.Column(db.GUID(), nullable=True)
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
