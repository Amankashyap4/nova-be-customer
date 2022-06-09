import json

from app.core.exceptions import AppException, HTTPException
from app.core.repository import SQLBaseRepository
from app.models import CustomerModel
from app.schema import CustomerSchema
from app.services import RedisService


class CustomerRepository(SQLBaseRepository):
    model = CustomerModel

    def __init__(self, redis_service: RedisService, customer_schema: CustomerSchema):
        self.redis_service = redis_service
        self.customer_schema = customer_schema
        super().__init__()

    def index(self):
        try:
            all_cache_data = self.redis_service.get("all_customers")
            if all_cache_data:
                deserialized_objects = self.deserialize_list_of_object(all_cache_data)
                return deserialized_objects
            server_data = super().index()
            self.serialize_list_of_object(server_data)
            return server_data
        except HTTPException:
            return super().index()

    def create(self, data):
        server_data = super().create(self.customer_schema.load(data, unknown="include"))
        try:
            obj_data = self.serialize_object(server_data.id, server_data)
            self.serialize_list_of_object(super().index())
            return obj_data
        except HTTPException:
            return server_data

    def get_by_id(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"customer_{obj_id}")
            if cache_data:
                deserialized_object = self.deserialize_object(cache_data)
                return deserialized_object
            object_data = self.serialize_object(obj_id, super().find_by_id(obj_id))
            return object_data
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        server_data = super().update_by_id(
            obj_id, self.customer_schema.load(obj_in, unknown="include")
        )
        try:
            cache_data = self.redis_service.get(f"customer_{obj_id}")
            if cache_data:
                self.redis_service.delete(f"customer_{obj_id}")
            object_data = self.serialize_object(obj_id, server_data)
            self.serialize_list_of_object(super().index())
            return object_data
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        server_data = super().delete(obj_id)
        try:
            cache_data = self.redis_service.get(f"customer_{obj_id}")
            if cache_data:
                self.redis_service.delete(f"customer_{obj_id}")
            self.serialize_list_of_object(super().index())
            return server_data
        except HTTPException:
            return super().delete(obj_id)

    def cache_record(self, key):
        try:
            cache_data = self.redis_service.get(key)
        except HTTPException:
            raise AppException.NotFoundException(
                context="error connecting to redis server",
            )
        else:
            if not cache_data:
                raise AppException.NotFoundException(
                    context=f"record with key {key} not available in cache"
                )
            return cache_data

    def serialize_object(self, obj_id, obj_data: dict):
        serialize_data = self.customer_schema.dumps(obj_data)
        self.redis_service.set(f"customer_{obj_id}", serialize_data)
        return obj_data

    def serialize_list_of_object(self, obj_list):
        serialize_all_data = self.customer_schema.dumps(obj_list, many=True)
        self.redis_service.set("all_customers", serialize_all_data)

    def deserialize_object(self, obj_data: str):
        deserialize_data = self.customer_schema.loads(json.dumps(obj_data))
        return self.model(**deserialize_data)

    def deserialize_list_of_object(self, object_data: str):
        deserialize_object_data = self.customer_schema.loads(
            json.dumps(object_data), many=True
        )
        for count, value in enumerate(deserialize_object_data):
            deserialize_object_data[count] = self.model(**value)
        return deserialize_object_data
