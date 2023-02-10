from app.core.exceptions import HTTPException
from app.core.repository import SQLBaseRepository
from app.models import CustomerModel
from app.schema import CustomerSchema
from app.services import RedisService

from .cache_object import (
    cache_list_of_object,
    cache_object,
    deserialize_cached_object,
    deserialize_list_of_cached_object,
)

SINGLE_RECORD_CACHE_KEY = "customer_{}"
ALL_RECORDS_CACHE_KEY = "all_customers"


class CustomerRepository(SQLBaseRepository):
    """
    This class handles the database operations and record caching of customers data.
    customers: users who are done with the registration process.
    """

    model = CustomerModel

    def __init__(self, redis_service: RedisService, customer_schema: CustomerSchema):
        self.redis_service = redis_service
        self.customer_schema = customer_schema
        super().__init__()

    def index(self):
        try:
            list_of_cached_object = self.redis_service.get(ALL_RECORDS_CACHE_KEY)
            if list_of_cached_object:
                deserialized_objects = deserialize_list_of_cached_object(
                    obj_data=list_of_cached_object,
                    obj_schema=self.customer_schema,
                    obj_model=self.model,
                )
                return deserialized_objects
            server_data = cache_list_of_object(
                obj_data=super().index(),
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return server_data
        except HTTPException:
            return super().index()

    def create(self, data):
        server_data = super().create(self.customer_schema.load(data, unknown="include"))
        try:
            obj_data = cache_object(
                obj_data=server_data,
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(server_data),
            )
            _ = cache_list_of_object(
                obj_data=super().index(),
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return obj_data
        except HTTPException:
            return server_data

    def get_by_id(self, obj_id):
        try:
            cached_object = self.redis_service.get(
                SINGLE_RECORD_CACHE_KEY.format(obj_id)
            )
            if cached_object:
                deserialized_object = deserialize_cached_object(
                    obj_data=cached_object,
                    obj_model=self.model,
                    obj_schema=self.customer_schema,
                )
                return deserialized_object
            object_data = cache_object(
                obj_data=super().find_by_id(obj_id),
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(obj_id),
            )
            return object_data
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        server_data = super().update_by_id(
            obj_id, self.customer_schema.load(obj_in, unknown="include")
        )
        try:
            cached_object = self.redis_service.get(
                SINGLE_RECORD_CACHE_KEY.format(obj_id)
            )
            if cached_object:
                self.redis_service.delete(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            object_data = cache_object(
                obj_data=server_data,
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(server_data.id),
            )
            _ = cache_list_of_object(
                obj_data=super().index(),
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return object_data
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        server_data = super().delete(obj_id)
        try:
            cached_data = self.redis_service.get(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            if cached_data:
                self.redis_service.delete(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            _ = cache_list_of_object(
                obj_data=super().index(),
                obj_schema=self.customer_schema,
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return server_data
        except HTTPException:
            return super().delete(obj_id)
