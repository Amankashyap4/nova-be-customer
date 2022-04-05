import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.enums import IDEnum, StatusEnum


@dataclass
class CustomerModel(db.Model):
    id: str
    phone_number: str
    full_name: str
    email: str
    birth_date: datetime.datetime
    id_expiry_date: datetime.datetime
    id_type: str
    id_number: str
    pin: str
    status: str
    auth_service_id: str
    profile_image: str
    created: datetime.datetime
    modified: datetime.datetime

    __tablename__ = "customers"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(), unique=True, nullable=False)
    full_name = db.Column(db.String(60))
    email = db.Column(db.String(60))
    birth_date = db.Column(db.Date())
    id_expiry_date = db.Column(db.Date())
    id_type = db.Column(
        db.Enum(IDEnum, name="id_type"), default=IDEnum.null, nullable=False
    )
    id_number = db.Column(db.String(20))
    hash_pin = db.Column("pin", db.String())
    auth_service_id = db.Column(db.GUID())
    status = db.Column(
        db.Enum(StatusEnum, name="status"), default=StatusEnum.inactive, nullable=False
    )
    auth_token = db.Column(db.String())
    auth_token_expiration = db.Column(db.DateTime(timezone=True))
    profile_image = db.Column(db.String())
    otp_token = db.Column(db.String(), nullable=True)
    otp_token_expiration = db.Column(db.DateTime(timezone=True))
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @property
    def pin(self):
        return self.hash_pin

    @pin.setter
    def pin(self, pin):
        self.hash_pin = generate_password_hash(pin, method="sha256")

    def verify_pin(self, pin):
        return check_password_hash(self.hash_pin, pin)


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
