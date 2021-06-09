import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from dataclasses import dataclass

from app import db

from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"


@dataclass
class Customer(db.Model):
    id: str
    phone_number: str
    first_name: str
    last_name: str
    id_type: str
    id_number: str
    status: str
    otp: str
    created: datetime.datetime
    modified: datetime.datetime
    __tablename__ = "customer"
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(0), unique=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    id_type = db.Column(db.String(20), nullable=False)
    id_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Enum(StatusEnum, name="status"),
                       default=StatusEnum.inactive,
                       nullable=False)
    otp = db.Column(db.String(6))
    created = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    modified = db.Column(db.DateTime(timezone=True), onupdate=datetime.datetime.now)
