import unittest
try:
    from fastapi.testclient import TestClient
    from repomedic.api import app
except ImportError:
    TestClient = None

@unittest.skipIf(TestClient is None, "Install optional API extra")
class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        self.assertEqual(self.client.get("/health").status_code, 200)

    def test_run_and_review_declined(self):
        response = self.client.post("/runs", json={})
        self.assertEqual(response.status_code, 200)
        record = response.json()
        self.assertEqual(record["decision"], "AWAITING_HUMAN_APPROVAL")
        declined = self.client.post(f"/runs/{record['run_id']}/review", json={"approved": False})
        self.assertEqual(declined.json()["decision"], "HUMAN_REJECTED")
