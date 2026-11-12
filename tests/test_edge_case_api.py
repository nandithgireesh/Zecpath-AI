"""
Integration Tests for Day 31 Edge Case & Failure Handling FastAPI Endpoints
============================================================================
"""

import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestEdgeCaseAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_analyze_audio_whisper(self):
        payload = {
            "snr_db": 22.0,
            "peak_amplitude_dbfs": -32.0,
            "packet_loss_rate": 0.0,
            "clipping_events": 0,
        }
        resp = self.client.post("/screening/edge-cases/analyze-audio", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["estimated_audio_degradation"], "LOW_AMPLITUDE_WHISPER")
        self.assertTrue(data["needs_acoustic_retry"])
        self.assertEqual(data["recommended_action"], "ACOUSTIC_REPEAT")
        self.assertIn("faint", data["retry_prompt"].lower())

    def test_02_analyze_audio_clean(self):
        payload = {
            "snr_db": 28.0,
            "peak_amplitude_dbfs": -12.0,
            "packet_loss_rate": 0.0,
            "clipping_events": 0,
        }
        resp = self.client.post("/screening/edge-cases/analyze-audio", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["estimated_audio_degradation"], "NORMAL")
        self.assertFalse(data["needs_acoustic_retry"])

    def test_03_normalize_language_hinglish(self):
        payload = {
            "text": "Current CTC bees lakh hai aur expected pachees LPA hai, but buyout possible hai."
        }
        resp = self.client.post("/screening/edge-cases/normalize-language", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn(data["detected_category"], ["HINGLISH_CODE_SWITCH", "BILINGUAL_TECHNICAL"])
        self.assertIn("hi", data["detected_languages"])
        self.assertEqual(data["extracted_entities"].get("salary_lpa"), 25.0)
        self.assertTrue(data["extracted_entities"].get("buyout_flexible"))

    def test_04_evaluate_turn_edge_case(self):
        payload = {
            "session_id": "test_sess_turn_001",
            "candidate_id": "cand_aditya",
            "turn_id": 1,
            "utterance": "Humne Celery aur Redis use kiya tha async processing ke liye kyunki latency kam thi.",
            "question_id": "q_bg_workers",
            "topic": "asynchronous background tasks",
            "next_topic": "database transactions",
            "snr_db": 26.0,
            "peak_amplitude_dbfs": -12.0,
        }
        resp = self.client.post("/screening/edge-cases/evaluate-turn", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_safe_to_advance"])
        self.assertEqual(data["safety_tier"], "NORMAL_FLOW")
        self.assertIn("celery", data["extracted_entities"].get("technologies", []))

    def test_05_run_benchmark_endpoint(self):
        resp = self.client.post("/screening/edge-cases/run-benchmark")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_scenarios"], 16)
        self.assertEqual(data["scenarios_evaluated"], 16)
        self.assertEqual(data["audio_recoveries_handled"], 4)
        self.assertEqual(data["code_switches_normalized"], 4)
        self.assertEqual(data["missing_answers_recovered"], 4)
        self.assertEqual(data["noise_adaptations_handled"], 4)
        self.assertGreaterEqual(data["overall_resilience_rate"], 0.90)

    def test_06_edge_case_schema_endpoint(self):
        resp = self.client.get("/screening/edge-cases/schema")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["$schema"], "http://json-schema.org/draft-07/schema#")
        self.assertIn("audio_telemetry", data["properties"])
        self.assertIn("code_switch_analysis", data["properties"])


if __name__ == "__main__":
    unittest.main()
