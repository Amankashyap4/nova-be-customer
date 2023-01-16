import uuid
from dataclasses import dataclass

from app import db


@dataclass
class ContactUsModel(db.Model):
    id: str
    name: str
    email: str
    subject: str
    compose_email: str

    __tablename__ = "contact_us"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(60))
    email = db.Column(db.String(60))
    subject = db.Column(db.String())
    compose_email = db.Column(db.String())
