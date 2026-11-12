"""
Integration Tests for Day 30 Optimization & Testing FastAPI Endpoints
====================================================================
"""

import unittest
from fastapi.testclient import TestClient

from api.main_day20 import app
from screening_ai.system_evaluator import ScreeningSystemEvaluator


class TestOptimizationAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.evaluator = ScreeningSystemEvaluator()

    def test_01_simulate_call_endpoint(self):
        payload = {
            "candidate_id": "cand_expert_fluent",
            "use_optimized_thresholds": True,
        }
        resp = self.client.post("/screening/optimization/simulate-call", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["candidate_id"], "cand_expert_fluent")
        self.assertEqual(data["archetype"], "EXPERT_FLUENT")
        self.assertIn(data["ai_recommendation"], ["STRONG_HIRE", "HIRE"])
        self.assertFalse(data["is_false_rejection"])


    def test_02_simulate_call_not_found(self):
        payload = {
            "candidate_id": "non_existent_candidate_xyz",
            "use_optimized_thresholds": True,
        }
        resp = self.client.post("/screening/optimization/simulate-call", json=payload)
        self.assertEqual(resp.status_code, 404)

    def test_03_evaluate_benchmark_endpoint(self):
        payload = {"use_optimized_thresholds": True}
        resp = self.client.post("/screening/optimization/evaluate-benchmark", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("report_id", data)
        self.assertEqual(data["benchmark_profiles_evaluated"], 12)
        self.assertGreater(data["false_rejection_reduction_pct"], 50.0)
        self.assertIn("baseline_metrics", data)
        self.assertIn("optimized_metrics", data)
        self.assertEqual(data["optimized_metrics"]["false_acceptance_rate"], 0.0)

    def test_04_tune_thresholds_endpoint(self):
        payload = {
            "overall_hire_cutoff": 69.0,
            "strong_hire_cutoff": 84.0,
            "technical_hire_cutoff": 67.0,
            "communication_hire_cutoff": 58.0,
            "enable_tech_compensation": True,
            "brevity_protection": True,
            "hesitation_penalty_dampener": True,
        }
        resp = self.client.post("/screening/optimization/tune-thresholds", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertGreaterEqual(data["resulting_f1_score"], 0.85)

    def test_05_get_metrics_endpoint(self):
        resp = self.client.get("/screening/optimization/metrics")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_profiles"], 12)
        self.assertGreaterEqual(data["f1_score"], 0.85)
        self.assertLessEqual(data["false_rejection_rate"], 0.10)
        self.assertEqual(data["false_acceptance_rate"], 0.0)

    def test_06_get_schema_endpoint(self):
        resp = self.client.get("/screening/optimization/schema")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["title"], "ScreeningSystemOptimizationSchema")
        self.assertIn("properties", data)

    def test_07_evaluator_intent_accuracy_lift(self):
        acc_report = self.evaluator.evaluate_intent_accuracy()
        self.assertIn("accuracy_lift_pct", acc_report)
        self.assertGreaterEqual(acc_report["optimized_accuracy"], acc_report["baseline_accuracy"])


if __name__ == "__main__":
    unittest.main()
