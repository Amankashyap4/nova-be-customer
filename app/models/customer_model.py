import datetime
from sqlalchemy.sql import func
from dataclasses import dataclass

from app import db
import uuid

from app.utils import IDEnum, StatusEnum


@dataclass
class Customer(db.Model):
    id: str
    phone_number: str
    full_name: str
    email: str
    birth_date: datetime.datetime
    id_expiry_date: datetime.datetime
    id_type: str
    id_number: str
    status: str
    otp: str
    otp_expiration: datetime.datetime
    created: datetime.datetime
    modified: datetime.datetime

    __tablename__ = "customers"

    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(), unique=True)
    full_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.DateTime(timezone=True))
    id_expiry_date = db.Column(db.DateTime(timezone=True))
    id_type = db.Column(
        db.Enum(IDEnum, name="id_type"), default=IDEnum.national_id, nullable=False
    )
    id_number = db.Column(db.String(20), nullable=False)
    auth_service_id = db.Column(db.GUID(), nullable=False)
    status = db.Column(
        db.Enum(StatusEnum, name="status"), default=StatusEnum.inactive, nullable=False
    )
    auth_token = db.Column(db.String(6))
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
    # new_phone_number = db.Column(db.String(60), nullable=True)
    otp_token = db.Column(db.String(4), nullable=True)
    otp_token_expiration = db.Column(db.DateTime(timezone=True))
