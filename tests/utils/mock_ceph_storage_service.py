from dataclasses import dataclass

from app.services import CephObjectStorage


@dataclass
class MockCephObjectStorage(CephObjectStorage):
    def pre_signed_post(self, obj_id: str):
        pre_signed_post = {
            "url": "https://server.url:port/bucket-name",
            "fields": {
                "key": "customer/46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.png",
                "AWSAccessKeyId": "S63I9MN2UB43276SLAEY",
                "policy": "eyJleHBpcmF0aW9uIjogIjIwMjItMDUtMjdUMTE6NDg6MzBaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibm92YS1idWNrZXQifSwgeyJrZXkiOiAiNDZmZTM4ZDgtNzBlZi00NGVhLTljOTEtZjc3YTY3YmMxYzZkLnBuZyJ9XX0=",  # noqa
                "signature": "ZmKKSjVFohbQPvze4GaicLOichE=",
            },
        }
        return pre_signed_post

    def pre_signed_get(self, obj_id: str):
        pre_signed_get = "https://server.url:port/bucket-name/46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.png?AWSAccessKeyId=S63I9MN2UB43276SLAEY&Signature=paF1YlruiylCOadaZvXp2%2BYI5z4%3D&Expires=1653652111"  # noqa
        return pre_signed_get

    def view(self, obj_id: str):
        obj = {
            "ETag": "7e76d20a375c0259e21e985a5478bbac",
            "Key": "customer/46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.jpeg",
            "LastModified": "Fri, 27 May 2022 10:25:27 GMT",
            "Owner": {"DisplayName": "novauser", "ID": "nova"},
            "Size": 294991,
            "StorageClass": "STANDARD",
        }
        return obj

    def list(self):
        obj_list = [
            {
                "ETag": "7e76d20a375c0259e21e985a5478bbac",
                "Key": "customer/46fe38d8-70ef-44ea-9c91-f77a67bc1c6d.jpeg",
                "LastModified": "Fri, 27 May 2022 10:25:27 GMT",
                "Owner": {"DisplayName": "novauser", "ID": "nova"},
                "Size": 294991,
                "StorageClass": "STANDARD",
            }
        ]
        return obj_list
