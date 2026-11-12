"""
Unit Tests for Day 41: Unified Scoring Engine & Cross-Round Hiring Intelligence
==============================================================================
Validates:
1. Cross-round weight presets & mathematical normalization (sums to 1.0)
2. Custom weight profile validation & error handling
3. Role-based automatic profile keyword resolution
4. Confident candidate evaluation (Aditi Rao -> Strong Hire)
5. Hesitant candidate evaluation (Siddharth Verma -> Lean Hire)
6. Inexperienced candidate evaluation (Kavita Patel -> Lean No Hire)
7. Overqualified candidate evaluation (Dr. Rajesh Sundaram -> Strong Hire / Leveling)
8. Inconsistent candidate evaluation (Tarun Khanna -> No Hire, Risk Discount & Gate Fail)
9. Missing round safety gate rejection
10. Unified Candidate Score Object serialization (ATS JSON & Recruiter Markdown)
"""

import os
import json
import shutil
import unittest

from unified_scoring.models import (
    RoundType,
    RoleFamily,
    HiringDecisionTier,
    ReadinessLevel,
    RoundScoreInput,
    CrossRoundWeightProfile,
    UnifiedCandidateScoreObject,
)
from unified_scoring.weight_system import CrossRoundWeightSystem, WeightConfigurationError
from unified_scoring.hiring_fit_calculator import HiringFitCalculator
from unified_scoring.cross_round_engine import UnifiedScoringEngine
from unified_scoring.unified_score_object import UnifiedScoreObjectFormatter


class TestUnifiedScoringEngine(unittest.TestCase):
    """Test suite for Day 41 Unified Scoring Engine."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = "data/test_unified_scores"
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.engine = UnifiedScoringEngine(output_dir=cls.test_dir)
        cls.weight_system = CrossRoundWeightSystem()
        cls.calculator = HiringFitCalculator()
        cls.formatter = UnifiedScoreObjectFormatter()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_01_cross_round_weight_presets_normalization(self):
        """Validates all 5 presets have weights summing to 1.0 and valid thresholds."""
        profiles = self.weight_system.list_all_profiles()
        self.assertEqual(len(profiles), 5)

        for p in profiles:
            total_w = p.ats_weight + p.screening_weight + p.hr_interview_weight
            self.assertAlmostEqual(total_w, 1.0, places=4, msg=f"Weights in {p.display_name} must sum to 1.0")
            self.assertGreater(p.ats_weight, 0.0)
            self.assertGreater(p.screening_weight, 0.0)
            self.assertGreater(p.hr_interview_weight, 0.0)
            self.assertGreaterEqual(len(p.minimum_thresholds), 2)

    def test_02_custom_weight_profile_validation(self):
        """Validates custom profile creation and error enforcement."""
        # Valid custom profile
        custom = self.weight_system.create_custom_profile(
            display_name="Enterprise Research Track",
            ats_weight=0.30,
            screening_weight=0.30,
            hr_interview_weight=0.40,
        )
        self.assertEqual(custom.role_family, RoleFamily.CUSTOM_ENTERPRISE)
        self.assertAlmostEqual(custom.ats_weight + custom.screening_weight + custom.hr_interview_weight, 1.0)

        # Invalid sum (> 1.0)
        with self.assertRaises(WeightConfigurationError):
            self.weight_system.create_custom_profile(
                display_name="Invalid Track",
                ats_weight=0.50,
                screening_weight=0.50,
                hr_interview_weight=0.50,
            )

        # Invalid negative weight
        with self.assertRaises(WeightConfigurationError):
            self.weight_system.create_custom_profile(
                display_name="Negative Track",
                ats_weight=-0.10,
                screening_weight=0.50,
                hr_interview_weight=0.60,
            )

    def test_03_role_profile_auto_detection(self):
        """Validates role keyword matching across role families."""
        self.assertEqual(
            self.weight_system.resolve_profile_for_role("Senior Python Backend Engineer").role_family,
            RoleFamily.TECHNICAL_ENGINEERING,
        )
        self.assertEqual(
            self.weight_system.resolve_profile_for_role("VP of Platform Engineering").role_family,
            RoleFamily.LEADERSHIP_MANAGEMENT,
        )
        self.assertEqual(
            self.weight_system.resolve_profile_for_role("Enterprise Account Executive").role_family,
            RoleFamily.SALES_CUSTOMER_FACING,
        )
        self.assertEqual(
            self.weight_system.resolve_profile_for_role("Software Engineering Graduate Intern").role_family,
            RoleFamily.EARLY_CAREER_FRESHER,
        )
        self.assertEqual(
            self.weight_system.resolve_profile_for_role("Cloud Infrastructure NOC Support Specialist").role_family,
            RoleFamily.OPERATIONS_SUPPORT,
        )

    def test_04_confident_candidate_evaluation(self):
        """Validates evaluation of high-performing candidate (Aditi Rao)."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-CONF-01",
            candidate_name="Aditi Rao",
            target_role="Senior Cloud Platform Architect",
            experience_years=7.5,
            ats_input={"final_ats_score": 88.0, "skill_score": 90.0, "experience_score": 86.0},
            screening_input={"overall_score": 85.0, "clarity_score": 86.0, "behavioral_score": 84.0},
            hr_input={"composite_score": 90.3, "communication_score": 88.0, "aptitude_score": 92.0, "cultural_fit": 85.0},
        )

        self.assertEqual(score_obj.final_decision, HiringDecisionTier.STRONG_HIRE)
        self.assertEqual(score_obj.readiness_level, ReadinessLevel.IMMEDIATE_FAST_TRACK)
        self.assertGreaterEqual(score_obj.hiring_fit.net_hiring_fit_percentage, 85.0)
        self.assertTrue(score_obj.safety_gate_passed)
        self.assertIn("Senior", score_obj.calibrated_role_tier)

    def test_05_hesitant_candidate_evaluation(self):
        """Validates evaluation of competent but hesitant candidate (Siddharth Verma)."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-HES-02",
            candidate_name="Siddharth Verma",
            target_role="Data Infrastructure Engineer",
            experience_years=4.0,
            ats_input={"final_ats_score": 72.0, "skill_score": 75.0, "experience_score": 70.0},
            screening_input={"overall_score": 70.0, "clarity_score": 72.0, "behavioral_score": 68.0},
            hr_input={"composite_score": 65.0, "communication_score": 64.0, "aptitude_score": 69.0, "cultural_fit": 74.0},
        )

        self.assertEqual(score_obj.final_decision, HiringDecisionTier.LEAN_HIRE)
        self.assertEqual(score_obj.readiness_level, ReadinessLevel.DEVELOPING_WITH_MENTORSHIP)
        self.assertGreaterEqual(score_obj.hiring_fit.net_hiring_fit_percentage, 60.0)
        self.assertLess(score_obj.hiring_fit.net_hiring_fit_percentage, 72.0)
        self.assertTrue(score_obj.safety_gate_passed)

    def test_06_inexperienced_candidate_evaluation(self):
        """Validates evaluation of junior sub-threshold candidate (Kavita Patel)."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-INEXP-03",
            candidate_name="Kavita Patel",
            target_role="Senior Systems Engineer",
            experience_years=1.2,
            ats_input={"final_ats_score": 58.0, "skill_score": 60.0, "experience_score": 55.0},
            screening_input={"overall_score": 60.0, "clarity_score": 62.0, "behavioral_score": 58.0},
            hr_input={"composite_score": 55.8, "communication_score": 58.0, "aptitude_score": 46.0, "cultural_fit": 73.0, "flags_or_penalties": ["VAGUENESS_DETECTED"]},
        )

        self.assertEqual(score_obj.final_decision, HiringDecisionTier.LEAN_NO_HIRE)
        self.assertEqual(score_obj.readiness_level, ReadinessLevel.SUB_THRESHOLD_UPSKILL)
        self.assertGreaterEqual(score_obj.hiring_fit.net_hiring_fit_percentage, 45.0)
        self.assertLess(score_obj.hiring_fit.net_hiring_fit_percentage, 60.0)

    def test_07_overqualified_candidate_leveling_advisory(self):
        """Validates overqualified candidate receives leveling upgrade advisory (Dr. Rajesh Sundaram)."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-OVER-04",
            candidate_name="Dr. Rajesh Sundaram",
            target_role="DevOps Engineer",
            experience_years=14.0,
            ats_input={"final_ats_score": 94.0, "skill_score": 96.0, "experience_score": 92.0},
            screening_input={"overall_score": 90.0, "clarity_score": 92.0, "behavioral_score": 88.0},
            hr_input={"composite_score": 92.2, "communication_score": 90.0, "aptitude_score": 94.0, "cultural_fit": 86.8},
        )

        self.assertEqual(score_obj.final_decision, HiringDecisionTier.STRONG_HIRE)
        self.assertGreaterEqual(score_obj.hiring_fit.net_hiring_fit_percentage, 90.0)
        self.assertIn("Principal / Staff", score_obj.calibrated_role_tier)

    def test_08_inconsistent_candidate_risk_discount_and_gate_fail(self):
        """Validates inconsistent candidate suffers risk discount and gate failure (Tarun Khanna)."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-INCON-05",
            candidate_name="Tarun Khanna",
            target_role="Senior Backend Lead",
            experience_years=6.0,
            ats_input={"final_ats_score": 65.0, "skill_score": 68.0, "experience_score": 62.0},
            screening_input={"overall_score": 55.0, "clarity_score": 60.0, "behavioral_score": 50.0},
            hr_input={
                "composite_score": 40.1,
                "communication_score": 52.0,
                "aptitude_score": 35.0,
                "cultural_fit": 40.0,
                "flags_or_penalties": ["CRITICAL_CONTRADICTION", "BLAME_DEFLECTION"],
            },
        )

        self.assertEqual(score_obj.final_decision, HiringDecisionTier.NO_HIRE)
        self.assertEqual(score_obj.readiness_level, ReadinessLevel.OPERATIONAL_RISK_REJECT)
        self.assertFalse(score_obj.safety_gate_passed)
        self.assertGreater(score_obj.hiring_fit.risk_and_integrity_discount, 5.0)
        self.assertGreater(len(score_obj.gate_failure_reasons), 0)

    def test_09_missing_round_safety_gating(self):
        """Validates that omitting a required round triggers safety gate failure."""
        ats_inp = self.engine.build_ats_round_input(85.0)
        hr_inp = self.engine.build_hr_round_input(88.0)

        # Evaluate without screening round
        inputs = {RoundType.ATS_RESUME: ats_inp, RoundType.HR_INTERVIEW: hr_inp}
        profile = self.weight_system.get_profile(RoleFamily.TECHNICAL_ENGINEERING)
        contributions, comp, passed, reasons = self.calculator.calculate_round_contributions(inputs, profile)

        self.assertFalse(passed)
        self.assertIn("Missing mandatory evaluation round", reasons[0])

    def test_10_serialization_and_dossier_formatting(self):
        """Validates ATS JSON export and Recruiter Markdown debrief formatting."""
        score_obj = self.engine.evaluate_candidate(
            candidate_id="SIM-CONF-01",
            candidate_name="Aditi Rao",
            target_role="Senior Cloud Platform Architect",
            experience_years=7.5,
            ats_input=88.0,
            screening_input=85.0,
            hr_input=90.3,
        )

        # JSON verification
        json_str = self.formatter.to_ats_json(score_obj)
        data = json.loads(json_str)
        self.assertEqual(data["candidate_id"], "SIM-CONF-01")
        self.assertEqual(data["final_decision"], "STRONG_HIRE")
        self.assertIn("round_contributions", data)

        # Markdown verification
        md_str = self.formatter.to_recruiter_markdown(score_obj)
        self.assertIn("# Unified Hiring Intelligence Report: Aditi Rao", md_str)
        self.assertIn("Cross-Round Scoring Breakdown", md_str)
        self.assertIn("Multi-Dimensional Hiring Fit Analytics", md_str)
        self.assertIn("Safety Gating & Audit Trail", md_str)


if __name__ == "__main__":
    unittest.main()
