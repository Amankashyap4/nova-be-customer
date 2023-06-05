import datetime
import uuid
from dataclasses import dataclass
from app import db
from app.enums import Cylinder_quality, CylinderSize, CylinderType


@dataclass
class OwnedOtherBrandCylindersModel(db.Model):
    id: str
    customer_id: str
    age: str
    size: str
    type: str
    company_name: str
    measuring_unit: str
    image_url: str
    status: bool

    cylinder_quality: str
    __tablename__ = "owned_otherbrand_cylinders"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(db.GUID(), db.ForeignKey("customers.id"), nullable=False, index=True)
    name = db.Column(db.String(60), nullable=True)
    age = db.Column(db.String(), nullable=False)
    size = db.Column(db.Enum(CylinderSize, name="size"), nullable=True)
    type = db.Column(db.Enum(CylinderType, name="type"), nullable=True)
    company_name = db.Column(db.String(200), nullable=False)
    measuring_unit = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String)
    status = db.Column(db.Boolean, nullable=True)
    cylinder_quality = db.Column(
        db.Enum(Cylinder_quality, name="cylinder_quality"), default=Cylinder_quality.null, nullable=False
    )
