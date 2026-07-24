import unittest
import json
from shadowc2.admin.app import app

class TestAdminTemplateEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_create_java(self):
        resp = self.client.post(
            "/api/payloads/template",
            data=json.dumps({"language":"java","name":"DemoDir"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "created")

    def test_duplicate(self):
        # First creation
        self.client.post(
            "/api/payloads/template",
            data=json.dumps({"language":"java","name":"DupDir"}),
            content_type="application/json",
        )
        # Second should fail
        resp = self.client.post(
            "/api/payloads/template",
            data=json.dumps({"language":"java","name":"DupDir"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_language(self):
        resp = self.client.post(
            "/api/payloads/template",
            data=json.dumps({"language":"c++","name":"BadLang"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

if __name__ == "__main__":
    unittest.main()
