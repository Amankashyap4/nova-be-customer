import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func

from app import db


@dataclass
class CustomerHistoryModel(db.Model):
    """
    This class defines customer properties saved in history table. Records are
    populated using a trigger set on the customers relation.
    """

    id: str
    customer_id: str
    phone_number: str
    email: str
    action: str
    status: str
    valid_from: datetime
    valid_to: datetime
    created: datetime

    __tablename__ = "customers_history"
    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(
        db.GUID(), db.ForeignKey("customers.id"), nullable=False, index=True
    )
    phone_number = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=True)
    action = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    valid_from = db.Column(db.DateTime(timezone=True), nullable=False)
    valid_to = db.Column(db.DateTime(timezone=True), nullable=True)
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
