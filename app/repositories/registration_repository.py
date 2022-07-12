from app.core.repository import SQLBaseRepository
from app.models import RegistrationModel


class RegistrationRepository(SQLBaseRepository):
    """
    This class handles the database operations for potential customer's data.
    potential customer: users who are not done with the registration process.
    """

    model = RegistrationModel
