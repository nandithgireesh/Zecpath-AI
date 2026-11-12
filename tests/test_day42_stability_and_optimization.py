"""
Unit Test Suite for Day 42: Optimization & Stability
====================================================
Tests the 3 core deliverables:
1. TranscriptCleaner: ASR noise, stutters, filler consolidation.
2. StableHRFlowEngine: Recursion bounds, entity grounding, deadlock handling.
3. RefinedScoringEngine: Dual-track latency, bounded penalties, OLI leveling.
4. OptimizationBenchmarkSuite: Empirical benchmark execution and reliability.
"""

import unittest
from interview_ai.transcript_cleaner import TranscriptCleaner, CleaningResult
from interview_ai.stable_hr_flow_engine import StableHRFlowEngine, FlowGuardConfig, DynamicProbeDecision
from interview_ai.refined_scoring_models import (
    RefinedDecisionTier,
    LevelingUpgradeTier,
    RefinedScoreSummary,
)
from interview_ai.refined_scoring_engine import RefinedScoringEngine
from interview_ai.optimization_benchmarks import OptimizationBenchmarkSuite
from interview_ai.hr_models import HRInterviewSession, FollowUpTriggerReason


class TestDay42OptimizationAndStability(unittest.TestCase):

    def setUp(self):
        self.cleaner = TranscriptCleaner()
        self.flow_engine = StableHRFlowEngine(config=FlowGuardConfig(max_followups_per_topic=2, max_followups_per_session=4))
        self.refined_scorer = RefinedScoringEngine()
        self.benchmarks = OptimizationBenchmarkSuite()

    def test_01_transcript_cleaner_asr_noise_and_fillers(self):
        """Verifies stripping of ASR acoustic tags and vocalic fillers."""
        raw = "Um... <cough> I worked on, you know, distributed systems uh... sort of like at scale."
        result = self.cleaner.clean(raw)
        self.assertNotIn("<cough>", result.cleaned_transcript)
        self.assertNotIn("Um", result.cleaned_transcript)
        self.assertNotIn("uh", result.cleaned_transcript)
        self.assertNotIn("you know", result.cleaned_transcript)
        self.assertIn("distributed systems", result.cleaned_transcript)
        self.assertGreater(result.fillers_removed_count, 0)
        self.assertGreater(result.artifacts_removed_count, 0)

    def test_02_transcript_cleaner_stutter_removal(self):
        """Verifies collapsing of speech stuttering and repeated words."""
        raw = "I... I... I built the the microservice using Kafka."
        result = self.cleaner.clean(raw)
        self.assertTrue(result.cleaned_transcript.startswith("I built the microservice using Kafka"))
        self.assertGreater(result.stutters_removed_count, 0)

    def test_03_transcript_cleaner_throughput_and_latency(self):
        """Verifies transcript cleaner latency is sub-millisecond."""
        raw = "We used Docker and Kubernetes for container orchestration and automated rollbacks."
        result = self.cleaner.clean(raw)
        self.assertLess(result.latency_microseconds, 5000)  # < 5ms
        self.assertEqual(result.word_count_cleaned, len(result.cleaned_transcript.split()))

    def test_04_stable_flow_engine_recursion_bounds(self):
        """Verifies follow-up recursion strictly terminates at max_followups_per_topic."""
        from interview_ai.hr_models import HRInterviewConfig
        cfg = HRInterviewConfig.auto_classify("C-01", "Candidate", "Backend Eng", 3.0)
        session = HRInterviewSession(session_id="S-01", config=cfg)
        decision = self.flow_engine.evaluate_response(
            session=session,
            current_question="How did you scale Kafka?",
            current_category="TECHNICAL",
            raw_answer="We scaled partitions.",
            current_topic_depth=2,  # Already at limit
        )
        self.assertFalse(decision.should_probe, "Must not probe beyond topic recursion bounds")
        self.assertIsNone(decision.probe_question)

    def test_05_stable_flow_engine_entity_grounding(self):
        """Verifies entity-grounded question formulation on brief technical answers."""
        from interview_ai.hr_models import HRInterviewConfig
        cfg = HRInterviewConfig.auto_classify("C-02", "Candidate", "Data Eng", 3.0)
        session = HRInterviewSession(session_id="S-02", config=cfg)
        decision = self.flow_engine.evaluate_response(
            session=session,
            current_question="What messaging queue did you pick?",
            current_category="TECHNICAL",
            raw_answer="We just used Kafka and Docker.",
            current_topic_depth=0,
        )
        self.assertTrue(decision.should_probe)
        self.assertIsNotNone(decision.grounded_entity)
        self.assertIn(decision.grounded_entity, ["Kafka", "Docker"])
        self.assertIn(decision.grounded_entity, decision.probe_question)

    def test_06_stable_flow_engine_deadlock_recovery(self):
        """Verifies deadlock & evasion detection gracefully skips follow-up."""
        from interview_ai.hr_models import HRInterviewConfig
        cfg = HRInterviewConfig.auto_classify("C-03", "Candidate", "DevOps", 3.0)
        session = HRInterviewSession(session_id="S-03", config=cfg)
        decision = self.flow_engine.evaluate_response(
            session=session,
            current_question="Explain eBPF security policies.",
            current_category="TECHNICAL",
            raw_answer="I don't know, skip this please.",
        )
        self.assertFalse(decision.should_probe)
        self.assertTrue(decision.deadlock_detected)

    def test_07_refined_scoring_dual_track_latency_filter(self):
        """Verifies analytical pause is recognized and composure score is restored."""
        summary = self.refined_scorer.evaluate_candidate(
            candidate_id="SIM-HES-02",
            candidate_name="Siddharth Verma",
            target_role="Data Infrastructure Engineer",
            experience_years=4.0,
            semantic_relevance=72.0,
            communication_score=68.0,
            raw_composure=64.0,
            consistency_score=74.0,
            latency_seconds=3.8,
            answer_word_count=85,
            flags_or_penalties=["HESITATION_DETECTED"],
        )
        self.assertTrue(summary.deliberation_metrics.is_analytical_pause)
        self.assertGreater(summary.composure_confidence_score, 64.0)
        self.assertGreaterEqual(summary.net_refined_score, 68.0)
        self.assertEqual(summary.final_decision, RefinedDecisionTier.LEAN_HIRE)

    def test_08_refined_scoring_anti_double_dipping_cap(self):
        """Verifies penalty bounding caps deductions at 12.0 pts and prevents score collapse."""
        summary = self.refined_scorer.evaluate_candidate(
            candidate_id="SIM-INCON-05",
            candidate_name="Tarun Khanna",
            target_role="Senior Backend Lead",
            experience_years=6.0,
            semantic_relevance=52.0,
            communication_score=54.0,
            raw_composure=45.0,
            consistency_score=42.0,
            latency_seconds=2.8,
            answer_word_count=60,
            flags_or_penalties=["CONTRADICTION", "BLAME_DEFLECTION", "FALSE_DILEMMA", "VAGUENESS"],
        )
        self.assertLessEqual(summary.penalty_breakdown.net_bounded_penalty, 12.0)
        self.assertGreater(summary.penalty_breakdown.penalty_damping_applied, 0.0)
        self.assertEqual(summary.final_decision, RefinedDecisionTier.NO_HIRE)

    def test_09_refined_scoring_overqualification_leveling(self):
        """Verifies high experience + high score triggers Staff/Principal leveling upgrade."""
        summary = self.refined_scorer.evaluate_candidate(
            candidate_id="SIM-OVER-04",
            candidate_name="Dr. Rajesh Sundaram",
            target_role="DevOps Engineer",
            experience_years=14.0,
            semantic_relevance=94.0,
            communication_score=90.0,
            raw_composure=92.0,
            consistency_score=94.0,
            latency_seconds=0.9,
            answer_word_count=140,
            flags_or_penalties=[],
        )
        self.assertEqual(summary.recommended_leveling_tier, LevelingUpgradeTier.STAFF_PRINCIPAL_UPGRADE)
        self.assertGreater(summary.overqualification_index, 1.20)
        self.assertEqual(summary.final_decision, RefinedDecisionTier.STRONG_HIRE)

    def test_10_adversarial_stress_and_null_resiliency(self):
        """Verifies zero-crash reliability on adversarial edge cases."""
        passed, total, crash_rate = self.benchmarks.run_stress_test(trials=100)
        self.assertEqual(passed, total)
        self.assertEqual(crash_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
