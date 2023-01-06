import unittest
import requests

SAFETY_OBJECT={
    "tittle": "tittle testing",
    "description" :"description TESTING",
    "image": "image testing"
}

class TestSafety(unittest.TestCase):
    API_URL = "http://localhost:5000/api/v1/customers"
    PROMOTION_URL = "{}/promotion".format(API_URL)

    SAFETY_OBJECT = {
        "tittle": "tittle testing",
        "description": "description TESTING",
        "image": "image testing"
    }

    def test_1_get_all_promotion(self):
        r = requests.get(TestSafety.PROMOTION_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()),9)

    def test_add_new_promotion(self):
        r = requests.post(TestSafety.PROMOTION_URL,json=TestSafety.SAFETY_OBJECT)
        self.assertEqual(r.status_code, 200)

    def test_update_promotion(self):
        NEW_SAFETY_OBJECT = {
            "tittle": "updated tittle testing",
            "description": "updated description TESTING",
            "image": "updated image testing"
        }
        id = "171ba65b-2f1d-44d4-9f3d-627783f4495b "
        r = requests.put("{}/{}".format(TestSafety.PROMOTION_URL,id), json=NEW_SAFETY_OBJECT)
        self.assertEqual(r.status_code, 405)

    def test_delete_promotion(self):
        id = "171ba65b-2f1d-44d4-9f3d-627783f4495b "
        r = requests.delete("{}/{}".format(TestSafety.PROMOTION_URL, id))
        self.assertEqual(r.status_code, 400)




