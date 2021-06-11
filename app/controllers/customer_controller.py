from app.definitions import Result, ServiceResult
from app.repositories import CustomerRepository


class CustomerController:
    def __init__(self, customer_repository: CustomerRepository):
        self.repository = customer_repository

    def create(self, data):
        customer = self.repository.create(data)
        result = ServiceResult(Result(customer, 201))
        return result

    def show(self, customer_id):
        customer = self.repository.find_by_id(customer_id)
        result = ServiceResult(Result(customer, 200))
        return result

    def update(self, customer_id, data):
        customer = self.repository.update_by_id(customer_id, data)
        result = ServiceResult(Result(customer, 200))
        return result

    def delete(self, customer_id):
        self.repository.delete(customer_id)
        result = ServiceResult(Result({}, 204))
        return result


