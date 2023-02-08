from app.core.repository import SQLBaseRepository
from app.models.safety_model import SafetyModel


class SafetyRepository(SQLBaseRepository):

    model = SafetyModel

