from app import db
import uuid

class SafetyModel(db.Model):

    id: str
    title: str
    description: str
    image: str
    __tablename__ = "safety"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String())
    description = db.Column(db.String())
    image = db.Column(db.String())
