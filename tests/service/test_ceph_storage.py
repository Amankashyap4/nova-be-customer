from unittest import mock

import pytest

from app.core.exceptions import AppException
from app.services import CephObjectStorage
from tests.utils.mock_response import MockSideEffects

SERVER_URL = "localhost:8000"


class TestCephStorage(MockSideEffects):
    _ceph_storage = CephObjectStorage()

    @pytest.mark.service
    def test_pre_signed_post(self):
        result = self._ceph_storage.pre_signed_post("object")
        self.assertIsInstance(result, dict)
        self.assertIn("url", result)
        self.assertIn("fields", result)

    @pytest.mark.service
    def test_pre_signed_get(self):
        result = self._ceph_storage.pre_signed_get("object")
        self.assertIsInstance(result, str)

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.CephObjectStorage.s3_client.list_objects")
    def test_view(self, mock_list_object):
        mock_list_object.side_effect = self.boto3_list_objects
        result = self._ceph_storage.view("customer/obj_key")
        self.assertIsInstance(result, dict)
        self.assertIn("Key", result)

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.CephObjectStorage.s3_client.list_objects")
    def test_list(self, mock_list_object):
        mock_list_object.side_effect = self.boto3_list_objects
        result = self._ceph_storage.list()
        self.assertIsInstance(result, list)
        self.assertNotEqual(result, [])

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.CephObjectStorage.s3_client.delete_object")
    def test_delete(self, mock_delete_object):
        mock_delete_object.return_value = None
        result = self._ceph_storage.delete("customer/obj_key")
        self.assertIsNone(result)
        result = self._ceph_storage.delete("customer/null")
        self.assertIsNone(result)

    @pytest.mark.service
    @mock.patch(
        "app.services.ceph_storage.CephObjectStorage.s3_client.generate_presigned_post"
    )
    def test_object_storage_request(self, object_request):
        object_request.side_effect = self.boto3_request
        result = self._ceph_storage.object_storage_request(
            method="generate_presigned_post",
            kwarg={"Bucket": "bucket-name", "Key": "obj_key"},
        )
        self.assertIsInstance(result, dict)
        self.assertNotEqual(result, {})
        self.assertIn("status", result)
        with self.assertRaises(AppException.OperationError) as operation_error:
            object_request.side_effect = self.boto3_client_error
            self._ceph_storage.object_storage_request(
                method="generate_presigned_post",
                kwarg={"Bucket": "bucket-name", "Key": "obj_key"},
            )
        self.assertTrue(operation_error.exception)
        self.assert400(operation_error.exception)
        with self.assertRaises(AppException.OperationError) as operation_error:
            object_request.side_effect = self.boto3_connection_error
            self._ceph_storage.object_storage_request(
                method="generate_presigned_post",
                kwarg={"Bucket": "bucket-name", "Key": "obj_key"},
            )
        self.assertTrue(operation_error.exception)
        self.assert400(operation_error.exception)
