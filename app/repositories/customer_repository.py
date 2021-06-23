from app.definitions.repository import SQLBaseRepository
from app.models import Customer


class CustomerRepository(SQLBaseRepository):
    model = Customer

    def find_by_number(self, phone_number):
        assert phone_number, "Phone number missing"
        customer = self.model.query.filter_by(phone_number=phone_number).first()
        return customer
