from unittest import mock

import pytest

from app.core.exceptions import AppException
from app.services import ObjectStorage
from tests.utils.mock_response import MockSideEffects

SERVER_URL = "localhost:8000"


class TestCephStorage(MockSideEffects):
    _ceph_storage = ObjectStorage()

    @pytest.mark.service
    def test_create_object(self):
        result = self._ceph_storage.create_object("object")
        self.assertIsInstance(result, dict)
        self.assertIn("url", result)
        self.assertIn("fields", result)
        result = self._ceph_storage.create_object("null")
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    @pytest.mark.service
    def test_download_object(self):
        result = self._ceph_storage.download_object("object")
        self.assertIsInstance(result, str)
        result = self._ceph_storage.download_object("null")
        self.assertEqual(result, "null")

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.ObjectStorage.s3_client.list_objects")
    def test_get_object(self, mock_list_object):
        mock_list_object.side_effect = self.boto3_list_objects
        result = self._ceph_storage.get_object("obj_key")
        self.assertIsInstance(result, dict)
        self.assertIn("Key", result)

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.ObjectStorage.s3_client.list_objects")
    def test_list_objects(self, mock_list_object):
        mock_list_object.side_effect = self.boto3_list_objects
        result = self._ceph_storage.list_objects()
        self.assertIsInstance(result, list)
        self.assertNotEqual(result, [])

    @pytest.mark.service
    @mock.patch("app.services.ceph_storage.ObjectStorage.s3_client.delete_object")
    def test_delete_object(self, mock_delete_object):
        mock_delete_object.return_value = None
        result = self._ceph_storage.delete_object("obj_key")
        self.assertIsNone(result)
        result = self._ceph_storage.delete_object("null")
        self.assertIsNotNone(result)

    @pytest.mark.service
    def test_validate_object_key(self):
        result = self._ceph_storage.validate_object_key("obj_key")
        self.assertIsNotNone(result)
        self.assertEqual(result, "obj_key")
        result = self._ceph_storage.validate_object_key("null")
        self.assertIsNone(result)
        self.assertNotEqual(result, "obj_key")

    @pytest.mark.service
    @mock.patch(
        "app.services.ceph_storage.ObjectStorage.s3_client.generate_presigned_post"
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
