"""
Unit Tests for Day 30 Threshold Optimization & False Rejection Reduction
========================================================================
"""

import os
import json
import unittest

from screening_ai.threshold_optimizer import ScreeningThresholdOptimizer
from screening_ai.optimization_models import ThresholdConfig, EvaluationMetrics
from screening_ai.report_models import HiringRecommendation


class TestThresholdOptimization(unittest.TestCase):
    def setUp(self):
        self.optimizer = ScreeningThresholdOptimizer()
        self.benchmark_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "benchmarks", "human_screening_benchmark.json"
        )
        with open(self.benchmark_path, "r", encoding="utf-8") as f:
            self.benchmark_data = json.load(f)

    def test_baseline_config_defaults(self):
        cfg = self.optimizer.get_baseline_config()
        self.assertEqual(cfg.name, "baseline_strict")
        self.assertFalse(cfg.enable_tech_compensation)
        self.assertFalse(cfg.brevity_protection)
        self.assertFalse(cfg.enable_second_look_routing)

    def test_optimized_config_defaults(self):
        cfg = self.optimizer.get_optimized_config()
        self.assertEqual(cfg.name, "day30_optimized")
        self.assertTrue(cfg.enable_tech_compensation)
        self.assertTrue(cfg.brevity_protection)
        self.assertTrue(cfg.enable_second_look_routing)
        self.assertEqual(cfg.tech_compensation_threshold, 78.0)

    def test_technical_depth_compensation(self):
        # Candidate with very high tech (88.0) but lower communication (58.0) due to nervousness
        base_cfg = self.optimizer.get_baseline_config()
        opt_cfg = self.optimizer.get_optimized_config()

        base_rec = self.optimizer.evaluate_recommendation(
            overall_score=71.0,
            technical_score=88.0,
            communication_score=58.0,
            config=base_cfg,
        )
        opt_rec = self.optimizer.evaluate_recommendation(
            overall_score=71.0,
            technical_score=88.0,
            communication_score=58.0,
            config=opt_cfg,
        )

        # Baseline demotes candidate to PROCEED_WITH_CAUTION (below communication cutoff 65.0)
        self.assertEqual(base_rec, HiringRecommendation.PROCEED_WITH_CAUTION)
        # Optimized rescues via Technical Depth Compensation to HIRE
        self.assertEqual(opt_rec, HiringRecommendation.HIRE)


    def test_second_look_borderline_routing(self):
        opt_cfg = self.optimizer.get_optimized_config()
        rec = self.optimizer.evaluate_recommendation(
            overall_score=67.0,
            technical_score=66.0,
            communication_score=68.0,
            config=opt_cfg,
        )
        self.assertEqual(rec, HiringRecommendation.PROCEED_WITH_CAUTION)

    def test_automatic_disqualifier_critical_risk(self):
        opt_cfg = self.optimizer.get_optimized_config()
        rec = self.optimizer.evaluate_recommendation(
            overall_score=95.0,
            technical_score=95.0,
            communication_score=95.0,
            has_critical_risk=True,
            config=opt_cfg,
        )
        self.assertEqual(rec, HiringRecommendation.NO_HIRE)

    def test_unacceptable_salary_disqualification(self):
        opt_cfg = self.optimizer.get_optimized_config()
        rec = self.optimizer.evaluate_recommendation(
            overall_score=90.0,
            technical_score=90.0,
            communication_score=90.0,
            salary_acceptable=False,
            config=opt_cfg,
        )
        self.assertEqual(rec, HiringRecommendation.NO_HIRE)

    def test_metric_computation_math(self):
        preds = [
            HiringRecommendation.HIRE,
            HiringRecommendation.HIRE,
            HiringRecommendation.NO_HIRE,
            HiringRecommendation.NO_HIRE,
        ]
        gts = [
            HiringRecommendation.HIRE,
            HiringRecommendation.HIRE,
            HiringRecommendation.NO_HIRE,
            HiringRecommendation.HIRE,  # 1 false negative
        ]
        metrics = self.optimizer.compute_metrics(preds, gts)
        self.assertEqual(metrics.total_evaluations, 4)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.true_negatives, 1)
        self.assertEqual(metrics.false_positives, 0)
        self.assertEqual(metrics.false_negatives, 1)
        self.assertEqual(metrics.precision, 1.0)
        self.assertAlmostEqual(metrics.recall, 0.6667, places=3)
        self.assertAlmostEqual(metrics.false_rejection_rate, 0.3333, places=3)
        self.assertEqual(metrics.false_acceptance_rate, 0.0)

    def test_benchmark_comparison_report(self):
        profiles = self.benchmark_data["profiles"]
        report = self.optimizer.compare_benchmarks(profiles)
        self.assertEqual(report.benchmark_profiles_evaluated, 12)
        self.assertGreater(report.false_rejection_reduction_pct, 50.0)
        self.assertGreater(len(report.resolved_candidates), 0)
        self.assertEqual(report.optimized_metrics.false_acceptance_rate, 0.0)
        self.assertGreaterEqual(report.optimized_metrics.f1_score, 0.90)


if __name__ == "__main__":
    unittest.main()
