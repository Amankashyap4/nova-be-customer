import uuid
from datetime import datetime, timedelta
from time import sleep
from unittest import mock

import pytest

from app.core import Result
from app.core.exceptions import AppException
from app.models import CustomerModel, RegistrationModel
from tests.base_test_case import BaseTestCase


class TestCustomerController(BaseTestCase):
    @pytest.mark.controller
    def test_index(self):
        result = self.customer_controller.index()
        self.assertIsInstance(result, Result)
        self.assert200(result)
        self.assertIsInstance(result.value, list)
        self.assertIsInstance(result.value[0], CustomerModel)

    @pytest.mark.controller
    def test_register_customer(self):
        result = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.register_customer.copy()
        self.assertIsInstance(result, Result)
        self.assertIn("id", result.value)
        self.assertEqual(result.status_code, 201)
        data["phone_number"] = self.registration_repository.find_by_id(
            result.value.get("id")
        ).phone_number
        result = self.customer_controller.register(data)
        self.assertIsInstance(result, Result)
        self.assertIn("id", result.value)
        self.assertEqual(result.status_code, 201)
        with self.assertRaises(AppException.ResourceExists) as obj_exist:
            data["phone_number"] = self.customer_model.phone_number
            self.customer_controller.register(data)
        self.assertTrue(obj_exist.exception)
        self.assert400(obj_exist.exception)

    @pytest.mark.controller
    def test_confirm_token(self):
        self.customer_controller.register(self.customer_test_data.register_customer)
        result = RegistrationModel.query.filter_by(
            phone_number=self.customer_test_data.register_customer.get("phone_number")
        ).first()
        self.assertIsNotNone(result.otp_token)
        self.assertIsNotNone(result.otp_token_expiration)
        data = {"id": result.id, "token": result.otp_token}
        confirm_token = self.customer_controller.confirm_token(data)
        self.assertIsNotNone(confirm_token)
        self.assertIsInstance(confirm_token, Result)
        self.assert200(confirm_token)
        with self.assertRaises(AppException.ExpiredTokenException) as expired_otp:
            result.otp_token_expiration = datetime.now() + timedelta(seconds=1)
            sleep(1)
            self.customer_controller.confirm_token(data)
        self.assertTrue(expired_otp.exception)
        self.assert400(expired_otp.exception)
        with self.assertRaises(AppException.BadRequest) as invalid_otp:
            data["token"] = "00000"
            self.customer_controller.confirm_token(data)
        self.assertTrue(invalid_otp.exception)
        self.assert400(invalid_otp.exception)

    @pytest.mark.controller
    def test_add_information(self):
        self.customer_controller.register(self.customer_test_data.register_customer)
        customer = RegistrationModel.query.filter_by(
            phone_number=self.customer_test_data.register_customer.get("phone_number")
        ).first()
        confirm_token = self.customer_controller.confirm_token(
            {"id": customer.id, "token": customer.otp_token}
        )
        data = self.customer_test_data.add_information.copy()
        data["confirmation_token"] = confirm_token.value.get("confirmation_token")
        data["id"] = customer.id
        result = self.customer_controller.add_information(data)
        self.assert200(result)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, dict)
        self.assertIn("password_token", result.value)
        self.assertIn("id", result.value)
        with self.assertRaises(AppException.BadRequest) as bad_request:
            self.customer_controller.add_information(
                {"id": uuid.uuid4(), "phone_number": "0203340444"}
            )
        self.assertTrue(bad_request.exception)
        self.assert400(bad_request.exception)
        with self.assertRaises(AppException.BadRequest) as bad_request:
            self.customer_controller.add_information(
                self.customer_test_data.add_information
            )
        self.assertTrue(bad_request.exception)
        self.assert400(bad_request.exception)

    @pytest.mark.controller
    def test_resend_token(self):
        result = CustomerModel.query.filter_by(
            phone_number=self.customer_test_data.existing_customer.get("phone_number")
        ).first()
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
        self.assertIsNone(result.otp_token)
        self.assertIsNone(result.otp_token_expiration)
        resend_token = self.customer_controller.resend_token({"id": result.id})
        self.assertIsNotNone(result.otp_token)
        self.assertIsNotNone(result.otp_token_expiration)
        self.assertIsInstance(resend_token, Result)
        self.assert200(resend_token)
        with self.assertRaises(AppException.BadRequest) as bad_request:
            self.customer_controller.resend_token({"id": uuid.uuid4()})
        self.assertTrue(bad_request.exception)
        self.assert400(bad_request.exception)

    @pytest.mark.controller
    def test_login_customer(self):
        result = self.customer_controller.login(
            self.customer_test_data.customer_credential
        )
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, CustomerModel)
        self.assertTrue(hasattr(result.value, "refresh_token"))
        self.assertTrue(hasattr(result.value, "access_token"))
        self.assertEqual(result.status_code, 200)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            credentials = {"phone_number": "2345678921", "pin": "1234"}
            self.customer_controller.login(credentials)
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.update(
                self.customer_model.id, {"status": "disabled"}
            )
            self.customer_controller.login(self.customer_test_data.customer_credential)
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_update_customer(self):
        result = self.customer_controller.update(
            self.customer_model.id, self.customer_test_data.update_customer
        )
        self.assert200(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, CustomerModel)
        self.assertEqual(
            result.value.email,
            self.customer_test_data.update_customer.get("email"),
        )
        with self.assertRaises(AppException.NotFoundException) as not_found:
            self.customer_controller.update(
                obj_id=uuid.uuid4(),
                obj_data=self.customer_test_data.update_customer,
            )
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)
        with mock.patch(
            "app.utils.object_storage.s3_client.generate_presigned_url"
        ) as boto3_exception:
            boto3_exception.side_effect = self.botocore_client_error
            with self.assertRaises(AppException.OperationError) as operation_error:
                self.customer_controller.update(
                    self.customer_model.id, self.customer_test_data.update_customer
                )
        self.assertTrue(operation_error.exception)
        self.assert400(operation_error.exception)
        with mock.patch(
            "app.utils.object_storage.s3_client.generate_presigned_post"
        ) as boto3_exception:
            boto3_exception.side_effect = self.botocore_client_error
            with self.assertRaises(AppException.OperationError) as operation_error:
                self.customer_controller.update(
                    self.customer_model.id, self.customer_test_data.update_customer
                )
        self.assertTrue(operation_error.exception)
        self.assert400(operation_error.exception)

    @pytest.mark.controller
    def test_add_pin(self):
        result = self.customer_controller.update(
            self.customer_model.id, {"auth_token": "auth_token"}
        )
        self.assertIsNotNone(result.value.auth_token)
        add_pin = self.customer_controller.add_pin(
            {"password_token": "auth_token", "pin": "1234"}
        )
        self.assert200(add_pin)
        self.assertIsInstance(add_pin, Result)
        self.assertIsInstance(add_pin.value, dict)
        self.assertIn("access_token", add_pin.value)
        self.assertIn("refresh_token", add_pin.value)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            self.customer_controller.add_pin(
                {"password_token": "not_found", "pin": "1234"}
            )
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_forgot_password(self):
        result = CustomerModel.query.filter_by(
            phone_number=self.customer_model.phone_number
        ).first()
        self.assertIsNotNone(result)
        self.assertIsNone(result.otp_token)
        self.assertIsNone(result.otp_token_expiration)
        forgot_password = self.customer_controller.forgot_password(
            self.customer_test_data.existing_customer
        )
        self.assertIsNotNone(result.otp_token)
        self.assertIsNotNone(result.otp_token_expiration)
        self.assertIsInstance(forgot_password, Result)
        self.assertEqual(forgot_password.status_code, 200)
        self.assertIsInstance(forgot_password.value, dict)
        self.assertEqual(len(forgot_password.value), 1)
        self.assertEqual(forgot_password.value.get("id"), result.id)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.forgot_password(
                self.customer_test_data.register_customer
            )
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_reset_password(self):
        result = CustomerModel.query.filter_by(
            phone_number=self.customer_model.phone_number
        ).first()
        result.auth_token = "auth_token"
        self.assertIsNotNone(result.pin)
        self.assertTrue(result.verify_pin("1234"))
        reset_password = self.customer_controller.reset_password(
            {"id": result.id, "new_pin": "0000", "token": "auth_token"}
        )
        self.assertIsInstance(reset_password, Result)
        self.assertEqual(reset_password.status_code, 200)
        self.assertFalse(result.verify_pin("1234"))
        self.assertTrue(result.verify_pin("0000"))
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.reset_password({"id": uuid.uuid4()})
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)
        with self.assertRaises(AppException.ExpiredTokenException) as expired_token:
            self.customer_controller.reset_password(
                {"id": result.id, "new_pin": "0000", "token": "no_auth"}
            )
        self.assertTrue(expired_token.exception)
        self.assert400(expired_token.exception)
        with self.assertRaises(AppException.ValidationException) as not_found_exc:
            result.auth_token = "new_auth"
            self.customer_controller.reset_password(
                {"id": result.id, "new_pin": "0000", "token": "old_auth"}
            )
        self.assertTrue(not_found_exc.exception)
        self.assert400(not_found_exc.exception)

    @pytest.mark.controller
    def test_change_password(self):
        result = CustomerModel.query.filter_by(
            phone_number=self.customer_model.phone_number
        ).first()
        self.assertIsNotNone(result.pin)
        self.assertTrue(result.verify_pin("1234"))
        data = {"customer_id": result.id, "old_pin": "1234", "new_pin": "0000"}
        change_password = self.customer_controller.change_password(data)
        self.assertIsInstance(change_password, Result)
        self.assertEqual(change_password.status_code, 200)
        self.assertFalse(result.verify_pin("1234"))
        self.assertTrue(result.verify_pin("0000"))
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.change_password(
                {"customer_id": uuid.uuid4(), "old_pin": "1234", "new_pin": "0000"}
            )
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_pin_process(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "666666"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        pin_process = self.customer_controller.pin_process(
            self.customer_test_data.register_customer
        )
        self.assert200(pin_process)
        self.assertIn("id", pin_process.value)
        result = CustomerModel.query.get(pin_process.value.get("id"))
        self.assertIsNone(result.pin)
        self.assertIsNotNone(result.otp_token)
        self.assertIsNotNone(result.otp_token_expiration)
        with self.assertRaises(AppException.BadRequest) as bad_request:
            self.customer_controller.pin_process(
                self.customer_test_data.existing_customer
            )
        self.assertTrue(bad_request.exception)
        self.assert400(bad_request.exception)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.pin_process({"phone_number": "0245060606"})
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_request_pin(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "666666"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        request_pin = self.customer_controller.pin_process(
            self.customer_test_data.register_customer
        )
        self.assert200(request_pin)
        self.assertIn("id", request_pin.value)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.pin_process({"phone_number": "0245555555"})
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_reset_phone_request(self):
        reset_phone = self.customer_controller.reset_phone_request(
            self.customer_test_data.existing_customer
        )
        self.assert200(reset_phone)
        self.assertIn("id", reset_phone.value)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            self.customer_controller.reset_phone_request({"phone_number": "0245555555"})
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_reset_phone(self):
        data = {
            "customer_id": "id",
            "new_phone_number": "0244444444",
            "token": "auth_token",
        }
        request_reset_phone = self.customer_controller.reset_phone_request(
            self.customer_test_data.existing_customer
        )
        self.assert200(request_reset_phone)
        self.assertIn("id", request_reset_phone.value)
        self.customer_controller.update(
            request_reset_phone.value.get("id"), {"auth_token": "auth_token"}
        )
        data["customer_id"] = request_reset_phone.value.get("id")
        reset_phone = self.customer_controller.reset_phone(data)
        self.assert200(reset_phone)
        self.assertIn("id", reset_phone.value)
        self.assertIn("phone_number", reset_phone.value)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            data["customer_id"] = uuid.uuid4()
            self.customer_controller.reset_phone(data)
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)
        with self.assertRaises(AppException.BadRequest) as bad_request:
            data["customer_id"] = request_reset_phone.value.get("id")
            data["token"] = "no_auth"
            self.customer_controller.reset_phone(data)
        self.assertTrue(bad_request.exception)
        self.assert400(bad_request.exception)
        with self.assertRaises(AppException.ResourceExists) as resource_exist:
            data["new_phone_number"] = self.customer_test_data.existing_customer.get(
                "phone_number"
            )
            self.customer_controller.reset_phone(data)
        self.assertTrue(resource_exist.exception)
        self.assert400(resource_exist.exception)

    @pytest.mark.controller
    def test_request_phone_reset(self):
        data = {"customer_id": "id", "phone_number": "0244444444", "token": "666666"}
        reset_phone_request = self.customer_controller.reset_phone_request(
            self.customer_test_data.existing_customer
        )
        data["customer_id"] = reset_phone_request.value.get("id")
        reset_phone = self.customer_controller.request_phone_reset(data)
        self.assert200(reset_phone)
        self.assertIn("detail", reset_phone.value)
        with self.assertRaises(AppException.BadRequest) as expired_token:
            data["token"] = "1234"
            self.customer_controller.request_phone_reset(data)
        self.assertTrue(expired_token.exception)
        self.assert400(expired_token.exception)
        with self.assertRaises(AppException.NotFoundException) as not_found_exc:
            data["customer_id"] = uuid.uuid4()
            self.customer_controller.request_phone_reset(data)
        self.assertTrue(not_found_exc.exception)
        self.assert404(not_found_exc.exception)

    @pytest.mark.controller
    def test_get_customer(self):
        result = self.customer_controller.get_customer(self.customer_model.id)
        self.assert200(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, CustomerModel)
        self.assertEqual(result.value, self.customer_model)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            self.customer_controller.get_customer(obj_id=uuid.uuid4())
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_password_otp_confirmation(self):
        register = self.customer_controller.register(
            self.customer_test_data.register_customer
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        token = self.customer_controller.confirm_token(
            {"id": register.value.get("id"), "token": "666666"}
        )
        data = self.customer_test_data.add_information.copy()
        data["id"] = register.value.get("id")
        data["confirmation_token"] = token.value.get("confirmation_token")
        self.customer_controller.add_information(data)
        self.customer_controller.forgot_password(
            self.customer_test_data.register_customer
        )
        result = CustomerModel.query.filter_by(
            phone_number=self.customer_test_data.register_customer.get("phone_number")
        ).first()
        self.assertIsNotNone(result.otp_token)
        self.assertIsNotNone(result.otp_token_expiration)
        data = {"id": result.id, "token": result.otp_token}
        confirm_otp = self.customer_controller.password_otp_confirmation(data)
        self.assert200(confirm_otp)
        self.assertIsNotNone(confirm_otp)
        self.assertIsInstance(confirm_otp, Result)
        self.assertIn("token", confirm_otp.value)
        with self.assertRaises(AppException.ExpiredTokenException) as expired_otp:
            result.otp_token_expiration = datetime.now() + timedelta(seconds=1)
            result.otp_token = "666666"
            sleep(1)
            self.customer_controller.password_otp_confirmation(data)
        self.assertTrue(expired_otp.exception)
        self.assert400(expired_otp.exception)
        with self.assertRaises(AppException.BadRequest) as invalid_otp:
            data["id"] = uuid.uuid4()
            self.customer_controller.password_otp_confirmation(data)
        self.assertTrue(invalid_otp.exception)
        self.assert400(invalid_otp.exception)

    @pytest.mark.controller
    def test_reset_pin_process(self):
        data = {"id": self.customer_model.id, "token": "666666"}
        self.customer_model.otp_token = "666666"
        reset_pin = self.customer_controller.reset_pin_process(data)
        self.assert200(reset_pin)
        self.assertIn("id", reset_pin.value)
        self.assertIn("password_token", reset_pin.value)
        with self.assertRaises(AppException.Unauthorized) as unauthorize_exc:
            self.customer_model.otp_token = None
            self.customer_controller.reset_pin_process(data)
        self.assertTrue(unauthorize_exc.exception)
        self.assert401(unauthorize_exc.exception)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            data["id"] = uuid.uuid4()
            self.customer_controller.reset_pin_process(data)
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_process_reset_pin(self):
        data = {
            "customer_id": self.customer_model.id,
            "password_token": "auth_token",
            "pin": "0000",
        }
        self.customer_model.auth_token = "auth_token"
        reset_pin = self.customer_controller.process_reset_pin(data)
        self.assert200(reset_pin)
        self.assertIsInstance(reset_pin.value, CustomerModel)
        with self.assertRaises(AppException.Unauthorized) as unauthorize_exc:
            self.customer_model.auth_token = None
            self.customer_controller.process_reset_pin(data)
        self.assertTrue(unauthorize_exc.exception)
        self.assert401(unauthorize_exc.exception)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            data["customer_id"] = uuid.uuid4()
            self.customer_controller.process_reset_pin(data)
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_delete_customer(self):
        result = self.customer_controller.delete(self.customer_model.id)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 204)
        self.assertEqual(result.value, {})
        with self.assertRaises(AppException.NotFoundException) as not_found:
            self.customer_controller.delete(obj_id=uuid.uuid4())
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_find_by_phone_number(self):
        result = self.customer_controller.find_by_phone_number(
            self.customer_model.phone_number
        )
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 200)
        self.assertIsInstance(result.value, CustomerModel)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            self.customer_controller.find_by_phone_number("0234566555")
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    @pytest.mark.controller
    def test_refresh_token(self):
        data = {"id": self.customer_model.id, "refresh_token": self.refresh_token}
        result = self.customer_controller.refresh_token(data)
        self.assertIsInstance(result.value, dict)
        self.assertIn("access_token", result.value)
        self.assertIn("refresh_token", result.value)
        with self.assertRaises(AppException.NotFoundException) as not_found:
            data["id"] = uuid.uuid4()
            self.customer_controller.refresh_token(data)
        self.assertTrue(not_found.exception)
        self.assert404(not_found.exception)

    def test_customer_profile_images(self):
        with mock.patch("app.utils.object_storage.s3_client.list_objects") as boto3_list:
            boto3_list.side_effect = self.botocore_client_list
            result = self.customer_controller.customer_profile_images()
            self.assertIsInstance(result, Result)
            self.assertEqual(result.status_code, 200)
            self.assertIsInstance(result.value, list)

    def test_customer_profile_image(self):
        with mock.patch("app.utils.object_storage.s3_client.list_objects") as boto3_list:
            boto3_list.side_effect = self.botocore_client_list
            self.customer_model.profile_image = str(self.customer_model.id)
            result = self.customer_controller.customer_profile_image(
                self.customer_model.id
            )
            self.assertIsInstance(result, Result)
            self.assertEqual(result.status_code, 200)
            self.assertIsInstance(result.value, dict)
