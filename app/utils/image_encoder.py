import base64
import os
from io import BytesIO

from PIL import Image

from app.core.exceptions import AppException

root_dir = os.path.join(os.path.dirname(__file__), "..")


def save_profile_image(obj_id, obj_data):
    image_directory_path = os.path.join(root_dir, "static/profile_images")
    encoded_image = obj_data.get("profile_image")
    if encoded_image:
        try:
            decode_image = base64.b64decode(encoded_image)
        except Exception:
            raise AppException.OperationError(context="error decoding image data")
        valid_image_info = validate_image_file(decode_image)
        image_name = f"{obj_id}.{valid_image_info.get('image_format')}"
        with open(f"{image_directory_path}/{image_name}", "wb") as profile_image:
            profile_image.write(valid_image_info.get("image_byte"))
        obj_data["profile_image"] = image_name
        return obj_data
    return obj_data


def validate_image_file(decoded_image_data):
    try:
        image = Image.open(BytesIO(decoded_image_data))
    except Exception:
        raise AppException.OperationError(context="invalid image file with error")
    buffer = BytesIO()
    image.save(buffer, format=image.format)
    return {
        "image_byte": buffer.getvalue(),
        "image_format": image.format.lower(),
    }


def send_profile_image(image_name):
    image_directory_path = os.path.join(root_dir, "static/profile_images")
    for file in os.listdir(image_directory_path):
        if image_name == file.split(".")[0]:
            with open(f"{image_directory_path}/{file}", "rb") as image:
                image_byte = image.read()
            try:
                encode_image_data = base64.b64encode(image_byte)
                return encode_image_data.decode("utf-8")
            except Exception as exc:
                raise AppException.OperationError(
                    context=f"error encoding image data with error {exc}"
                )
    return None
