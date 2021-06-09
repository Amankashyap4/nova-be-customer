from app.definitions.repository import SQLBaseRepository
from app.models import Customer


class CustomerRepository(SQLBaseRepository):
    model = Customer
