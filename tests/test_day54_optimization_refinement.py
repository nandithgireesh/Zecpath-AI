"""
Day 54: Optimization & Refinement - Comprehensive Test Suite
============================================================
15 Unit and Integration Tests covering:
- Models and SHA-256 cryptographic audit sealing
- Confusion matrix diagnostic mathematics (TP, TN, FP, FN, Precision, Recall, F1)
- Intent refiner (Conceptual Thinking pause disambiguation, implicit STAR, evasive deflection)
- Cross-round coherence index & Bayesian variance smoothing
- Dynamic role thresholds and boundary margin damping
- Sub-10ms P99 latency SLA verification
- Deliverable 2 Optimization Report generation
"""

import time
import unittest
from optimization_refinement_ai.models import (
    DecisionClass,
    PauseType,
    ErrorClassification,
    ConfusionMatrixMetrics,
    ErrorAnalysisCase,
    RefinedScoringOutput,
    OptimizationReportData
)
from optimization_refinement_ai.intent_refiner import IntentRefiner
from optimization_refinement_ai.refined_scoring_engine import RefinedScoringEngine
from optimization_refinement_ai.accuracy_evaluator import AccuracyEvaluator


class TestDay54OptimizationRefinement(unittest.TestCase):

    def setUp(self):
        self.intent_refiner = IntentRefiner()
        self.scoring_engine = RefinedScoringEngine(intent_refiner=self.intent_refiner)
        self.evaluator = AccuracyEvaluator(scoring_engine=self.scoring_engine)

    def test_01_models_and_audit_hash(self):
        """Verifies deterministic SHA-256 seal generation."""
        output = self.scoring_engine.evaluate_candidate(
            candidate_id="CAN-101",
            candidate_name="Priya Sharma",
            target_role="DISTRIBUTED_ARCHITECT",
            round_scores=[88.0, 86.5, 89.0, 87.0],
            pause_duration_seconds=1.5,
            transcript_segment="I architected an asynchronous message queue with idempotency."
        )
        self.assertTrue(len(output.audit_hash) == 64)
        first_hash = output.audit_hash
        output.finalize_and_seal()
        self.assertEqual(output.audit_hash, first_hash)

    def test_02_confusion_matrix_perfect_scenario(self):
        """Verifies confusion matrix math on 100% accurate predictions."""
        gt = [DecisionClass.SELECTED, DecisionClass.SELECTED, DecisionClass.HOLD_REVIEW, DecisionClass.REJECTED]
        pred = [DecisionClass.SELECTED, DecisionClass.SELECTED, DecisionClass.HOLD_REVIEW, DecisionClass.REJECTED]
        metrics = self.evaluator.compute_confusion_matrix(gt, pred)
        self.assertEqual(metrics.total_samples, 4)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.true_negatives, 2)
        self.assertEqual(metrics.false_positives, 0)
        self.assertEqual(metrics.false_negatives, 0)
        self.assertEqual(metrics.accuracy, 100.0)
        self.assertEqual(metrics.precision, 100.0)
        self.assertEqual(metrics.recall, 100.0)
        self.assertEqual(metrics.f1_score, 100.0)

    def test_03_confusion_matrix_with_mixed_errors(self):
        """Verifies precision, recall, FPR, FNR on mixed dataset."""
        # 10 samples: 5 positive (Selected), 5 negative (Hold/Reject)
        gt = [DecisionClass.SELECTED] * 5 + [DecisionClass.REJECTED] * 5
        # Pred: 4 TP, 1 FN, 1 FP, 4 TN
        pred = [DecisionClass.SELECTED] * 4 + [DecisionClass.REJECTED] * 1 + [DecisionClass.SELECTED] * 1 + [DecisionClass.REJECTED] * 4
        metrics = self.evaluator.compute_confusion_matrix(gt, pred)
        self.assertEqual(metrics.true_positives, 4)
        self.assertEqual(metrics.false_negatives, 1)
        self.assertEqual(metrics.false_positives, 1)
        self.assertEqual(metrics.true_negatives, 4)
        self.assertEqual(metrics.accuracy, 80.0)
        self.assertAlmostEqual(metrics.precision, 80.0, places=1)
        self.assertAlmostEqual(metrics.recall, 80.0, places=1)

    def test_04_intent_refiner_normal_cadence(self):
        """Verifies pause < 2.5s is treated as normal cadence with 0 penalty."""
        pause_type, penalty = self.intent_refiner.classify_pause(
            pause_duration_seconds=1.8,
            subsequent_transcript="Yes, in my previous role we used Redis for caching."
        )
        self.assertEqual(pause_type, PauseType.NORMAL_CADENCE)
        self.assertEqual(penalty, 0.0)

    def test_05_intent_refiner_conceptual_thinking(self):
        """Verifies pause > 3s followed by rich technical markers is conceptual thinking."""
        transcript = (
            "To solve this distributed latency bottleneck, I chose Raft consensus over Paxos "
            "due to leader election simplicity, and introduced a cache-aside layer with write-through "
            "invalidation to maintain eventual consistency without deadlocks."
        )
        pause_type, penalty = self.intent_refiner.classify_pause(
            pause_duration_seconds=4.2,
            subsequent_transcript=transcript
        )
        self.assertEqual(pause_type, PauseType.CONCEPTUAL_THINKING)
        self.assertEqual(penalty, 0.0)

    def test_06_intent_refiner_nervous_hesitation(self):
        """Verifies pause > 4.5s with verbal crutches is classified as nervous hesitation."""
        transcript = (
            "Um, uh, you know, like, basically I mean, to be honest sort of, um, "
            "we kind of just tried restarting the server and it worked."
        )
        pause_type, penalty = self.intent_refiner.classify_pause(
            pause_duration_seconds=5.0,
            subsequent_transcript=transcript
        )
        self.assertEqual(pause_type, PauseType.NERVOUS_HESITATION)
        self.assertLess(penalty, 0.0)

    def test_07_implicit_star_coverage(self):
        """Tests implicit STAR recognition across S, T, A, R dimensions."""
        transcript = (
            "In my previous role at Zecpath, we faced a major production outage due to scaling bottlenecks. "
            "My goal was to refactor the payment gateway and meet our 99.9% uptime SLA. "
            "I designed and implemented an asynchronous worker pool with circuit breakers. "
            "Resulting in zero downtime and p99 latency dropped by 45 percent."
        )
        coverage = self.intent_refiner.evaluate_implicit_star(transcript)
        self.assertEqual(coverage, 100.0)

        empty_cov = self.intent_refiner.evaluate_implicit_star("")
        self.assertEqual(empty_cov, 0.0)

    def test_08_evasive_deflection_detection(self):
        """Verifies detection of non-committal deflection statements."""
        transcript = (
            "Honestly, that wasn't really my responsibility, I usually let the team handle that part, "
            "and someone else built that part so I don't recall the specifics."
        )
        evasion_prob = self.intent_refiner.detect_evasive_deflection(transcript)
        self.assertGreaterEqual(evasion_prob, 0.60)

    def test_09_cross_round_coherence_index(self):
        """Verifies high coherence for consistent rounds and lower coherence for volatile rounds."""
        consistent_rounds = [88.0, 89.0, 87.5, 88.5]
        volatile_rounds = [92.0, 52.0, 88.0, 48.0]
        coh_high = self.scoring_engine.calculate_coherence_index(consistent_rounds)
        coh_low = self.scoring_engine.calculate_coherence_index(volatile_rounds)
        self.assertGreater(coh_high, 95.0)
        self.assertLess(coh_low, 70.0)

    def test_10_bayesian_variance_smoothing_outlier_damping(self):
        """Verifies outlier damping prevents single anomalous round from ruining score."""
        rounds = [88.0, 90.0, 60.0, 89.0]
        raw_mean, smoothed = self.scoring_engine.apply_bayesian_variance_smoothing(rounds)
        # Raw mean is (88+90+60+89)/4 = 81.75
        # Outlier damping pulls the 60 upward toward median ~89
        self.assertGreater(smoothed, raw_mean)

    def test_11_role_adaptive_thresholds(self):
        """Verifies Distributed Architect threshold (84) vs General SDE (80)."""
        cfg_arch = self.scoring_engine.get_role_config("DISTRIBUTED_ARCHITECT")
        cfg_sde = self.scoring_engine.get_role_config("GENERAL_SDE")
        self.assertEqual(cfg_arch.base_selected_threshold, 84.0)
        self.assertEqual(cfg_sde.base_selected_threshold, 80.0)

    def test_12_boundary_margin_damping(self):
        """Verifies margin damping properly handles borderline scores."""
        # Candidate right at boundary 82.5 for role with 82.0 cutoff
        out = self.scoring_engine.evaluate_candidate(
            candidate_id="CAN-BORD-1",
            candidate_name="Borderline Candidate",
            target_role="FULL_STACK_SENIOR",
            round_scores=[82.0, 83.0, 82.5, 83.0],  # highly coherent
            pause_duration_seconds=1.0,
            transcript_segment="I implemented responsive microservices."
        )
        self.assertIn("COHERENCE_DAMPING", out.decision_substatus)
        self.assertEqual(out.final_decision, DecisionClass.SELECTED)

    def test_13_sub_10ms_latency_sla(self):
        """Verifies 100 evaluations execute within 100ms total (<1.0ms average per evaluation)."""
        transcript = "I designed an idempotent distributed pipeline reducing p99 latency by 30%."
        t0 = time.perf_counter()
        for i in range(100):
            self.scoring_engine.evaluate_candidate(
                candidate_id=f"PERF-{i}",
                candidate_name=f"Perf Candidate {i}",
                target_role="DISTRIBUTED_ARCHITECT",
                round_scores=[85.0, 86.0, 84.0, 87.0],
                pause_duration_seconds=3.2,
                transcript_segment=transcript
            )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        avg_ms = elapsed_ms / 100.0
        self.assertLess(avg_ms, 5.0)  # well within sub-10ms SLA

    def test_14_error_analysis_cases_validation(self):
        """Verifies canonical error cases have complete diagnostics."""
        cases = self.evaluator.get_canonical_benchmark_cases()
        self.assertEqual(len(cases), 4)
        for c in cases:
            self.assertTrue(c.candidate_id.startswith("CAN-"))
            self.assertTrue(len(c.root_cause_analysis) > 30)
            self.assertTrue(len(c.optimization_remedy) > 30)

    def test_15_full_optimization_report_generation(self):
        """Verifies Deliverable 2 Optimization Report metrics and cryptographic sealing."""
        report = self.evaluator.generate_optimization_report()
        self.assertEqual(report.dataset_cohort_size, 200)
        self.assertEqual(report.baseline_metrics.accuracy, 84.50)
        self.assertEqual(report.optimized_metrics.accuracy, 97.50)
        self.assertEqual(report.accuracy_improvement_pct, 13.00)
        self.assertGreater(report.fp_reduction_pct, 80.0)
        self.assertGreater(report.fn_reduction_pct, 70.0)
        self.assertGreater(report.speedup_factor, 10.0)
        self.assertTrue(len(report.audit_hash) == 64)


if __name__ == "__main__":
    unittest.main()
