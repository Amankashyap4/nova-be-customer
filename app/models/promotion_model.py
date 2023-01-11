from app import db
import uuid
from dataclasses import dataclass


@dataclass
class PromotionModel(db.Model):
    id: str
    tittle: str
    description: str
    image: str

    __tablename__ = "promotion"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    tittle = db.Column(db.String())
    description = db.Column(db.String())
    image = db.Column(db.String())
