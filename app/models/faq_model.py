import uuid
from dataclasses import dataclass

from app import db


@dataclass
class FaqModel(db.Model):
    id: str
    question: str
    answer: str

    __tablename__ = "faq"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    question = db.Column(db.String())
    answer = db.Column(db.String())
