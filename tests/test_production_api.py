"""
Integration Tests for Day 32 Production Screening FastAPI Endpoints
====================================================================
"""

import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestProductionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_production_health(self):
        resp = self.client.get("/screening/production/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["uptime_status"], "OPERATIONAL")
        self.assertGreaterEqual(len(data["subsystems"]), 10)

    def test_02_production_manifest(self):
        resp = self.client.get("/screening/production/manifest")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["author"], "Nandith Gireesh")
        self.assertEqual(data["total_curriculum_days"], 12)
        self.assertEqual(len(data["modules_inventory"]), 12)
        self.assertEqual(data["metrics_summary"]["system_resilience_rate"], "100.0%")
        self.assertEqual(data["metrics_summary"]["false_rejection_rate"], "0.0%")

    def test_03_full_api_session_lifecycle(self):
        # 1. Start session
        start_payload = {
            "candidate_id": "cand_api_test_01",
            "candidate_name": "Arjun Sundaram",
            "job_role": "Senior Cloud Infrastructure Engineer",
            "target_experience_years": 4.0,
            "max_budget_lpa": 32.0,
            "max_notice_days": 60,
        }
        r_start = self.client.post("/screening/production/session/start", json=start_payload)
        self.assertEqual(r_start.status_code, 200)
        s_data = r_start.json()
        session_id = s_data["session_id"]
        self.assertTrue(session_id.startswith("sess_prod_"))
        self.assertEqual(s_data["current_state"], "GREETING")

        # 2. Process Turn 1: Greeting confirmation
        r_turn1 = self.client.post("/screening/production/session/turn", json={
            "session_id": session_id,
            "turn_index": 1,
            "candidate_speech": "Yes, I am available and ready for the technical screening.",
            "snr_db": 26.0,
        })
        self.assertEqual(r_turn1.status_code, 200)
        t1_data = r_turn1.json()
        self.assertEqual(t1_data["current_state"], "ELIGIBILITY_CHECK")
        self.assertIn("experience", t1_data["ai_spoken_prompt"].lower())

        # 3. Process Turn 2: Technical experience in Hinglish
        r_turn2 = self.client.post("/screening/production/session/turn", json={
            "session_id": session_id,
            "turn_index": 2,
            "candidate_speech": "Maine 5 saal Python aur Docker use kiya tha Kubernetes deployment ke liye.",
            "snr_db": 24.0,
        })
        self.assertEqual(r_turn2.status_code, 200)
        t2_data = r_turn2.json()
        self.assertEqual(t2_data["current_state"], "TECHNICAL_QUESTIONING")
        self.assertIn("python", t2_data["extracted_entities"].get("technologies", []))

        # 4. Finalize session
        r_fin = self.client.post("/screening/production/session/finalize", json={
            "session_id": session_id
        })
        self.assertEqual(r_fin.status_code, 200)
        fin_data = r_fin.json()
        self.assertEqual(fin_data["candidate_id"], "cand_api_test_01")
        self.assertTrue(fin_data["eligibility_verified"])
        self.assertIn(fin_data["decision"], ["HIRE", "STRONG_HIRE"])
        self.assertGreaterEqual(fin_data["final_score"], 65.0)
        self.assertEqual(fin_data["false_rejection_risk"], "0.0%")

    def test_04_turn_not_found(self):
        r_err = self.client.post("/screening/production/session/turn", json={
            "session_id": "sess_non_existent_999",
            "turn_index": 1,
            "candidate_speech": "Hello?"
        })
        self.assertEqual(r_err.status_code, 404)

    def test_05_finalize_not_found(self):
        r_err = self.client.post("/screening/production/session/finalize", json={
            "session_id": "sess_non_existent_999"
        })
        self.assertEqual(r_err.status_code, 404)


if __name__ == "__main__":
    unittest.main()
