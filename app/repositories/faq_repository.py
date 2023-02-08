from app.core.repository import SQLBaseRepository
from app.models.faq_model import FaqModel


class FaqRepository(SQLBaseRepository):

    model = FaqModel
