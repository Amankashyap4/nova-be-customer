import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from dataclasses import dataclass

from app import db


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"


@dataclass
class Consumer(db.Model):
    id: str
    email: str
    name: str
    __tablename__ = "consumer"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(0), unique=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    id_type = db.Column(db.String(20), nullable=False)
    id_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Enum(StatusEnum, name="status"))
    otp = db.Column(db.String(6))
    created = db.Column(
        db.Datetime(timzone=True),
        nullable=False,
        server_default=func.now())
    modified = db.Column(db.Datetime(timezone=True), onupdate=datetime.datetime.now)
