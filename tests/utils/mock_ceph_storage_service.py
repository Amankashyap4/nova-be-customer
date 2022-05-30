from dataclasses import dataclass

from app.services import ObjectStorage


@dataclass
class MockStorageService(ObjectStorage):
    def create_object(self, obj_name):
        pre_signed_post = {
            "url": "http://server.url:port/bucket-name",
            "fields": {
                "key": "46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.png",
                "AWSAccessKeyId": "S63I9MN2UB43276SLAEY",
                "policy": "eyJleHBpcmF0aW9uIjogIjIwMjItMDUtMjdUMTE6NDg6MzBaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibm92YS1idWNrZXQifSwgeyJrZXkiOiAiNDZmZTM4ZDgtNzBlZi00NGVhLTljOTEtZjc3YTY3YmMxYzZkLnBuZyJ9XX0=",  # noqa
                "signature": "ZmKKSjVFohbQPvze4GaicLOichE=",
            },
        }
        return pre_signed_post

    def download_object(self, obj_name):
        pre_signed_get = "http://server.url:port/bucket-name/46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.png?AWSAccessKeyId=S63I9MN2UB43276SLAEY&Signature=paF1YlruiylCOadaZvXp2%2BYI5z4%3D&Expires=1653652111"  # noqa
        return pre_signed_get

    def get_object(self, obj_name):
        obj = {
            "ETag": "7e76d20a375c0259e21e985a5478bbac",
            "Key": "46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.jpeg",
            "LastModified": "Fri, 27 May 2022 10:25:27 GMT",
            "Owner": {"DisplayName": "novauser", "ID": "nova"},
            "Size": 294991,
            "StorageClass": "STANDARD",
        }
        return obj

    def list_objects(self):
        obj_list = [
            {
                "ETag": "7e76d20a375c0259e21e985a5478bbac",
                "Key": "46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.jpeg",
                "LastModified": "Fri, 27 May 2022 10:25:27 GMT",
                "Owner": {"DisplayName": "novauser", "ID": "nova"},
                "Size": 294991,
                "StorageClass": "STANDARD",
            }
        ]
        return obj_list

    def delete_object(self, obj_name):
        return None
