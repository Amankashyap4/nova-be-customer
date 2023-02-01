from app.core.repository import SQLBaseRepository
from app.models import CustomerHistoryModel


class CustomerHistoryRepository(SQLBaseRepository):

    model = CustomerHistoryModel
