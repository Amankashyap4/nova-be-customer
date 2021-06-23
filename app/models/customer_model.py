import datetime
import enum
from sqlalchemy.sql import func
from dataclasses import dataclass

from app import db
import uuid


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    first_time = "first_time"


class IDEnum(enum.Enum):
    national_id = "national id"
    drivers_license = "drivers license"
    passport = "passport"
    voters_id = "voters id"


@dataclass
class Customer(db.Model):
    id: str
    phone_number: str
    first_name: str
    last_name: str
    id_type: str
    id_number: str
    status: str
    created: datetime.datetime
    modified: datetime.datetime
    __tablename__ = "customer"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(0), unique=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    id_type = db.Column(
        db.Enum(IDEnum, name="id"), default=StatusEnum.inactive, nullable=False
    )
    id_number = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum(StatusEnum, name="status"), default=StatusEnum.inactive, nullable=False
    )
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(db.DateTime(timezone=True), onupdate=datetime.datetime.now)
