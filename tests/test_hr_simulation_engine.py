"""
Unit Tests for Day 40: HR Interview Simulation & Accuracy Evaluation
===================================================================
Validates:
1. Standard cohort profiles specification (5 archetypes)
2. Confident candidate simulation (Aditi Rao -> Strong Hire)
3. Hesitant candidate simulation (Siddharth Verma -> Lean Hire)
4. Inexperienced candidate simulation (Kavita Patel -> Lean No Hire, Vagueness probe)
5. Overqualified candidate simulation (Dr. Rajesh Sundaram -> Strong Hire / Leveling)
6. Inconsistent candidate simulation (Tarun Khanna -> No Hire, Critical Fallacies)
7. Statistical accuracy evaluation (MAE, RMSE, Pearson r, Concordance)
8. Discrepancy diagnosis and root cause analysis
9. Benchmark report JSON & Markdown export integrity
"""

import os
import shutil
import unittest
from datetime import datetime

from interview_ai.simulation_models import (
    CandidateArchetype,
    SimulatedCandidateProfile,
    SimulationTurnData,
    SessionSimulationResult,
    AccuracyBenchmarkReport,
)
from interview_ai.simulation_engine import HRInterviewSimulationEngine
from interview_ai.accuracy_evaluator import AccuracyEvaluator
from interview_ai.hr_scoring_models import HiringRecommendation


class TestHRInterviewSimulationEngine(unittest.TestCase):
    """Test suite for Day 40 HR interview simulation and accuracy benchmarking."""

    @classmethod
    def setUpClass(cls):
        cls.test_output_dir = "data/test_simulations"
        os.makedirs(cls.test_output_dir, exist_ok=True)
        cls.engine = HRInterviewSimulationEngine(output_dir=cls.test_output_dir)
        cls.evaluator = AccuracyEvaluator()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)

    def test_01_standard_cohort_profiles_specification(self):
        """Validates that 5 distinct candidate archetypes are defined with ground truth."""
        profiles = self.engine.get_standard_cohort_profiles()
        self.assertEqual(len(profiles), 5)

        archetypes = {p.archetype for p in profiles}
        expected_archetypes = {
            CandidateArchetype.CONFIDENT,
            CandidateArchetype.HESITANT,
            CandidateArchetype.INEXPERIENCED,
            CandidateArchetype.OVERQUALIFIED,
            CandidateArchetype.INCONSISTENT,
        }
        self.assertEqual(archetypes, expected_archetypes)

        for p in profiles:
            self.assertTrue(p.candidate_id.startswith("SIM-"))
            self.assertGreater(p.experience_years, 0.0)
            self.assertIsNotNone(p.human_ground_truth)
            self.assertGreater(p.human_ground_truth.composite_score, 0.0)

    def test_02_confident_candidate_simulation(self):
        """Validates simulation of confident, high-performing candidate."""
        profiles = [p for p in self.engine.get_standard_cohort_profiles() if p.archetype == CandidateArchetype.CONFIDENT]
        result = self.engine.simulate_session(profiles[0])

        self.assertEqual(result.ai_recommendation, HiringRecommendation.STRONG_HIRE)
        self.assertGreaterEqual(result.ai_composite_score, 85.0)
        self.assertEqual(result.inconsistencies_detected, 0)
        self.assertTrue(result.decision_match)
        self.assertLess(abs(result.score_variance), 2.0)
        self.assertTrue(os.path.exists(result.summary_json_path))

    def test_03_hesitant_candidate_simulation(self):
        """Validates simulation of competent but hesitant candidate."""
        profiles = [p for p in self.engine.get_standard_cohort_profiles() if p.archetype == CandidateArchetype.HESITANT]
        result = self.engine.simulate_session(profiles[0])

        self.assertEqual(result.ai_recommendation, HiringRecommendation.LEAN_HIRE)
        self.assertGreaterEqual(result.ai_composite_score, 60.0)
        self.assertLess(result.ai_composite_score, 75.0)
        self.assertTrue(result.decision_match)
        self.assertLess(abs(result.score_variance), 5.0)

    def test_04_inexperienced_candidate_simulation(self):
        """Validates simulation of inexperienced candidate triggering dynamic follow-up."""
        profiles = [p for p in self.engine.get_standard_cohort_profiles() if p.archetype == CandidateArchetype.INEXPERIENCED]
        result = self.engine.simulate_session(profiles[0])

        self.assertEqual(result.ai_recommendation, HiringRecommendation.LEAN_NO_HIRE)
        self.assertGreaterEqual(result.ai_composite_score, 45.0)
        self.assertLess(result.ai_composite_score, 60.0)
        self.assertTrue(result.decision_match)
        # Verify dynamic follow-up was triggered
        followups = [t for t in result.turns_executed if t.dynamic_followup_triggered]
        self.assertGreater(len(followups), 0)
        self.assertEqual(followups[0].followup_reason, "VAGUENESS_DETECTED")

    def test_05_overqualified_candidate_simulation(self):
        """Validates simulation of overqualified candidate."""
        profiles = [p for p in self.engine.get_standard_cohort_profiles() if p.archetype == CandidateArchetype.OVERQUALIFIED]
        result = self.engine.simulate_session(profiles[0])

        self.assertEqual(result.ai_recommendation, HiringRecommendation.STRONG_HIRE)
        self.assertGreaterEqual(result.ai_composite_score, 90.0)
        # Adjacent tier concordance with human panel (Strong Hire vs Hire)
        self.assertLessEqual(result.tier_distance, 1)

    def test_06_inconsistent_candidate_simulation(self):
        """Validates simulation of inconsistent/high-risk candidate with critical fallacies."""
        profiles = [p for p in self.engine.get_standard_cohort_profiles() if p.archetype == CandidateArchetype.INCONSISTENT]
        result = self.engine.simulate_session(profiles[0])

        self.assertEqual(result.ai_recommendation, HiringRecommendation.NO_HIRE)
        self.assertLess(result.ai_composite_score, 45.0)
        self.assertTrue(result.decision_match)
        self.assertGreaterEqual(result.inconsistencies_detected, 2)

    def test_07_accuracy_evaluator_statistical_metrics(self):
        """Validates computation of statistical accuracy benchmark metrics."""
        results = self.engine.run_cohort_simulation()
        report = self.evaluator.evaluate_cohort(results)

        # Assertions against benchmark thresholds
        self.assertEqual(report.total_sessions_simulated, 5)
        self.assertLess(report.mean_absolute_error, 3.5, "MAE must be below 3.5 pts")
        self.assertLess(report.root_mean_squared_error, 4.0, "RMSE must be below 4.0 pts")
        self.assertGreater(report.pearson_correlation, 0.95, "Pearson r must be above 0.95")
        self.assertGreater(report.spearman_rank_correlation, 0.85, "Spearman rho must be above 0.85")
        self.assertGreaterEqual(report.exact_decision_concordance_pct, 75.0, "Exact concordance must be >= 75%")
        self.assertEqual(report.adjacent_decision_concordance_pct, 100.0, "Adjacent concordance must be 100%")
        self.assertGreater(report.f1_macro, 0.70, "Macro F1 must be above 0.70")

    def test_08_discrepancy_diagnosis(self):
        """Validates that edge cases and discrepancies are correctly diagnosed."""
        results = self.engine.run_cohort_simulation()
        diagnoses = self.evaluator.diagnose_discrepancies(results)

        self.assertEqual(len(diagnoses), 5)
        diag_types = {d.discrepancy_type for d in diagnoses}
        self.assertIn("OVERQUALIFICATION_LEVELING_DIVERGENCE", diag_types)
        self.assertIn("HESITATION_ACOUSTIC_SENSITIVITY", diag_types)
        self.assertIn("VAGUENESS_PROBING_CONVERGENCE", diag_types)

        for d in diagnoses:
            self.assertTrue(len(d.root_cause) > 20)
            self.assertTrue(len(d.remediation_recommendation) > 20)

    def test_09_report_exports(self):
        """Validates export of JSON benchmark report and Markdown report generation."""
        results = self.engine.run_cohort_simulation()
        report = self.evaluator.evaluate_cohort(results)

        json_path = os.path.join(self.test_output_dir, "test_accuracy_report.json")
        self.evaluator.export_benchmark_json(report, json_path)
        self.assertTrue(os.path.exists(json_path))

        md_content = self.evaluator.generate_accuracy_markdown(report, results)
        self.assertIn("Deliverable 2: HR Interview Accuracy Evaluation", md_content)
        self.assertIn("Statistical Metric Summary", md_content)
        self.assertIn("Decision Concordance Matrix", md_content)


if __name__ == "__main__":
    unittest.main()
