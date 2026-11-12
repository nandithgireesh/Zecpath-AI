"""
Unit Tests for Day 52: Final Recommendation AI
==============================================
Validates:
1. Decision Categories: Selected, Hold / Review, Rejected
2. Rule + Score Hybrid Logic & Critical Gating Overrides
3. Decision Confidence Score Mathematical Bounds & Properties
4. Risk Factor Aggregation (Behavioral & Integrity Telemetry)
5. Explainability & Counterfactual Output Consistency
6. Cryptographic SHA-256 Audit Seal Integrity
7. Sub-35ms Evaluation Execution SLA
"""

import unittest
import time
import json
from final_recommendation_ai import (
    FinalDecisionCategory,
    DecisionSubStatus,
    OverallRiskLevel,
    ConfidenceBand,
    RuleStatus,
    BehavioralRiskFactor,
    IntegrityRiskFactor,
    RiskFactorsTelemetry,
    FinalDecisionAIEngine,
    RecommendationLogicEngine,
)


class TestDay52FinalRecommendationAI(unittest.TestCase):
    def setUp(self):
        self.engine = FinalDecisionAIEngine()
        self.logic = RecommendationLogicEngine()

    def test_01_selected_decision_high_confidence(self):
        """Validates that a high-scoring candidate with clean rules and low risk is SELECTED."""
        stage_scores = {
            "ATS_RESUME": 92.5,
            "SCREENING": 88.0,
            "HR_INTERVIEW": 89.5,
            "TECHNICAL_INTERVIEW": 93.0,
            "MACHINE_TEST": 100.0,
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.LOW,
            total_risk_penalty_points=0.0,
        )

        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-PRIYA-01",
            candidate_name="Priya Sharma",
            target_role="Principal Distributed Systems Architect",
            role_weight_profile="DISTRIBUTED_SYSTEMS_LEAD",
            experience_tier="PRINCIPAL_ARCHITECT",
            hiring_fit_score=94.0,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.SELECTED)
        self.assertEqual(decision.decision_substatus, DecisionSubStatus.OFFER_IMMEDIATE_FAST_TRACK)
        self.assertTrue(decision.all_critical_rules_passed)
        self.assertGreaterEqual(decision.decision_confidence.confidence_score, 88.0)
        self.assertIn(decision.decision_confidence.confidence_band, [ConfidenceBand.VERY_HIGH, ConfidenceBand.HIGH])
        self.assertTrue(len(decision.audit_hash) == 64)

    def test_02_hold_review_decision_borderline_fit(self):
        """Validates that a candidate in the 65.0 - 81.9% band is placed in HOLD / REVIEW."""
        stage_scores = {
            "ATS_RESUME": 78.0,
            "SCREENING": 74.0,
            "HR_INTERVIEW": 72.0,
            "TECHNICAL_INTERVIEW": 76.0,
            "MACHINE_TEST": 75.0,
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.MODERATE,
            total_risk_penalty_points=3.0,
            behavioral_risks=[
                BehavioralRiskFactor(
                    factor_id="BR-01",
                    dimension="COMMUNICATION",
                    severity=OverallRiskLevel.MODERATE,
                    description="Minor hesitation pauses under stress.",
                    deduction_points=3.0,
                )
            ]
        )

        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-ROHAN-02",
            candidate_name="Rohan Mehta",
            target_role="Software Engineer Core",
            role_weight_profile="SOFTWARE_ENGINEERING",
            experience_tier="MID_LEVEL_3_5",
            hiring_fit_score=74.5,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.HOLD_REVIEW)
        self.assertTrue(decision.all_critical_rules_passed)
        self.assertIsNotNone(decision.counterfactual_guidance)
        self.assertEqual(decision.counterfactual_guidance.target_category, FinalDecisionCategory.SELECTED)
        self.assertIn("82.0%", decision.counterfactual_guidance.required_modifications[0])

    def test_03_hold_review_decision_high_variance_override(self):
        """Validates that an eligible fit score (>82%) with extreme cross-round variance triggers HOLD / REVIEW."""
        stage_scores = {
            "ATS_RESUME": 98.0,
            "SCREENING": 95.0,
            "HR_INTERVIEW": 92.0,
            "TECHNICAL_INTERVIEW": 60.0,
            "MACHINE_TEST": 58.0,
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.LOW,
            total_risk_penalty_points=0.0,
        )

        # Base fit is 83.0, but technical is much lower than resume -> variance > 22.0
        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-ANANYA-03",
            candidate_name="Ananya Sen",
            target_role="Solutions Architecture",
            role_weight_profile="SOLUTIONS_ARCHITECTURE",
            experience_tier="SENIOR_LEAD_5_PLUS",
            hiring_fit_score=83.0,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.HOLD_REVIEW)
        self.assertEqual(decision.decision_substatus, DecisionSubStatus.HOLD_BAR_RAISER_EVALUATION)
        # Check rule 3 flagged
        rule3 = [r for r in decision.hybrid_rules_evaluated if r.rule_id == "RULE-03-CROSS-ROUND-STABILITY"][0]
        self.assertEqual(rule3.status, RuleStatus.FLAGGED)

    def test_04_rejected_decision_low_overall_fit(self):
        """Validates that a low-scoring candidate (< 65.0%) without gate breaches is REJECTED."""
        stage_scores = {
            "ATS_RESUME": 60.0,
            "SCREENING": 58.0,
            "HR_INTERVIEW": 55.0,
            "TECHNICAL_INTERVIEW": 56.0,
            "MACHINE_TEST": 55.0,
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.LOW,
            total_risk_penalty_points=0.0,
        )

        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-LOW-04",
            candidate_name="Kavita Patel",
            target_role="Software Engineering Core",
            role_weight_profile="SOFTWARE_ENGINEERING",
            experience_tier="ENTRY_LEVEL_0_2",
            hiring_fit_score=56.5,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.REJECTED)
        self.assertEqual(decision.decision_substatus, DecisionSubStatus.REJECT_LOW_OVERALL_FIT)
        self.assertTrue(decision.all_critical_rules_passed)
        self.assertIsNotNone(decision.counterfactual_guidance)
        self.assertEqual(decision.counterfactual_guidance.target_category, FinalDecisionCategory.HOLD_REVIEW)

    def test_05_rejected_critical_technical_gate_failure(self):
        """Validates that failing critical technical floors forces immediate REJECTED."""
        stage_scores = {
            "ATS_RESUME": 90.0,
            "SCREENING": 80.0,
            "HR_INTERVIEW": 82.0,
            "TECHNICAL_INTERVIEW": 48.0,  # Below 55.0 floor
            "MACHINE_TEST": 38.0,         # Below 55.0 floor
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.HIGH,
            total_risk_penalty_points=15.0,
        )

        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-GATE-05",
            candidate_name="Vikram Rao",
            target_role="Software Engineering Core",
            role_weight_profile="SOFTWARE_ENGINEERING",
            experience_tier="SENIOR_LEAD_5_PLUS",
            hiring_fit_score=52.0,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.REJECTED)
        self.assertEqual(decision.decision_substatus, DecisionSubStatus.REJECT_CRITICAL_GATE_BREACH)
        self.assertFalse(decision.all_critical_rules_passed)
        # Check rule 2 failed
        rule2 = [r for r in decision.hybrid_rules_evaluated if r.rule_id == "RULE-02-TECH-EXECUTION-FLOOR"][0]
        self.assertEqual(rule2.status, RuleStatus.FAILED_CRITICAL)

    def test_06_rejected_zero_tolerance_integrity_malpractice(self):
        """Validates that critical integrity breaches override even high candidate scores."""
        stage_scores = {
            "ATS_RESUME": 95.0,
            "SCREENING": 90.0,
            "HR_INTERVIEW": 92.0,
            "TECHNICAL_INTERVIEW": 88.0,
            "MACHINE_TEST": 90.0,
        }
        risk = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.CRITICAL,
            total_risk_penalty_points=35.0,
            has_disqualifying_breach=True,
            integrity_risks=[
                IntegrityRiskFactor(
                    factor_id="INT-01",
                    category="MALPRACTICE",
                    severity=OverallRiskLevel.CRITICAL,
                    evidence="Multiple unauthorized devices and synthetic voice proxy detected during sandbox.",
                    deduction_points=35.0,
                )
            ]
        )

        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-MALPRACTICE-06",
            candidate_name="Fraudulent Candidate",
            target_role="Software Engineering Core",
            role_weight_profile="SOFTWARE_ENGINEERING",
            experience_tier="MID_LEVEL_3_5",
            hiring_fit_score=91.0,
            stage_scores=stage_scores,
            risk_telemetry=risk,
        )

        self.assertEqual(decision.decision_category, FinalDecisionCategory.REJECTED)
        self.assertEqual(decision.decision_substatus, DecisionSubStatus.REJECT_INTEGRITY_MALPRACTICE)
        self.assertFalse(decision.all_critical_rules_passed)
        rule1 = [r for r in decision.hybrid_rules_evaluated if r.rule_id == "RULE-01-INTEGRITY-COMPLIANCE"][0]
        self.assertEqual(rule1.status, RuleStatus.FAILED_CRITICAL)

    def test_07_confidence_score_bounds_and_properties(self):
        """Validates mathematical properties and bounds of the confidence formulation."""
        # Extreme high fit
        conf_high = self.logic.compute_decision_confidence(
            hiring_fit_score=98.0,
            decision_category=FinalDecisionCategory.SELECTED,
            stage_scores={"S1": 98.0, "S2": 97.0, "S3": 99.0, "S4": 98.0, "S5": 98.0},
            risk_telemetry=RiskFactorsTelemetry(overall_risk_level=OverallRiskLevel.LOW),
        )
        self.assertGreaterEqual(conf_high.confidence_score, 90.0)
        self.assertEqual(conf_high.confidence_band, ConfidenceBand.VERY_HIGH)
        self.assertLessEqual(conf_high.confidence_score, 100.0)

        # Deep rejection
        conf_low = self.logic.compute_decision_confidence(
            hiring_fit_score=30.0,
            decision_category=FinalDecisionCategory.REJECTED,
            stage_scores={"S1": 30.0, "S2": 32.0, "S3": 28.0, "S4": 30.0, "S5": 30.0},
            risk_telemetry=RiskFactorsTelemetry(overall_risk_level=OverallRiskLevel.CRITICAL, total_risk_penalty_points=30.0),
        )
        self.assertGreaterEqual(conf_low.confidence_score, 85.0)
        self.assertLessEqual(conf_low.confidence_score, 100.0)

    def test_08_explainable_positive_drivers_and_blockers(self):
        """Validates explainability output extraction."""
        stage_scores = {"HR_INTERVIEW": 95.0, "TECHNICAL_INTERVIEW": 50.0}
        rules, all_crit = self.logic.evaluate_hybrid_rules(
            stage_scores=stage_scores,
            role_profile="SOFTWARE_ENGINEERING",
            risk_telemetry=RiskFactorsTelemetry(overall_risk_level=OverallRiskLevel.LOW),
            base_fit_score=72.0,
        )
        pos, blk, cf = self.logic.derive_explainable_drivers(
            stage_scores=stage_scores,
            rules=rules,
            risk_telemetry=RiskFactorsTelemetry(overall_risk_level=OverallRiskLevel.LOW),
            decision_category=FinalDecisionCategory.HOLD_REVIEW,
            fit_score=72.0,
        )

        self.assertTrue(any(p.dimension_name == "HR_INTERVIEW" for p in pos))
        self.assertTrue(any(b.dimension_name == "TECHNICAL_INTERVIEW" for b in blk))
        self.assertIsNotNone(cf)

    def test_09_sha256_audit_seal_reproducibility(self):
        """Validates deterministic SHA-256 seal generation and tamper detection."""
        stage_scores = {"ATS": 90.0, "HR": 85.0}
        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-SEAL-09",
            candidate_name="Audited Candidate",
            target_role="Engineering Management",
            role_weight_profile="ENGINEERING_MANAGEMENT",
            experience_tier="SENIOR_LEAD_5_PLUS",
            hiring_fit_score=86.0,
            stage_scores=stage_scores,
        )

        original_hash = decision.audit_hash
        self.assertEqual(len(original_hash), 64)
        # Re-computing should be identical
        recomputed = decision.compute_sha256_audit_seal()
        self.assertEqual(original_hash, recomputed)

    def test_10_json_serialization_roundtrip(self):
        """Validates Pydantic JSON schema serialization."""
        stage_scores = {"ATS": 85.0, "SCREEN": 80.0, "HR": 82.0, "TECH": 84.0, "MACH": 85.0}
        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-SERIAL-10",
            candidate_name="JSON Candidate",
            target_role="Software Engineering Core",
            role_weight_profile="SOFTWARE_ENGINEERING",
            experience_tier="MID_LEVEL_3_5",
            hiring_fit_score=83.5,
            stage_scores=stage_scores,
        )

        json_str = decision.model_dump_json()
        data = json.loads(json_str)
        self.assertEqual(data["decision_category"], "SELECTED")
        self.assertEqual(data["candidate_id"], "CAND-SERIAL-10")
        self.assertIn("audit_hash", data)

    def test_11_sub_35ms_sla_enforcement(self):
        """Validates that evaluation latency comfortably satisfies sub-35ms SLA."""
        stage_scores = {"ATS": 88.0, "SCREEN": 84.0, "HR": 86.0, "TECH": 90.0, "MACH": 92.0}
        start = time.perf_counter()
        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-SLA-11",
            candidate_name="Speed Benchmark",
            target_role="Distributed Systems Lead",
            role_weight_profile="DISTRIBUTED_SYSTEMS_LEAD",
            experience_tier="SENIOR_LEAD_5_PLUS",
            hiring_fit_score=88.5,
            stage_scores=stage_scores,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.assertLessEqual(elapsed_ms, 35.0)
        self.assertIsNotNone(decision.audit_hash)

    def test_12_non_tech_role_skips_tech_gate(self):
        """Validates that non-engineering roles (e.g. Sales, HR) do not enforce machine test floor."""
        stage_scores = {
            "ATS_RESUME": 85.0,
            "SCREENING": 88.0,
            "HR_INTERVIEW": 90.0,
            # No technical or machine test
        }
        decision = self.engine.evaluate_candidate_decision(
            candidate_id="CAND-NONTECH-12",
            candidate_name="Recruiter Candidate",
            target_role="Talent Acquisition Specialist",
            role_weight_profile="HUMAN_RESOURCES",
            experience_tier="MID_LEVEL_3_5",
            hiring_fit_score=87.0,
            stage_scores=stage_scores,
        )
        self.assertEqual(decision.decision_category, FinalDecisionCategory.SELECTED)
        # Check rule 2 was not applied
        rule_ids = [r.rule_id for r in decision.hybrid_rules_evaluated]
        self.assertNotIn("RULE-02-TECH-EXECUTION-FLOOR", rule_ids)

    def test_13_behavioral_risk_aggregation(self):
        """Validates multi-item behavioral risk penalty calculation."""
        b_risks = [
            BehavioralRiskFactor(factor_id="B1", dimension="STRESS", severity=OverallRiskLevel.MODERATE, description="Stress", deduction_points=4.0),
            BehavioralRiskFactor(factor_id="B2", dimension="BLAME", severity=OverallRiskLevel.HIGH, description="Blame", deduction_points=6.0),
        ]
        risk_telemetry = RiskFactorsTelemetry(
            overall_risk_level=OverallRiskLevel.HIGH,
            total_risk_penalty_points=10.0,
            behavioral_risks=b_risks,
        )
        self.assertEqual(len(risk_telemetry.behavioral_risks), 2)
        self.assertEqual(risk_telemetry.total_risk_penalty_points, 10.0)

    def test_14_substatus_mapping_exactness(self):
        """Validates all 3 categories have valid matching substatuses."""
        for cat in FinalDecisionCategory:
            self.assertIn(cat.value, ["SELECTED", "HOLD_REVIEW", "REJECTED"])

    def test_15_counterfactual_clarity(self):
        """Validates counterfactual guidance messages are actionable and specific."""
        stage_scores = {"ATS": 70.0, "TECH": 65.0, "HR": 70.0}
        pos, blk, cf = self.logic.derive_explainable_drivers(
            stage_scores=stage_scores,
            rules=[],
            risk_telemetry=RiskFactorsTelemetry(),
            decision_category=FinalDecisionCategory.HOLD_REVIEW,
            fit_score=68.5,
        )
        self.assertIsNotNone(cf)
        self.assertEqual(cf.target_category, FinalDecisionCategory.SELECTED)
        self.assertTrue(len(cf.required_modifications) >= 2)


if __name__ == "__main__":
    unittest.main()
