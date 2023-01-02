import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func

from app import db
from app.enums import AccountStatusEnum


@dataclass
class LoginAttemptModel(db.Model):
    id: uuid
    phone_number: str
    request_ip_address: str
    failed_login_attempts: int
    failed_login_time: datetime.datetime
    status: AccountStatusEnum
    expires_in: datetime.datetime
    created: datetime.datetime
    modified: datetime.datetime

    __tablename__ = "login_attempts"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(), nullable=False)
    request_ip_address = db.Column(db.String(), nullable=True)
    failed_login_attempts = db.Column(db.Integer(), nullable=False)
    failed_login_time = db.Column(db.DateTime(timezone=True), nullable=False)
    lockout_expiration = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(
        db.Enum(AccountStatusEnum, name="status"),
        default=AccountStatusEnum.active,
        nullable=False,
    )
    expires_in = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
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
