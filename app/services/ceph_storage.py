import inspect
from dataclasses import dataclass

import boto3
from botocore.client import Config as boto_config
from botocore.exceptions import ClientError, ConnectionError

from app.core.exceptions import AppException
from app.core.service_interfaces import StorageServiceInterface
from app.utils import get_full_class_name, message_struct
from config import Config


@dataclass
class ObjectStorage(StorageServiceInterface):
    boto3_config = boto_config(retries={"max_attempts": 3})
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=Config.CEPH_ACCESS_KEY,
        aws_secret_access_key=Config.CEPH_SECRET_KEY,
        endpoint_url=Config.CEPH_SERVER_URL,
        config=boto3_config,
    )

    def save_object(self, obj_key):
        if self.validate_object_key(obj_key):
            response = self.object_storage_request(
                method="generate_presigned_post",
                kwarg={"Bucket": Config.CEPH_BUCKET, "Key": obj_key},
            )
            return response
        return None

    def download_object(self, obj_key):
        if self.validate_object_key(obj_key):
            response = self.object_storage_request(
                method="generate_presigned_url",
                arg="get_object",
                kwarg={
                    "Params": {
                        "Bucket": Config.CEPH_BUCKET,
                        "Key": obj_key,
                    }
                },
            )
            return response
        return None

    def create_object(self, object_path, obj_key):
        if self.validate_object_key(obj_key):
            response = self.object_storage_request(
                method="put_object",
                kwarg={
                    "Body": open(object_path, "rb"),
                    "Bucket": Config.CEPH_BUCKET,
                    "Key": obj_key,
                },
            )
            return response
        return None

    def get_object(self, obj_key):
        response = self.object_storage_request(
            method="list_objects", kwarg={"Bucket": Config.CEPH_BUCKET}
        )
        contents = response.get("Contents")
        for obj in contents:
            if obj_key == obj.get("Key"):
                return obj
        return {}

    def list_objects(self, directory_name=None):
        response = self.object_storage_request(
            method="list_objects", kwarg={"Bucket": Config.CEPH_BUCKET}
        )
        contents = response.get("Contents")
        if contents:
            if directory_name:
                obj_list = [obj for obj in contents if directory_name in obj.get("Key")]
                return obj_list
            else:
                return contents
        return []

    def delete_object(self, obj_key):
        if self.validate_object_key(obj_key):
            response = self.object_storage_request(
                method="delete_object",
                kwarg={"Bucket": Config.CEPH_BUCKET, "Key": obj_key},
            )
            return response
        return None

    # noinspection PyMethodMayBeStatic
    def validate_object_key(self, key):
        key = key.split("/")[-1]
        if key not in ["None", "null"]:
            return key
        return None

    def object_storage_request(self, method, kwarg: dict, arg=None):
        try:
            if arg:
                response = getattr(self.s3_client, method)(arg, **kwarg)
            else:
                response = getattr(self.s3_client, method)(**kwarg)
        except ClientError as exc:
            raise AppException.OperationError(
                context="error generating pre-signed url",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        except ConnectionError as exc:
            raise AppException.OperationError(
                context="error connecting to object storage server",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        return response
