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
class CephObjectStorage(StorageServiceInterface):
    """
    This class is an intermediary between this service and the object storage service
    i.e ceph storage server.
    It makes api calls to the ceph server on behalf of the application.
    """

    boto3_config = boto_config(retries={"max_attempts": 3})
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=Config.CEPH_ACCESS_KEY,
        aws_secret_access_key=Config.CEPH_SECRET_KEY,
        endpoint_url=Config.CEPH_SERVER_URL,
        config=boto3_config,
    )

    def pre_signed_post(self, obj_id: str):
        assert obj_id, "missing id of object"

        response = self.object_storage_request(
            method="generate_presigned_post",
            kwarg={"Bucket": Config.CEPH_BUCKET, "Key": obj_id},
        )

        return response

    def pre_signed_get(self, obj_id: str):
        assert obj_id, "missing id of object"

        response = self.object_storage_request(
            method="generate_presigned_url",
            arg="get_object",
            kwarg={"Params": {"Bucket": Config.CEPH_BUCKET, "Key": obj_id}},
        )

        return response

    def save(self, obj_id: str, obj_path: str):
        assert obj_id, "missing id of object"
        assert obj_path, "missing path of object"

        response = self.object_storage_request(
            method="put_object",
            kwarg={
                "Body": open(obj_path, "rb"),
                "Bucket": Config.CEPH_BUCKET,
                "Key": obj_id,
            },
        )

        return response

    def download(self, obj_id: str):
        assert obj_id, "missing id of object"

        self.object_storage_request(
            method="download_file",
            kwarg={"Bucket": Config.CEPH_BUCKET, "Key": obj_id, "Filename": obj_id},
        )

        return None

    def view(self, obj_id: str):
        assert obj_id, "missing id of object"

        response = self.object_storage_request(
            method="list_objects", kwarg={"Bucket": Config.CEPH_BUCKET}
        )
        contents = response.get("Contents")
        for obj in contents:
            if obj_id == obj.get("Key"):
                return obj

        return None

    def list(self):

        response = self.object_storage_request(
            method="list_objects", kwarg={"Bucket": Config.CEPH_BUCKET}
        )
        contents = response.get("Contents")

        return contents if contents else None

    def delete(self, obj_id):
        assert obj_id, "missing id of object to delete"

        response = self.object_storage_request(
            method="delete_object",
            kwarg={"Bucket": Config.CEPH_BUCKET, "Key": obj_id},
        )

        return response

    def object_storage_request(self, method, kwarg: dict, arg=None):
        try:
            if arg:
                response = getattr(self.s3_client, method)(arg, **kwarg)
            else:
                response = getattr(self.s3_client, method)(**kwarg)
        except ClientError as exc:
            raise AppException.OperationError(
                error_message="ceph operation error",
                context=message_struct(
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
                error_message="error connecting to object storage server",
                context=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        return response
