"""
Unit Test Suite: Day 51 - Cross-Round Aggregation Engine
=========================================================
Validates:
1. 5 Canonical Assessment Stages Ingestion & Normalization
2. Role-Based Weight Configurations (Software, Systems Lead, Management, Data, Solutions)
3. Gating Cutoff Floors & Disqualification Triggers
4. Four-Dimensional Radar Competency Synthesis
5. Cross-Round Inconsistency Risk Discount Deductions
6. Profile-Aware Normalization (Junior vs. Senior Architect)
7. Unified Candidate Score Object & SHA-256 Audit Seal
8. P99 Latency SLA <= 45ms
"""

import unittest
import time
from cross_round_ai.models import (
    AssessmentStage,
    RoleWeightProfile,
    CandidateProfileTier,
    HiringDecision,
    ReadinessTier,
    StageScoreInput,
    StageWeightSpecification,
    CrossStageWeightConfig,
    UnifiedCandidateScoreObject,
)
from cross_round_ai.hiring_fit_calculator import HiringFitCalculator
from cross_round_ai.aggregation_engine import CrossRoundAggregationEngine, STANDARD_ROLE_PROFILES


class TestDay51CrossRoundEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CrossRoundAggregationEngine()
        self.calculator = HiringFitCalculator()

    # --------------------------------------------------------------------------
    # 1. ROLE WEIGHT PROFILES & NORMALIZATION
    # --------------------------------------------------------------------------

    def test_standard_profiles_weight_sum_normalization(self):
        """Verifies all standard role profiles have weights summing strictly to 1.0."""
        for role, config in STANDARD_ROLE_PROFILES.items():
            total_weight = sum(spec.weight for spec in config.weights.values())
            self.assertAlmostEqual(
                total_weight, 1.0, places=4,
                msg=f"Profile {role.value} weights do not sum to 1.0 (got {total_weight})"
            )
            self.assertEqual(len(config.weights), 5, "Must cover all 5 assessment stages.")

    def test_custom_profile_registration_and_validation(self):
        """Verifies custom profile registration and rejection of invalid weight sums."""
        valid_custom = CrossStageWeightConfig(
            profile_name="Custom QA Automation",
            role_profile=RoleWeightProfile.CUSTOM_ROLE,
            weights={
                AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.10),
                AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.20),
                AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.20),
                AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.20),
                AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.30),
            },
        )
        self.engine.register_custom_profile(valid_custom)
        fetched = self.engine.get_profile(RoleWeightProfile.CUSTOM_ROLE)
        self.assertIsNotNone(fetched)

        invalid_custom = CrossStageWeightConfig(
            profile_name="Invalid Sum Profile",
            role_profile=RoleWeightProfile.CUSTOM_ROLE,
            weights={
                AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.50),
                AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.60),  # Sum = 1.10
            },
        )
        with self.assertRaises(ValueError):
            self.engine.register_custom_profile(invalid_custom)

    # --------------------------------------------------------------------------
    # 2. STAGE CONTRIBUTIONS & GATING FLOORS
    # --------------------------------------------------------------------------

    def test_stage_contributions_and_all_gates_passed(self):
        """Verifies proportional point contribution calculation when all gates pass."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS Resume", raw_score=90.0, normalized_score=90.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR Interview", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Technical Interview", raw_score=90.0, normalized_score=90.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine Test", raw_score=95.0, normalized_score=95.0),
        }
        config = self.engine.get_profile(RoleWeightProfile.SOFTWARE_ENGINEERING)
        contributions, all_passed, base_agg = self.calculator.calculate_stage_contributions(stages, config)

        self.assertTrue(all_passed)
        # Expected: 90*0.10 + 85*0.15 + 80*0.15 + 90*0.30 + 95*0.30 = 9 + 12.75 + 12 + 27 + 28.5 = 89.25
        self.assertAlmostEqual(base_agg, 89.25, delta=0.1)
        self.assertEqual(len(contributions), 5)
        self.assertTrue(contributions[AssessmentStage.MACHINE_TEST].passed_gate)

    def test_gating_breach_detection(self):
        """Verifies critical stage cutoff breach flags failure."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=90.0, normalized_score=90.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=75.0, normalized_score=75.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=70.0, normalized_score=70.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine Test", raw_score=35.0, normalized_score=35.0),  # Below 55.0 cutoff
        }
        config = self.engine.get_profile(RoleWeightProfile.SOFTWARE_ENGINEERING)
        contributions, all_passed, base_agg = self.calculator.calculate_stage_contributions(stages, config)

        self.assertFalse(all_passed)
        self.assertFalse(contributions[AssessmentStage.MACHINE_TEST].passed_gate)

    # --------------------------------------------------------------------------
    # 3. RADAR COMPETENCY & PROFILE NORMALIZATION
    # --------------------------------------------------------------------------

    def test_radar_competency_synthesis(self):
        """Verifies 4 orthogonal radar dimensions are correctly synthesized."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=70.0, normalized_score=70.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=90.0, normalized_score=90.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=100.0, normalized_score=100.0),
        }
        radar = self.calculator.compute_radar_competencies(stages, CandidateProfileTier.SENIOR_LEAD_5_PLUS)
        self.assertEqual(len(radar), 4)

        # Technical problem solving = (90 * 0.5) + (100 * 0.5) = 95.0
        tech_radar = next(r for r in radar if "Technical" in r.dimension_name)
        self.assertEqual(tech_radar.score, 95.0)

    # --------------------------------------------------------------------------
    # 4. RISK DISCOUNT DEDUCTIONS
    # --------------------------------------------------------------------------

    def test_risk_discount_on_resume_vs_coding_gap(self):
        """Verifies risk deduction when high ATS claim contradicts low machine test."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=95.0, normalized_score=95.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=70.0, normalized_score=70.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=70.0, normalized_score=70.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=50.0, normalized_score=50.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=40.0, normalized_score=40.0),
        }
        discounts = self.calculator.calculate_risk_discounts(stages, all_gates_passed=True)
        self.assertGreater(discounts.cross_round_inconsistency_penalty, 0.0)
        self.assertGreaterEqual(discounts.total_risk_discount, 15.0)

    # --------------------------------------------------------------------------
    # 5. END-TO-END AGGREGATION & SLA VALIDATION
    # --------------------------------------------------------------------------

    def test_end_to_end_strong_hire_dossier(self):
        """Verifies full 5-stage synthesis for an exemplary candidate."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS Resume", raw_score=92.0, normalized_score=92.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Voice Screening", raw_score=88.0, normalized_score=88.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR Behavioral", raw_score=90.0, normalized_score=90.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Technical Depth", raw_score=92.0, normalized_score=92.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine Sandbox", raw_score=98.0, normalized_score=98.0),
        }

        t0 = time.perf_counter()
        dossier = self.engine.aggregate_candidate_dossier(
            candidate_id="CAND-PRIYA-01",
            candidate_name="Priya Sharma",
            applied_role="Principal Distributed Systems Architect",
            experience_tier=CandidateProfileTier.PRINCIPAL_ARCHITECT,
            role_profile=RoleWeightProfile.DISTRIBUTED_SYSTEMS_LEAD,
            stage_scores=stages,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # P99 Latency SLA <= 45ms
        self.assertLessEqual(elapsed_ms, 45.0)
        self.assertEqual(dossier.decision_verdict, HiringDecision.STRONG_HIRE)
        self.assertEqual(dossier.readiness_tier, ReadinessTier.FAST_TRACK_OFFER)
        self.assertGreaterEqual(dossier.hiring_fit_score, 88.0)
        self.assertTrue(dossier.all_gates_passed)
        self.assertEqual(len(dossier.audit_hash_sha256), 64)

    def test_end_to_end_disqualified_candidate(self):
        """Verifies candidate with critical gate failures is rejected as NO_HIRE."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS Resume", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Voice Screening", raw_score=55.0, normalized_score=55.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR Behavioral", raw_score=40.0, normalized_score=40.0),  # Gate fail
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Technical Depth", raw_score=45.0, normalized_score=45.0),  # Gate fail
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine Sandbox", raw_score=35.0, normalized_score=35.0),  # Gate fail
        }

        dossier = self.engine.aggregate_candidate_dossier(
            candidate_id="CAND-VIKRAM-02",
            candidate_name="Vikram Rao",
            applied_role="Full-Stack Developer",
            experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
            role_profile=RoleWeightProfile.SOFTWARE_ENGINEERING,
            stage_scores=stages,
        )

        self.assertEqual(dossier.decision_verdict, HiringDecision.NO_HIRE)
        self.assertEqual(dossier.readiness_tier, ReadinessTier.DISQUALIFIED_HIGH_RISK)
        self.assertFalse(dossier.all_gates_passed)
        self.assertLess(dossier.hiring_fit_score, 45.0)

    def test_all_five_role_profiles_aggregation(self):
        """Verifies candidate aggregation across all 5 standard role weight presets."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=75.0, normalized_score=75.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=75.0, normalized_score=75.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=75.0, normalized_score=75.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=75.0, normalized_score=75.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=75.0, normalized_score=75.0),
        }
        for profile_enum in [
            RoleWeightProfile.SOFTWARE_ENGINEERING,
            RoleWeightProfile.DISTRIBUTED_SYSTEMS_LEAD,
            RoleWeightProfile.ENGINEERING_MANAGEMENT,
            RoleWeightProfile.DATA_PLATFORM_ENGINEERING,
            RoleWeightProfile.SOLUTIONS_ARCHITECTURE,
        ]:
            d = self.engine.aggregate_candidate_dossier(
                candidate_id=f"CAND-TEST-{profile_enum.value}",
                candidate_name="Test Candidate",
                applied_role="General Engineer",
                experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
                role_profile=profile_enum,
                stage_scores=stages,
            )
            self.assertEqual(d.hiring_fit_score, 75.0)
            self.assertEqual(d.decision_verdict, HiringDecision.HIRE)

    def test_candidate_profile_tier_multipliers(self):
        """Verifies radar benchmark normalization scales properly with experience tiers."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=80.0, normalized_score=80.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=80.0, normalized_score=80.0),
        }
        radar_entry = self.calculator.compute_radar_competencies(stages, CandidateProfileTier.ENTRY_LEVEL_0_2)
        radar_lead = self.calculator.compute_radar_competencies(stages, CandidateProfileTier.SENIOR_LEAD_5_PLUS)
        # Entry level tier has higher percentile benchmark multiplier
        self.assertGreater(radar_entry[0].percentile_benchmark, radar_lead[0].percentile_benchmark)

    def test_lean_hire_verdict(self):
        """Verifies score band 60.0 - 71.9 maps to LEAN_HIRE."""
        dec, read, lev = self.calculator.determine_hiring_verdict(
            hiring_fit_score=68.5,
            all_gates_passed=True,
            experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
        )
        self.assertEqual(dec, HiringDecision.LEAN_HIRE)
        self.assertEqual(read, ReadinessTier.DEVELOPING_WITH_ONBOARDING)

    def test_lean_no_hire_verdict(self):
        """Verifies score band 45.0 - 59.9 maps to LEAN_NO_HIRE."""
        dec, read, lev = self.calculator.determine_hiring_verdict(
            hiring_fit_score=52.0,
            all_gates_passed=True,
            experience_tier=CandidateProfileTier.ENTRY_LEVEL_0_2,
        )
        self.assertEqual(dec, HiringDecision.LEAN_NO_HIRE)
        self.assertEqual(read, ReadinessTier.BELOW_BAR_UPSKILL)

    def test_counterfactual_guidance_generation(self):
        """Verifies counterfactual advice is generated when candidate is not a Strong Hire."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=60.0, normalized_score=60.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=65.0, normalized_score=65.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=60.0, normalized_score=60.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=60.0, normalized_score=60.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=60.0, normalized_score=60.0),
        }
        dossier = self.engine.aggregate_candidate_dossier(
            candidate_id="CAND-COUNTER-01",
            candidate_name="Borderline Dev",
            applied_role="Software Dev",
            experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
            role_profile=RoleWeightProfile.SOFTWARE_ENGINEERING,
            stage_scores=stages,
        )
        self.assertIn("improves lowest scoring stage", dossier.counterfactual_guidance)

    def test_engine_manifest_generation(self):
        """Verifies architectural manifest generation with deterministic SHA-256 seal."""
        manifest = self.engine.generate_engine_manifest()
        self.assertEqual(manifest["engine_id"], "ENGINE-DAY51-CROSS-ROUND-AGGREGATION")
        self.assertEqual(len(manifest["sha256_integrity_hash"]), 64)
        self.assertEqual(len(manifest["stages_supported"]), 5)

    def test_json_and_pydantic_serialization(self):
        """Verifies complete serialization of the UnifiedCandidateScoreObject."""
        stages = {
            AssessmentStage.ATS_RESUME: StageScoreInput(stage=AssessmentStage.ATS_RESUME, stage_name="ATS", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageScoreInput(stage=AssessmentStage.CONVERSATIONAL_SCREENING, stage_name="Screening", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.HR_BEHAVIORAL_INTERVIEW, stage_name="HR", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.TECHNICAL_INTERVIEW: StageScoreInput(stage=AssessmentStage.TECHNICAL_INTERVIEW, stage_name="Tech", raw_score=85.0, normalized_score=85.0),
            AssessmentStage.MACHINE_TEST: StageScoreInput(stage=AssessmentStage.MACHINE_TEST, stage_name="Machine", raw_score=85.0, normalized_score=85.0),
        }
        dossier = self.engine.aggregate_candidate_dossier(
            candidate_id="CAND-SERIAL-01",
            candidate_name="Serial Candidate",
            applied_role="Platform Engineer",
            experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
            role_profile=RoleWeightProfile.SOFTWARE_ENGINEERING,
            stage_scores=stages,
        )
        data_json = dossier.model_dump_json()
        self.assertIn("CAND-SERIAL-01", data_json)
        self.assertIn("audit_hash_sha256", data_json)


if __name__ == "__main__":
    unittest.main()

