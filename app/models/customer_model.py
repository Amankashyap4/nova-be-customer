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
        db.Enum(IDEnum, name="id_type"), default=IDEnum.national_id, nullable=False
    )
    id_number = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum(StatusEnum, name="status"), default=StatusEnum.inactive, nullable=False
    )
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
