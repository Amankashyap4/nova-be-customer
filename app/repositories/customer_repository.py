from app.core.repository import SQLBaseRepository
from app.models import Customer


class CustomerRepository(SQLBaseRepository):
    model = Customer
