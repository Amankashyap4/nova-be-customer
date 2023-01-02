from app.core.repository import SQLBaseRepository
from app.models import LoginAttemptModel


class LoginAttemptRepository(SQLBaseRepository):
    model = LoginAttemptModel
