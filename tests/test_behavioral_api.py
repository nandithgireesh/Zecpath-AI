"""
Day 27: Integration Tests for Behavioral REST API Endpoints
===========================================================
Tests:
1. POST /screening/behavioral/analyze-turn
2. POST /screening/behavioral/analyze-session
3. GET /screening/behavioral/benchmarks
"""

import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestBehavioralAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_analyze_turn_endpoint(self):
        """Test POST /screening/behavioral/analyze-turn with articulate response."""
        payload = {
            "turn_id": "TURN_TEST_01",
            "raw_text": "I have 5 years of experience leading Python backend microservices with FastAPI and Docker.",
            "duration_seconds": 5.5,
            "latency_ms": 1100,
        }
        response = self.client.post("/screening/behavioral/analyze-turn", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["turn_id"], "TURN_TEST_01")
        self.assertGreaterEqual(data["confidence_score"], 85.0)
        self.assertEqual(data["confidence_tier"], "HIGH")
        self.assertEqual(data["pace_rating"], "OPTIMAL")
        self.assertIn(data["sentiment_polarity"], ["NEUTRAL", "POSITIVE", "VERY_POSITIVE"])
        self.assertIn("fluency_score", data["communication_indicators"])

    def test_analyze_turn_hedging_endpoint(self):
        """Test POST /screening/behavioral/analyze-turn with uncertain response."""
        payload = {
            "turn_id": "TURN_TEST_02",
            "raw_text": "Um, uh, well, I think maybe we used AWS, but I'm not really sure.",
            "duration_seconds": 4.5,
            "latency_ms": 3200,
        }
        response = self.client.post("/screening/behavioral/analyze-turn", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["hesitation_penalties"], 0.0)
        self.assertGreater(data["uncertainty_score"], 40.0)
        self.assertTrue(len(data["hedging_phrases"]) >= 2)

    def test_analyze_session_endpoint(self):
        """Test POST /screening/behavioral/analyze-session with multi-turn conversation."""
        payload = {
            "candidate_id": "CAND_API_27",
            "session_id": "SESS_API_27",
            "turns": [
                {
                    "turn_id": "T1",
                    "raw_text": "I am thrilled to join the team, I have 4 years of Python and PostgreSQL experience.",
                    "duration_seconds": 4.0,
                },
                {
                    "turn_id": "T2",
                    "raw_text": "I can join in 30 days and my expected salary is 20 LPA.",
                    "duration_seconds": 3.0,
                },
            ],
        }
        response = self.client.post("/screening/behavioral/analyze-session", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["candidate_id"], "CAND_API_27")
        self.assertEqual(data["total_turns_analyzed"], 2)
        self.assertGreaterEqual(data["overall_confidence_score"], 80.0)
        self.assertIn("recruiter_executive_summary", data)
        self.assertEqual(len(data["turn_breakdowns"]), 2)

    def test_get_benchmarks_endpoint(self):
        """Test GET /screening/behavioral/benchmarks returns configuration dictionaries."""
        response = self.client.get("/screening/behavioral/benchmarks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("pace_benchmarks", data)
        self.assertIn("OPTIMAL", data["pace_benchmarks"])
        self.assertIn("confidence_tiers", data)
        self.assertIn("HIGH", data["confidence_tiers"])
        self.assertIn("sentiment_categories", data)
        self.assertIn("VERY_POSITIVE", data["sentiment_categories"])
        self.assertIn("communication_indicators", data)
        self.assertIn("Fluency", data["communication_indicators"])


if __name__ == "__main__":
    unittest.main()
