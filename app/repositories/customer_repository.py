import json

from app.core.exceptions import HTTPException
from app.core.repository import SQLBaseRepository
from app.models import CustomerModel
from app.schema import CustomerSchema
from app.services import RedisService

OBJECT_SCHEMA = CustomerSchema(unknown="include")
OBJECT = "customer"


class CustomerRepository(SQLBaseRepository):
    model = CustomerModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def index(self):
        try:
            all_cache_data = self.redis_service.get(f"all_{OBJECT}s")
            if all_cache_data:
                serialize_cache = OBJECT_SCHEMA.loads(
                    json.dumps(all_cache_data), many=True
                )
                for count, value in enumerate(serialize_cache):
                    serialize_cache[count] = self.model(**value)
                return serialize_cache
            return super().index()
        except HTTPException:
            return super().index()

    def create(self, data):
        server_data = super().create(OBJECT_SCHEMA.load(data))
        try:
            cache_data = OBJECT_SCHEMA.dumps(server_data)
            self.redis_service.set(f"{OBJECT}_{server_data.id}", cache_data)
            all_cache_data = OBJECT_SCHEMA.dumps(super().index(), many=True)
            self.redis_service.set(f"all_{OBJECT}s", all_cache_data)
            return server_data
        except HTTPException:
            return server_data

    def get_by_id(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"{OBJECT}_{obj_id}")
            if cache_data:
                serialize_cache = OBJECT_SCHEMA.loads(json.dumps(cache_data))
                return self.model(**serialize_cache)
            server_result = super().find_by_id(obj_id)
            self.redis_service.set(
                f"{OBJECT}_{obj_id}", OBJECT_SCHEMA.dumps(server_result)
            )
            return server_result
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        try:
            cache_data = self.redis_service.get(f"{OBJECT}_{obj_id}")
            if cache_data:
                self.redis_service.delete(f"{OBJECT}_{obj_id}")
            server_result = super().update_by_id(obj_id, OBJECT_SCHEMA.load(obj_in))
            self.redis_service.set(
                f"{OBJECT}_{obj_id}", OBJECT_SCHEMA.dumps(server_result)
            )
            self.redis_service.set(
                f"all_{OBJECT}s", OBJECT_SCHEMA.dumps(super().index(), many=True)
            )
            return server_result
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"{OBJECT}_{obj_id}")
            if cache_data:
                self.redis_service.delete(f"{OBJECT}_{obj_id}")
            server_result = super().delete(obj_id)
            self.redis_service.set(
                f"all_{OBJECT}s", OBJECT_SCHEMA.dumps(super().index(), many=True)
            )
            return server_result
        except HTTPException:
            return super().delete(obj_id)
