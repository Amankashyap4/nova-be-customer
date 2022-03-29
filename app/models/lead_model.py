import datetime
import uuid
from sqlalchemy.sql import func

from app import db


class Lead(db.Model):
    id: str
    phone_number: str
    full_name: str
    email: str
    birth_date: datetime.datetime
    id_expiry_date: datetime.datetime
    id_type: str
    id_number: str
    otp: str
    created: datetime.datetime
    __tablename__ = "lead"

    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = db.Column(db.String(0), nullable=False, unique=True)
    full_name = db.Column(db.String(60))
    email = db.Column(db.String(60), nullable=False, unique=True)
    birth_date = db.Column(db.DateTime(timezone=True))
    id_expiry_date = db.Column(db.DateTime(timezone=True))
    id_type = db.Column(db.String(20))
    id_number = db.Column(db.String(20))
    otp = db.Column(db.String(6))
    otp_expiration = db.Column(db.DateTime(timezone=True))
    password_token = db.Column(db.String())
    password_token_expiration = db.Column(db.DateTime(timezone=True))
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
