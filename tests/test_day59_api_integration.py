"""
Unit Tests for Day 59: API & Integration Planning
=================================================
Platform: Zecpath Enterprise Automated Hiring Platform
Tests:
  - 5 Mandated AI APIs Registry & Subsystem Mapping
  - Formal JSON Schemas & OpenAPI 3.1 Paths Specification
  - Async Processing Lifecycle (Resume Parsing Worker Queue)
  - Sync Real-Time Scoring Execution & Latency SLA (<50ms)
  - JWT Bearer & HMAC-SHA256 Authentication Security
  - Token-Bucket Rate Limiter & Idempotency Key Deduplication
  - Exponential Backoff Retries & Dead-Letter Queue (DLQ) Routing
  - Bayesian Cross-Round Decision Arbitration & Floor Safeguards
"""

import unittest
import hmac
import hashlib
import time

from api_integration_ai import (
    ProcessingMode, JobStatus, AuthScheme, APIAuthContext,
    ResumeParseRequest, AsyncJobResponse,
    ATSScoreRequest, ATSScoreResponse,
    InterviewTurnRequest, InterviewTurnResponse,
    DecisionArbitrationRequest, DecisionArbitrationResponse,
    APIErrorEnvelope,
    APISchemaRegistry, APICatalogRegistry,
    APIIntegrationGateway, RateLimiter
)


class TestDay59APIIntegration(unittest.TestCase):

    def setUp(self):
        self.gateway = APIIntegrationGateway(shared_hmac_secret="test-secret-key-59")

    def test_catalog_registry_all_5_apis_present(self):
        apis = APICatalogRegistry.get_registered_apis()
        self.assertEqual(len(apis), 5)
        endpoints = [a.endpoint_id for a in apis]
        self.assertIn("API-01-RESUME-PARSE", endpoints)
        self.assertIn("API-02-ATS-SCORE", endpoints)
        self.assertIn("API-03-SCREENING-AI", endpoints)
        self.assertIn("API-04-INTERVIEW-AI", endpoints)
        self.assertIn("API-05-DECISION-AI", endpoints)

    def test_catalog_registry_processing_mode_mapping(self):
        apis = APICatalogRegistry.get_registered_apis()
        api_map = {a.endpoint_id: a.processing_mode for a in apis}
        # Resume parsing is ASYNC (batch/worker)
        self.assertEqual(api_map["API-01-RESUME-PARSE"], ProcessingMode.ASYNC)
        # ATS scoring is ASYNC
        self.assertEqual(api_map["API-02-ATS-SCORE"], ProcessingMode.ASYNC)
        # Screening is SYNC (conversational flow)
        self.assertEqual(api_map["API-03-SCREENING-AI"], ProcessingMode.SYNC)
        # Interview is SYNC (real-time sub-50ms)
        self.assertEqual(api_map["API-04-INTERVIEW-AI"], ProcessingMode.SYNC)
        # Decision is SYNC (instant arbitration)
        self.assertEqual(api_map["API-05-DECISION-AI"], ProcessingMode.SYNC)

    def test_json_schemas_generated_and_valid(self):
        schemas = APISchemaRegistry.get_all_schemas()
        self.assertGreaterEqual(len(schemas), 10)
        self.assertIn("ResumeParseRequest", schemas)
        self.assertIn("InterviewTurnRequest", schemas)
        self.assertIn("DecisionArbitrationResponse", schemas)

        resume_schema = schemas["ResumeParseRequest"]
        self.assertEqual(resume_schema["type"], "object")
        self.assertIn("document_url", resume_schema["properties"])

    def test_openapi_paths_specification_completeness(self):
        paths = APISchemaRegistry.get_openapi_paths_specification()
        self.assertIn("/api/v1/ai/resume/parse", paths)
        self.assertIn("/api/v1/ai/ats/score", paths)
        self.assertIn("/api/v1/ai/screening/utterance", paths)
        self.assertIn("/api/v1/ai/interview/turn", paths)
        self.assertIn("/api/v1/ai/decision/arbitrate", paths)

    def test_auth_bearer_jwt_valid(self):
        valid_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.fake_signature_valid"
        success, ctx, err = self.gateway.authenticate_request(valid_header, scheme=AuthScheme.BEARER_JWT)
        self.assertTrue(success)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx.tenant_id, "TENANT-ZECSER")
        self.assertIsNone(err)

    def test_auth_bearer_jwt_missing_or_invalid(self):
        success1, _, err1 = self.gateway.authenticate_request(None)
        self.assertFalse(success1)
        self.assertIn("Missing", err1)

        success2, _, err2 = self.gateway.authenticate_request("Bearer invalid-token")
        self.assertFalse(success2)
        self.assertIn("Expired or signature-invalid", err2)

    def test_auth_hmac_sha256_valid_and_tampered(self):
        payload = '{"candidate_id": "C-101", "decision": "ARBITRATE"}'
        secret = "test-secret-key-59"
        valid_sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

        # Valid HMAC signature
        success, ctx, _ = self.gateway.authenticate_request(
            auth_header="HMAC",
            scheme=AuthScheme.HMAC_SHA256,
            payload_body=payload,
            signature_header=valid_sig
        )
        self.assertTrue(success)
        self.assertEqual(ctx.auth_scheme, AuthScheme.HMAC_SHA256)

        # Tampered payload -> Signature mismatch
        tampered_payload = '{"candidate_id": "C-101", "decision": "TAMPERED"}'
        tampered_sig = hmac.new(secret.encode("utf-8"), tampered_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        bad_success, _, bad_err = self.gateway.authenticate_request(
            auth_header="HMAC",
            scheme=AuthScheme.HMAC_SHA256,
            payload_body=payload,  # original body
            signature_header=tampered_sig  # tampered signature
        )
        self.assertFalse(bad_success)
        self.assertIn("mismatch", bad_err)

    def test_rate_limiter_token_bucket(self):
        limiter = RateLimiter(capacity=3, refill_rate_per_sec=0.1)
        # First 3 tokens consumed
        self.assertTrue(limiter.is_allowed("CLIENT-A"))
        self.assertTrue(limiter.is_allowed("CLIENT-A"))
        self.assertTrue(limiter.is_allowed("CLIENT-A"))
        # 4th token rejected due to capacity exhaustion
        self.assertFalse(limiter.is_allowed("CLIENT-A"))

    def test_async_resume_parse_lifecycle(self):
        req = ResumeParseRequest(
            candidate_id="CAND-5901",
            document_url="https://s3.amazonaws.com/zecpath-vault/resumes/c5901.pdf",
            mime_type="application/pdf",
            extract_academic_profile=True
        )
        job, is_cached = self.gateway.submit_resume_parse_async(req)
        self.assertFalse(is_cached)
        self.assertEqual(job.status, JobStatus.QUEUED)
        self.assertIn("JOB-RESUME-", job.job_id)

        # Worker processes job
        completed_job = self.gateway.process_queued_resume_job(job.job_id)
        self.assertEqual(completed_job.status, JobStatus.COMPLETED)
        self.assertIsNotNone(completed_job.result)
        self.assertGreater(len(completed_job.result.skills), 0)
        self.assertEqual(completed_job.result.email_redacted, "c***@domain.com")

    def test_idempotency_key_deduplication(self):
        req = ResumeParseRequest(
            candidate_id="CAND-5902",
            document_url="https://s3.amazonaws.com/zecpath-vault/resumes/c5902.pdf"
        )
        idemp_key = "IDEMP-KEY-999-ABCD"

        # 1st call: queues new job
        job1, is_cached1 = self.gateway.submit_resume_parse_async(req, idempotency_key=idemp_key)
        self.assertFalse(is_cached1)

        # 2nd call with identical key: returns cached job
        job2, is_cached2 = self.gateway.submit_resume_parse_async(req, idempotency_key=idemp_key)
        self.assertTrue(is_cached2)
        self.assertEqual(job1.job_id, job2.job_id)

    def test_sync_interview_turn_scoring_low_latency(self):
        req = InterviewTurnRequest(
            interview_session_id="SESS-TURN-001",
            candidate_id="CAND-5903",
            current_topic="Distributed Consensus & Raft",
            candidate_answer_text="We implemented Raft consensus with log replication across three microservices nodes.",
            code_submission="def append_entries(term, leader_id): return True",
            speech_rate_wpm=172.0,
            turn_index=3
        )
        resp = self.gateway.execute_interview_turn_sync(req)
        self.assertEqual(resp.interview_session_id, "SESS-TURN-001")
        self.assertEqual(resp.turn_index, 3)
        self.assertGreaterEqual(resp.turn_technical_score, 80.0)
        # Low latency target
        self.assertLess(resp.sync_processing_latency_ms, 50.0)
        self.assertIsNotNone(resp.realtime_pacing_feedback)
        self.assertIn("Take a gentle pause", resp.realtime_pacing_feedback)

    def test_decision_arbitration_hard_tech_floor(self):
        # Candidate with weak tech (40%) but high HR verbal charm (90%)
        req = DecisionArbitrationRequest(
            candidate_id="CAND-5904",
            job_id="JOB-BACKEND",
            ats_score=85.0,
            screening_score=85.0,
            hr_behavioral_score=90.0,
            technical_code_score=40.0,  # Below 50% floor
            enforce_tech_floor=True
        )
        resp = self.gateway.execute_decision_arbitration(req)
        # Should NOT be HIRE due to technical deficit
        self.assertIn(resp.recommendation_verdict, ["HOLD_REVIEW", "REJECT"])
        self.assertTrue(any("HARD_TECH_FLOOR_ACTIVE" in s for s in resp.applied_safeguards))

    def test_decision_arbitration_strong_hire(self):
        req = DecisionArbitrationRequest(
            candidate_id="CAND-5905",
            job_id="JOB-BACKEND",
            ats_score=92.0,
            screening_score=90.0,
            hr_behavioral_score=88.0,
            technical_code_score=94.0
        )
        resp = self.gateway.execute_decision_arbitration(req)
        self.assertEqual(resp.recommendation_verdict, "STRONG_HIRE")
        self.assertGreaterEqual(resp.final_composite_score, 85.0)

    def test_exponential_backoff_transient_recovery(self):
        counter = {"attempts": 0}

        def flaky_task():
            counter["attempts"] += 1
            if counter["attempts"] < 2:
                raise ConnectionResetError("Transient network drop")
            return "SUCCESS_DATA"

        success, result, attempts = self.gateway.execute_with_retry_and_dlq(
            flaky_task, max_retries=3, base_delay_ms=2.0
        )
        self.assertTrue(success)
        self.assertEqual(result, "SUCCESS_DATA")
        self.assertEqual(attempts, 2)

    def test_dead_letter_queue_routing_on_exhaustion(self):
        def permanently_failing_task():
            raise TimeoutError("Upstream model service 504 Gateway Timeout")

        success, err_msg, attempts = self.gateway.execute_with_retry_and_dlq(
            permanently_failing_task, max_retries=3, base_delay_ms=2.0
        )
        self.assertFalse(success)
        self.assertEqual(attempts, 3)
        self.assertIn("504", err_msg)
        # Entry logged in Dead Letter Queue
        self.assertEqual(len(self.gateway.dead_letter_queue), 1)
        self.assertEqual(self.gateway.dead_letter_queue[0]["error_type"], "TimeoutError")

    def test_rfc7807_error_envelope_formatting(self):
        envelope = APIErrorEnvelope(
            type="https://api.zecpath.ai/errors/rate-limit-exceeded",
            title="Too Many Requests",
            status=429,
            detail="Client tenant exceeded rate limit of 100 requests per minute.",
            instance="/api/v1/ai/interview/turn"
        )
        self.assertEqual(envelope.status, 429)
        self.assertEqual(envelope.title, "Too Many Requests")
        self.assertIn("100 requests", envelope.detail)


if __name__ == "__main__":
    unittest.main()
