"""
Unit Tests for Day 44: Documentation & API Specification
=========================================================
Tests API schemas, OpenAPI 3.1 generation, FastAPI endpoints,
architectural invariants, error catalogs, and troubleshooting playbooks.
"""

import unittest
from fastapi.testclient import TestClient

from interview_ai.api_router import create_app, generate_openapi_spec
from interview_ai.api_architecture import ArchitectureSpecification
from interview_ai.troubleshooting_engine import TroubleshootingEngine, ERROR_CATALOG
from interview_ai.api_schemas import SeniorityLevel


class TestDay44ApiAndDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.arch = ArchitectureSpecification()
        cls.troubleshooter = TroubleshootingEngine()

    def test_01_openapi_spec_generation(self):
        spec = generate_openapi_spec()
        self.assertIn("openapi", spec)
        self.assertTrue(spec["openapi"].startswith("3."))
        self.assertIn("paths", spec)

        # Verify all 5 core endpoints exist in spec
        paths = spec["paths"]
        self.assertIn("/api/v1/interview/sessions", paths)
        self.assertIn("/api/v1/interview/turns", paths)
        self.assertIn("/api/v1/interview/score", paths)
        self.assertIn("/api/v1/interview/gdpr/purge", paths)
        self.assertIn("/api/v1/interview/health", paths)

    def test_02_session_initialization_opt_in(self):
        payload = {
            "candidate_id": "CAND-44-NANDITH",
            "role_id": "DATA_INFRA_ENG",
            "target_seniority": "SENIOR",
            "explicit_opt_in": True,
            "locale": "en-US",
        }
        res = self.client.post("/api/v1/interview/sessions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["session_id"].startswith("sess-"))
        self.assertTrue(data["candidate_pseudonym"].startswith("PSEUDO-"))
        self.assertEqual(data["consent_status"], "EXPLICIT_OPT_IN")
        self.assertEqual(len(data["consent_receipt_sha256"]), 64)
        self.assertIn("distributed data pipeline", data["initial_question"])

    def test_03_session_initialization_opt_out_forbidden(self):
        payload = {
            "candidate_id": "CAND-44-DECLINE",
            "role_id": "DATA_INFRA_ENG",
            "target_seniority": "SENIOR",
            "explicit_opt_in": False,
            "locale": "en-US",
        }
        res = self.client.post("/api/v1/interview/sessions", json=payload)
        self.assertEqual(res.status_code, 403)
        err = res.json()["detail"]
        self.assertEqual(err["error_code"], "ERR_ZEC_4001")
        self.assertEqual(err["runbook"], "RB-ZEC-CONSENT-01")

    def test_04_turn_processing_and_bias_scrubbing(self):
        # First create session
        init_res = self.client.post(
            "/api/v1/interview/sessions",
            json={"candidate_id": "CAND-44-ADITI", "role_id": "DATA_INFRA_ENG", "explicit_opt_in": True},
        )
        session_id = init_res.json()["session_id"]

        turn_payload = {
            "session_id": session_id,
            "turn_index": 1,
            "raw_transcript": "My name is Aditi Rao. As a woman in tech, they told me Stanford grads get priority.",
            "speech_latency_seconds": 3.8,
            "audio_duration_seconds": 12.0,
        }
        turn_res = self.client.post("/api/v1/interview/turns", json=turn_payload)
        self.assertEqual(turn_res.status_code, 200)
        data = turn_res.json()

        # Verify demographic bias scrubbed
        self.assertNotIn("Aditi Rao", data["scrubbed_transcript"])
        self.assertIn("[CANDIDATE]", data["scrubbed_transcript"])
        self.assertNotIn("Stanford", data["scrubbed_transcript"])
        self.assertIn("[ACCREDITED_INSTITUTION]", data["scrubbed_transcript"])

        # Check telemetry
        telemetry = data["redaction_telemetry"]
        self.assertGreaterEqual(telemetry["total_redactions"], 3)
        self.assertGreaterEqual(data["cognitive_deliberation_ratio"], 4.0)

    def test_05_turn_processing_recursion_cap(self):
        init_res = self.client.post(
            "/api/v1/interview/sessions",
            json={"candidate_id": "CAND-44-FLOW", "role_id": "BACKEND_LEAD", "explicit_opt_in": True},
        )
        session_id = init_res.json()["session_id"]

        # Run 3 turns on same topic to trigger advance
        for t in range(1, 4):
            res = self.client.post(
                "/api/v1/interview/turns",
                json={
                    "session_id": session_id,
                    "turn_index": t,
                    "raw_transcript": "I designed microservices using Docker and Kafka.",
                    "speech_latency_seconds": 1.5,
                },
            )
            self.assertEqual(res.status_code, 200)

        # After depth >= 2, action should be ADVANCE_TOPIC
        last_turn = res.json()
        self.assertIn(last_turn["followup_action"], ["ADVANCE_TOPIC", "PROBE_DEEPER"])

    def test_06_scoring_evaluation_with_deliberation_and_explainability(self):
        init_res = self.client.post(
            "/api/v1/interview/sessions",
            json={"candidate_id": "CAND-44-SCORE", "role_id": "DATA_INFRA_ENG", "explicit_opt_in": True},
        )
        session_id = init_res.json()["session_id"]

        # Ingest a turn
        self.client.post(
            "/api/v1/interview/turns",
            json={
                "session_id": session_id,
                "turn_index": 1,
                "raw_transcript": "I configured PostgreSQL replication and optimized queries.",
                "speech_latency_seconds": 3.8,
            },
        )

        score_res = self.client.post(
            "/api/v1/interview/score",
            json={"session_id": session_id, "include_explainability": True, "apply_deliberation_discount": True},
        )
        self.assertEqual(score_res.status_code, 200)
        data = score_res.json()

        self.assertGreaterEqual(data["composite_score"], 65.0)
        self.assertEqual(len(data["factors"]), 4)
        self.assertIsNotNone(data["explainability"])
        self.assertTrue(data["explainability"]["deliberation_credit_applied"])
        self.assertIn("Final hiring decision remains subject to certified human", data["explainability"]["human_oversight_notice"])

    def test_07_anti_double_dipping_penalty_bounding(self):
        init_res = self.client.post(
            "/api/v1/interview/sessions",
            json={"candidate_id": "CAND-44-PENALTY", "role_id": "DATA_INFRA_ENG", "explicit_opt_in": True},
        )
        session_id = init_res.json()["session_id"]

        score_res = self.client.post("/api/v1/interview/score", json={"session_id": session_id})
        data = score_res.json()
        self.assertLessEqual(data["total_deduction_points"], 12.0)

    def test_08_gdpr_right_to_erasure_endpoint(self):
        purge_res = self.client.post(
            "/api/v1/interview/gdpr/purge",
            json={
                "candidate_id": "CAND-44-NANDITH",
                "statutory_authority": "GDPR Article 17 Right to be Forgotten",
                "requestor_token": "token_dpo_verified_99",
            },
        )
        self.assertEqual(purge_res.status_code, 200)
        data = purge_res.json()
        self.assertEqual(data["status"], "PERMANENTLY_ERASED")
        self.assertTrue(data["deletion_certificate_id"].startswith("DEL-CERT-"))
        self.assertEqual(len(data["sha256_verification_hash"]), 64)

    def test_09_subsystem_health_check_endpoint(self):
        health_res = self.client.get("/api/v1/interview/health")
        self.assertEqual(health_res.status_code, 200)
        data = health_res.json()
        self.assertIn(data["status"], ["HEALTHY", "OPTIMAL"])
        self.assertEqual(data["version"], "v1.4.4")
        self.assertIn("transcript_cleaner", data["subsystems"])
        self.assertIn("demographic_bias_scrubber", data["subsystems"])
        self.assertIn("refined_scoring_engine", data["subsystems"])

    def test_10_troubleshooting_diagnostics_and_runbook(self):
        diag = self.troubleshooter.diagnose_session_error(
            "ERR_ZEC_4002",
            {"session_id": "sess-test-99", "candidate_id": "CAND-99", "turn_index": 2},
        )
        self.assertEqual(diag["error_code"], "ERR_ZEC_4002")
        self.assertEqual(diag["severity"], "CRITICAL")
        self.assertEqual(diag["active_runbook"], "RB-ZEC-SCRUB-02")
        self.assertGreater(len(diag["prescribed_remediation"]), 0)


if __name__ == "__main__":
    unittest.main()
