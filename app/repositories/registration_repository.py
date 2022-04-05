from app.core.repository import SQLBaseRepository
from app.models import RegistrationModel


class RegistrationRepository(SQLBaseRepository):
    model = RegistrationModel
