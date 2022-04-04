import datetime
import os
import uuid

APP_ROOT = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), ".."
)


class CustomerTestData:
    @property
    def existing_customer(self):
        return {
            "phone_number": "0500000000",
            "email": "test@example.com",
            "pin": "1234",
            "birth_date": datetime.datetime.utcnow().date(),
            "full_name": "string",
            "id_expiry_date": datetime.datetime.utcnow().date(),
            "id_number": "existing",
            "id_type": "national_id",
        }

    @property
    def create_customer(self):
        return {
            "phone_number": "+233590000000",
            "email": "newtest@example.com",
            "pin": "1234",
            "birth_date": "2020-09-08",
            "full_name": "string",
            "id_expiry_date": "2020-09-08",
            "id_number": "create",
            "id_type": "national_id",
        }

    @property
    def register_customer(self):
        return {"phone_number": "0200000000"}

    @property
    def add_information(self):
        return {
            "birth_date": "2020-09-08",
            "full_name": "string",
            "id": uuid.uuid4(),
            "id_expiry_date": "2020-09-08",
            "id_number": "string",
            "id_type": "national_id",
        }

    @property
    def customer_credential(self):
        return {
            "phone_number": self.existing_customer.get("phone_number"),
            "pin": self.existing_customer.get("pin"),
        }

    @property
    def update_customer(self):
        return {
            "full_name": "customer update",
            "status": "active",
        }

    #
    # @property
    # def event_data(self):
    #     return {
    #         "service_name": "test_service",
    #         "details": "",
    #         "meta": {
    #             "event_action": "order_update",
    #         },
    #     }
    #
    # @property
    # def upload_profile_image(self):
    #     image = self.encode_profile_image("test_profile_image.jpeg")
    #     return {
    #         "profile_image": image,
    #     }
    #
    # @property
    # def upload_bad_encoded_image(self):
    #     return {
    #         "profile_image": "wrong encoded image data",
    #     }
    #
    # @property
    # def upload_invalid_image_file(self):
    #     image = self.encode_profile_image("test_invalid_image_file.txt")
    #     return {
    #         "profile_image": image,
    #     }
    #
    # @property
    # def upload_invalid_image_format(self):
    #     image = self.encode_profile_image("test_invalid_image_format.webp")
    #     return {
    #         "profile_image": image,
    #     }
    #
    # # noinspection PyMethodMayBeStatic
    # def encode_profile_image(self, image_name):
    #     image_path = f"{APP_ROOT}/tests/utils"
    #     with open(f"{image_path}/{image_name}", "rb") as test_image:
    #         image = test_image.read()
    #     encode_image = base64.b64encode(image)
    #     image_str = encode_image.decode("utf-8")
    #     return image_str
    #
    # # noinspection PyMethodMayBeStatic
    # def remove_uploaded_profile_image(self, image_name):
    #     image_path = f"{APP_ROOT}/app/static/image"
    #     os.remove(f"{image_path}/{image_name}.jpeg")


class KeycloakTestData:
    @property
    def create_user(self):
        return {
            "email": "me@example.com",
            "username": str(uuid.uuid4()),
            "firstname": "john",
            "lastname": "doe",
            "password": "p@$$w0rd",
            "group": "nova-customer-gp",
        }
