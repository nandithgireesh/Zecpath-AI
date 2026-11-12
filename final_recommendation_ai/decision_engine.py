"""
Day 52: Final Recommendation AI - Decision Engine (Deliverable 1)
================================================================
Master orchestrator executing the automated hiring decision engine pipeline:
- Hybrid rule + score mediation
- Decision confidence calculation
- Behavioral & integrity risk factor synthesis
- Explainability & counterfactual generation
- Tamper-evident SHA-256 cryptographic sealing
- Sub-35ms evaluation latency SLA
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

from final_recommendation_ai.models import (
    FinalDecisionCategory,
    DecisionSubStatus,
    OverallRiskLevel,
    ConfidenceBand,
    RiskFactorsTelemetry,
    BehavioralRiskFactor,
    IntegrityRiskFactor,
    EvaluatedRule,
    DecisionConfidenceTelemetry,
    ExplainableDriver,
    CounterfactualGuidance,
    CandidateDecisionOutput,
)
from final_recommendation_ai.recommendation_logic import RecommendationLogicEngine


class FinalDecisionAIEngine:
    """
    Enterprise-grade Decision AI Engine executing hybrid rule-score arbitration,
    decision confidence estimation, risk analysis, and explainable dossier generation.
    """

    def __init__(self):
        self.logic_engine = RecommendationLogicEngine()
        self.engine_version = "1.0.0-PROD"
        self._warmup()

    def _warmup(self) -> None:
        """Pre-warms JIT and runtime memory cache to guarantee low latency."""
        try:
            dummy_scores = {"ATS": 85.0, "SCREEN": 85.0, "HR": 85.0, "TECH": 85.0, "MACH": 85.0}
            self.logic_engine.evaluate_rules(85.0, dummy_scores, None)
        except Exception:
            pass

    def evaluate_candidate_decision(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        role_weight_profile: str,
        experience_tier: str,
        hiring_fit_score: float,
        stage_scores: Dict[str, float],
        risk_telemetry: Optional[RiskFactorsTelemetry] = None,
    ) -> CandidateDecisionOutput:
        """
        Executes end-to-end automated hiring outcome recommendation.
        Returns sealed CandidateDecisionOutput object.
        """
        start_time = time.perf_counter()

        if risk_telemetry is None:
            risk_telemetry = RiskFactorsTelemetry(
                overall_risk_level=OverallRiskLevel.LOW,
                total_risk_penalty_points=0.0,
            )

        # 1. Evaluate Hybrid Deterministic Rules
        rules, all_critical_passed = self.logic_engine.evaluate_hybrid_rules(
            stage_scores=stage_scores,
            role_profile=target_role,
            risk_telemetry=risk_telemetry,
            base_fit_score=hiring_fit_score,
        )

        # 2. Resolve Decision Category & Sub-Status
        category, substatus = self.logic_engine.resolve_decision_category(
            hiring_fit_score=hiring_fit_score,
            rules=rules,
            all_critical_passed=all_critical_passed,
            risk_telemetry=risk_telemetry,
        )

        # 3. Compute Quantified Decision Confidence
        confidence_telemetry = self.logic_engine.compute_decision_confidence(
            hiring_fit_score=hiring_fit_score,
            decision_category=category,
            stage_scores=stage_scores,
            risk_telemetry=risk_telemetry,
        )

        # 4. Generate Explainable Drivers & Counterfactual Guidance
        positives, blockers, counterfactual = self.logic_engine.derive_explainable_drivers(
            stage_scores=stage_scores,
            rules=rules,
            risk_telemetry=risk_telemetry,
            decision_category=category,
            fit_score=hiring_fit_score,
        )

        # 5. Synthesize Executive Narrative Rationale
        executive_rationale = self._synthesize_executive_rationale(
            candidate_name=candidate_name,
            target_role=target_role,
            category=category,
            substatus=substatus,
            hiring_fit_score=hiring_fit_score,
            confidence_telemetry=confidence_telemetry,
            all_critical_passed=all_critical_passed,
            risk_telemetry=risk_telemetry,
        )

        # 6. Construct Candidate Decision Output Object
        decision_output = CandidateDecisionOutput(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            role_weight_profile=role_weight_profile,
            experience_tier=experience_tier,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            engine_version=self.engine_version,
            decision_category=category,
            decision_substatus=substatus,
            hiring_fit_score=round(hiring_fit_score, 2),
            decision_confidence=confidence_telemetry,
            stage_scores_summary=stage_scores,
            hybrid_rules_evaluated=rules,
            all_critical_rules_passed=all_critical_passed,
            risk_factors=risk_telemetry,
            primary_positive_drivers=positives,
            critical_risk_blockers=blockers,
            counterfactual_guidance=counterfactual,
            executive_decision_rationale=executive_rationale,
        )

        # 7. Finalize Cryptographic Audit Seal
        decision_output.finalize_and_seal()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        decision_output.evaluation_latency_ms = round(elapsed_ms, 3)

        return decision_output

    def _synthesize_executive_rationale(
        self,
        candidate_name: str,
        target_role: str,
        category: FinalDecisionCategory,
        substatus: DecisionSubStatus,
        hiring_fit_score: float,
        confidence_telemetry: DecisionConfidenceTelemetry,
        all_critical_passed: bool,
        risk_telemetry: RiskFactorsTelemetry,
    ) -> str:
        """Synthesizes human-readable executive briefing for hiring committees."""
        if category == FinalDecisionCategory.SELECTED:
            return (
                f"Candidate {candidate_name} is decisively recommended for [{category.value}] "
                f"({substatus.value}) for the position of {target_role}. With a calibrated hiring fit "
                f"of {hiring_fit_score:.1f}% and algorithmic confidence of {confidence_telemetry.confidence_score:.1f}% "
                f"({confidence_telemetry.confidence_band.value}), all deterministic quality and technical floors "
                f"were comprehensively cleared. Composite risk rating is {risk_telemetry.overall_risk_level.value}."
            )
        elif category == FinalDecisionCategory.HOLD_REVIEW:
            return (
                f"Candidate {candidate_name} has been placed under [{category.value}] ({substatus.value}) "
                f"for the position of {target_role}. While demonstrating an eligible hiring fit of "
                f"{hiring_fit_score:.1f}% (Confidence: {confidence_telemetry.confidence_score:.1f}%), "
                f"cross-round variance or behavioral indicators warrant formal Bar Raiser or Hiring Manager review "
                f"prior to extending an offer. Composite risk rating: {risk_telemetry.overall_risk_level.value}."
            )
        else: # REJECTED
            reason_clause = "disqualifying critical rule failures" if not all_critical_passed else "sub-threshold overall fit"
            return (
                f"Candidate {candidate_name} is marked as [{category.value}] ({substatus.value}) "
                f"for the position of {target_role} due to {reason_clause}. Calibrated hiring fit stands at "
                f"{hiring_fit_score:.1f}% with decision certainty of {confidence_telemetry.confidence_score:.1f}% "
                f"({confidence_telemetry.confidence_band.value}). Observed risk level: {risk_telemetry.overall_risk_level.value}."
            )
