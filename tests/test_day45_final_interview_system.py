"""
Unit Tests for Day 45: Final HR Interview AI System, Demo Dataset, and Handover
==============================================================================
Validates the complete capstone delivery:
- Demo dataset structure & integrity
- Multi-turn candidate interview simulation
- Deliberation credit & bounded scoring
- ESL dialect normalization
- Overqualification index calculation
- Manager evaluation audit scorecard
- Production handover manifest & module checksums
"""

import unittest
import json
import os
import time

from interview_ai.api_schemas import (
    InterviewSessionInitRequest,
    CandidateTurnRequest,
    ScoringEvaluationRequest,
    GDPRRetentionPurgeRequest,
)
from interview_ai.transcript_cleaner import TranscriptCleaner
from interview_ai.demographic_bias_scrubber import DemographicBiasScrubber
from interview_ai.stable_hr_flow_engine import StableHRFlowEngine
from interview_ai.refined_scoring_engine import RefinedScoringEngine
from interview_ai.compliance_retention_policy import ComplianceRetentionPolicyEngine
from interview_ai.manager_evaluation_audit import ManagerEvaluationAuditEngine
from interview_ai.handover_manifest import ProductionHandoverManifest


class TestDay45FinalInterviewSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_path = "data/day45_demo_interview_dataset.json"
        with open(cls.dataset_path, "r", encoding="utf-8") as f:
            cls.dataset = json.load(f)

        cls.cleaner = TranscriptCleaner()
        cls.scrubber = DemographicBiasScrubber()
        cls.flow = StableHRFlowEngine()
        cls.scorer = RefinedScoringEngine()
        cls.retention = ComplianceRetentionPolicyEngine()
        cls.audit_engine = ManagerEvaluationAuditEngine()
        cls.handover = ProductionHandoverManifest()

    def test_01_demo_dataset_integrity(self):
        """Verify demo dataset contains 5 diverse candidates with statutory receipts."""
        self.assertIn("benchmark_cohort", self.dataset)
        cohort = self.dataset["benchmark_cohort"]
        self.assertEqual(len(cohort), 5)

        candidate_ids = [c["candidate_id"] for c in cohort]
        self.assertEqual(candidate_ids, ["CAND-45-01", "CAND-45-02", "CAND-45-03", "CAND-45-04", "CAND-45-05"])

        for cand in cohort:
            self.assertTrue(cand["statutory_consent"]["explicit_opt_in"])
            self.assertEqual(len(cand["statutory_consent"]["receipt_sha256"]), 64)
            self.assertGreater(len(cand["turns"]), 0)

    def test_02_candidate_interview_simulation_flow(self):
        """Simulate candidate 1 (Aditi Rao) turn 1 through cleaner, scrubber, and flow engine."""
        cand = self.dataset["benchmark_cohort"][0]
        raw_text = cand["turns"][0]["raw_transcript"]

        cleaned = self.cleaner.clean(raw_text).cleaned_transcript
        self.assertNotIn("[noise]", cleaned.lower())

        scrubbed = self.scrubber.scrub(cleaned).scrubbed_text
        self.assertIn("[CANDIDATE]", scrubbed)
        self.assertNotIn("Aditi Rao", scrubbed)

        self.flow.reset()
        flow_action = self.flow.process_turn(scrubbed, latency_sec=3.2)
        self.assertIsNotNone(flow_action)

    def test_03_deliberation_credit_and_cdr_restoration(self):
        """Verify that analytical pause (3.2s latency, 22 words) triggers deliberation discount."""
        result = self.scorer.evaluate_candidate(
            candidate_id="CAND-45-01",
            candidate_name="Aditi Rao",
            target_role="Lead Cloud Infrastructure Architect",
            experience_years=8.5,
            semantic_relevance=88.5,
            communication_score=82.0,
            raw_composure=86.0,
            consistency_score=89.0,
            latency_seconds=3.2,
            answer_word_count=22,
            flags_or_penalties=["hesitation"],
        )
        self.assertTrue(result.deliberation_metrics.is_analytical_pause)
        self.assertGreater(result.deliberation_metrics.hesitation_penalty_discount, 0.0)
        self.assertGreaterEqual(result.net_refined_score, 85.0)

    def test_04_anti_double_dipping_deduction_bounding(self):
        """Verify that compounded penalties on nervous candidates are clamped at <= 12.0 pts deduction."""
        penalties = ["hesitation", "stutter", "acoustic_disfluency", "nervous_pause", "hesitation_repeat", "filler_saturation"]
        result = self.scorer.evaluate_candidate(
            candidate_id="CAND-45-TEST",
            candidate_name="Test Nervous Candidate",
            target_role="Senior Full-Stack Engineer",
            experience_years=6.0,
            semantic_relevance=75.0,
            communication_score=70.0,
            raw_composure=70.0,
            consistency_score=75.0,
            latency_seconds=4.0,
            answer_word_count=10,
            flags_or_penalties=penalties,
        )
        self.assertLessEqual(result.penalty_breakdown.net_bounded_penalty, 12.0)
        self.assertGreater(result.penalty_breakdown.penalty_damping_applied, 0.0)

    def test_05_esl_dialect_normalization(self):
        """Verify Priya Patel's ESL syntax is normalized without false negative penalty."""
        cand = self.dataset["benchmark_cohort"][2]
        raw_text = cand["turns"][0]["raw_transcript"]
        scrubbed = self.scrubber.scrub(raw_text).scrubbed_text

        # The scrubber normalizes 'prepone' to advance / did the needful
        self.assertIn("advance", scrubbed.lower())
        self.assertNotIn("prepone", scrubbed.lower())

    def test_06_overqualification_leveling_index(self):
        """Verify 16-year staff candidate Dr. Elena Rostova is flagged for role elevation."""
        cand = self.dataset["benchmark_cohort"][4]
        result = self.scorer.evaluate_candidate(
            candidate_id=cand["candidate_id"],
            candidate_name=cand["candidate_name"],
            target_role=cand["target_role"],
            experience_years=cand["experience_years"],
            semantic_relevance=96.0,
            communication_score=92.0,
            raw_composure=94.0,
            consistency_score=95.0,
            latency_seconds=2.9,
            answer_word_count=20,
            flags_or_penalties=[],
        )
        self.assertGreaterEqual(result.overqualification_index, 0.75)
        self.assertEqual(result.final_decision.value, "STRONG_HIRE")
        self.assertIn("UPGRADE", result.recommended_leveling_tier.value)

    def test_07_manager_evaluation_scorecard(self):
        """Verify manager evaluation audit engine yields grade >= 95% and APPROVED status."""
        scorecard = self.audit_engine.evaluate_audit_scorecard()
        self.assertGreaterEqual(scorecard["percentage_grade"], 95.0)
        self.assertEqual(scorecard["overall_verdict"], "APPROVED_FOR_PRODUCTION")
        self.assertEqual(len(scorecard["criteria_breakdown"]), 5)

    def test_08_post_feedback_enhancements_traceability(self):
        """Verify all 4 post-feedback enhancement tickets are verified active."""
        scorecard = self.audit_engine.evaluate_audit_scorecard()
        enhancements = scorecard["post_feedback_enhancements"]
        self.assertEqual(len(enhancements), 4)
        for enh in enhancements:
            self.assertEqual(enh["verification_status"], "VERIFIED_ACTIVE")

    def test_09_production_handover_manifest_and_checksums(self):
        """Verify handover manifest catalogs all 11 core modules with valid SHA-256."""
        manifest = self.handover.generate_manifest()
        self.assertEqual(manifest["operational_status"], "READY_FOR_COMMERCIAL_DEPLOYMENT")
        self.assertEqual(len(manifest["module_manifest"]), 11)

        for mod in manifest["module_manifest"]:
            self.assertEqual(mod["status"], "VERIFIED_PRODUCTION_READY")
            self.assertEqual(len(mod["sha256"]), 64)

    def test_10_end_to_end_decision_loop_latency(self):
        """Benchmark end-to-end turn processing loop completes in < 10.0ms."""
        start = time.perf_counter()
        cleaned = self.cleaner.clean("I deployed Kafka clusters with 3-node quorums.").cleaned_transcript
        scrubbed = self.scrubber.scrub(cleaned).scrubbed_text
        self.flow.reset()
        _ = self.flow.process_turn(scrubbed, latency_sec=2.0)
        result = self.scorer.evaluate_candidate(
            candidate_id="PERF-TEST",
            candidate_name="Perf Candidate",
            target_role="Cloud Architect",
            experience_years=5.0,
            semantic_relevance=80.0,
            communication_score=80.0,
            raw_composure=80.0,
            consistency_score=80.0,
            latency_seconds=2.0,
            answer_word_count=15,
            flags_or_penalties=[],
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed_ms, 10.0)


if __name__ == "__main__":
    unittest.main()
