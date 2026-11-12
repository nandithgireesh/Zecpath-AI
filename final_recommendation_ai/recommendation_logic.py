"""
Day 52: Final Recommendation AI - Recommendation Logic & Hybrid Evaluator (Deliverable 2)
========================================================================================
Implements the hybrid rule + score resolution model, decision confidence mathematical
formulation, multi-pillar risk aggregation, and counterfactual prescription.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
from final_recommendation_ai.models import (
    FinalDecisionCategory,
    DecisionSubStatus,
    OverallRiskLevel,
    ConfidenceBand,
    RuleStatus,
    BehavioralRiskFactor,
    IntegrityRiskFactor,
    RiskFactorsTelemetry,
    EvaluatedRule,
    DecisionConfidenceTelemetry,
    ExplainableDriver,
    CounterfactualGuidance,
)


class RecommendationLogicEngine:
    """
    Hybrid decision engine resolving deterministic policy rules with calibrated
    multi-stage score thresholds, computing mathematical decision confidence.
    """

    # Decision Score Thresholds
    SCORE_THRESHOLD_SELECTED = 82.0
    SCORE_THRESHOLD_HOLD_FLOOR = 65.0

    # Critical Technical Floor Thresholds for Engineering Archetypes
    CRITICAL_TECH_FLOOR = 55.0
    CRITICAL_INTEGRITY_MAX_PENALTY = 25.0
    MAX_PERMISSIBLE_VARIANCE_STD = 16.0

    def __init__(self):
        pass

    # =========================================================================
    # 1. HYBRID RULE EVALUATION
    # =========================================================================

    def evaluate_hybrid_rules(
        self,
        stage_scores: Dict[str, float],
        role_profile: str,
        risk_telemetry: RiskFactorsTelemetry,
        base_fit_score: float,
    ) -> Tuple[List[EvaluatedRule], bool]:
        """
        Evaluates deterministic gating and integrity policies alongside scores.
        Returns: (List of evaluated rules, all_critical_passed boolean).
        """
        rules: List[EvaluatedRule] = []
        all_critical_passed = True

        # Rule 1: Zero-Tolerance Integrity & Malpractice Check
        integrity_penalties = sum(r.deduction_points for r in risk_telemetry.integrity_risks)
        rule_integrity_passed = (
            not risk_telemetry.has_disqualifying_breach
            and integrity_penalties < self.CRITICAL_INTEGRITY_MAX_PENALTY
        )
        if not rule_integrity_passed:
            all_critical_passed = False
            status = RuleStatus.FAILED_CRITICAL
            reason = f"Integrity violations detected: {integrity_penalties:.1f} penalty pts or disqualifying breach."
        else:
            status = RuleStatus.PASSED
            reason = f"Integrity clean: penalties ({integrity_penalties:.1f} pts) strictly below threshold."

        rules.append(
            EvaluatedRule(
                rule_id="RULE-01-INTEGRITY-COMPLIANCE",
                rule_name="Zero-Tolerance Integrity & Authentication Policy",
                is_critical_gate=True,
                status=status,
                threshold_applied=f"Integrity penalty < {self.CRITICAL_INTEGRITY_MAX_PENALTY} pts and zero critical breaches",
                observed_value=f"Penalty: {integrity_penalties:.1f} pts | Breach: {risk_telemetry.has_disqualifying_breach}",
                reasoning=reason,
            )
        )

        # Rule 2: Critical Technical Competency Floor (for Engineering Roles)
        is_tech_role = any(
            t in role_profile.upper()
            for t in ["SOFTWARE", "DISTRIBUTED", "DATA", "ENGINEERING", "DEV"]
        )
        tech_score = stage_scores.get("TECHNICAL_INTERVIEW", 100.0)
        mach_score = stage_scores.get("MACHINE_TEST", 100.0)

        if is_tech_role:
            tech_passed = tech_score >= self.CRITICAL_TECH_FLOOR and mach_score >= self.CRITICAL_TECH_FLOOR
            if not tech_passed:
                all_critical_passed = False
                status = RuleStatus.FAILED_CRITICAL
                reason = (
                    f"Core technical delivery breached minimum floor ({self.CRITICAL_TECH_FLOOR:.1f} pts). "
                    f"Tech Interview: {tech_score:.1f}, Machine Test: {mach_score:.1f}."
                )
            else:
                status = RuleStatus.PASSED
                reason = f"Technical competencies verified (Tech: {tech_score:.1f}, Sandbox: {mach_score:.1f} >= {self.CRITICAL_TECH_FLOOR:.1f})."

            rules.append(
                EvaluatedRule(
                    rule_id="RULE-02-TECH-EXECUTION-FLOOR",
                    rule_name="Minimum Practical Technical & Sandbox Floor",
                    is_critical_gate=True,
                    status=status,
                    threshold_applied=f"Technical Interview >= {self.CRITICAL_TECH_FLOOR} and Machine Test >= {self.CRITICAL_TECH_FLOOR}",
                    observed_value=f"Tech: {tech_score:.1f} | Sandbox: {mach_score:.1f}",
                    reasoning=reason,
                )
            )

        # Rule 3: Cross-Round Volatility & Variance Stability
        scores_list = list(stage_scores.values())
        if len(scores_list) > 1:
            mean_score = sum(scores_list) / len(scores_list)
            variance = sum((s - mean_score) ** 2 for s in scores_list) / len(scores_list)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        if std_dev > self.MAX_PERMISSIBLE_VARIANCE_STD:
            status = RuleStatus.FLAGGED
            reason = f"Cross-round score dispersion ({std_dev:.1f} pts) exceeds stability ceiling ({self.MAX_PERMISSIBLE_VARIANCE_STD:.1f} pts)."
        else:
            status = RuleStatus.PASSED
            reason = f"Performance consistency verified across stages (Std Dev: {std_dev:.1f} pts)."

        rules.append(
            EvaluatedRule(
                rule_id="RULE-03-CROSS-ROUND-STABILITY",
                rule_name="Cross-Round Performance Consistency & Variance Control",
                is_critical_gate=False,
                status=status,
                threshold_applied=f"Cross-stage std dev <= {self.MAX_PERMISSIBLE_VARIANCE_STD} pts",
                observed_value=f"Std Dev: {std_dev:.1f} pts",
                reasoning=reason,
            )
        )

        # Rule 4: Behavioral Composure & Cultural Alignment Floor
        hr_score = stage_scores.get("HR_INTERVIEW", 100.0)
        has_severe_behavioral = any(b.severity == OverallRiskLevel.CRITICAL for b in risk_telemetry.behavioral_risks)
        if hr_score < 45.0 or has_severe_behavioral:
            all_critical_passed = False
            status = RuleStatus.FAILED_CRITICAL
            reason = f"Behavioral score ({hr_score:.1f}) or critical behavioral flags breached cultural boundary."
        elif hr_score < 60.0 or risk_telemetry.overall_risk_level in [OverallRiskLevel.HIGH, OverallRiskLevel.MODERATE]:
            status = RuleStatus.FLAGGED
            reason = f"Behavioral or composure reservations observed (HR Score: {hr_score:.1f})."
        else:
            status = RuleStatus.PASSED
            reason = f"Behavioral and cultural requirements fulfilled (HR Score: {hr_score:.1f})."

        rules.append(
            EvaluatedRule(
                rule_id="RULE-04-BEHAVIORAL-ALIGNMENT",
                rule_name="Behavioral Composure & STAR Methodology Alignment",
                is_critical_gate=True,
                status=status,
                threshold_applied="HR Interview >= 45.0 and zero critical behavioral breaches",
                observed_value=f"HR Score: {hr_score:.1f} | Risk: {risk_telemetry.overall_risk_level.value}",
                reasoning=reason,
            )
        )

        return rules, all_critical_passed

    # =========================================================================
    # 2. HYBRID DECISION RESOLUTION
    # =========================================================================

    def resolve_decision_category(
        self,
        hiring_fit_score: float,
        rules: List[EvaluatedRule],
        all_critical_passed: bool,
        risk_telemetry: RiskFactorsTelemetry,
    ) -> Tuple[FinalDecisionCategory, DecisionSubStatus]:
        """
        Determines the final decision category (SELECTED, HOLD_REVIEW, REJECTED)
        and granular sub-status using hybrid rule-score mediation.
        """
        # 1. Critical Rule Breach -> Direct Rejection
        if not all_critical_passed:
            # Determine specific rejection reason
            if risk_telemetry.has_disqualifying_breach or any(
                r.rule_id == "RULE-01-INTEGRITY-COMPLIANCE" and r.status == RuleStatus.FAILED_CRITICAL for r in rules
            ):
                return FinalDecisionCategory.REJECTED, DecisionSubStatus.REJECT_INTEGRITY_MALPRACTICE
            
            if any(r.rule_id == "RULE-02-TECH-EXECUTION-FLOOR" and r.status == RuleStatus.FAILED_CRITICAL for r in rules):
                return FinalDecisionCategory.REJECTED, DecisionSubStatus.REJECT_CRITICAL_GATE_BREACH
            
            return FinalDecisionCategory.REJECTED, DecisionSubStatus.REJECT_CRITICAL_GATE_BREACH

        # 2. Score-Based Categorization with Rule-Mediated Downgrades
        has_flagged_rules = any(r.status == RuleStatus.FLAGGED for r in rules)

        if hiring_fit_score >= self.SCORE_THRESHOLD_SELECTED:
            if risk_telemetry.overall_risk_level == OverallRiskLevel.LOW and not has_flagged_rules:
                if hiring_fit_score >= 92.0:
                    return FinalDecisionCategory.SELECTED, DecisionSubStatus.OFFER_IMMEDIATE_FAST_TRACK
                return FinalDecisionCategory.SELECTED, DecisionSubStatus.OFFER_STANDARD
            else:
                # High score but moderate risk or flagged variance -> Downgrade to HOLD / REVIEW
                if any(r.rule_id == "RULE-03-CROSS-ROUND-STABILITY" and r.status == RuleStatus.FLAGGED for r in rules):
                    return FinalDecisionCategory.HOLD_REVIEW, DecisionSubStatus.HOLD_BAR_RAISER_EVALUATION
                return FinalDecisionCategory.HOLD_REVIEW, DecisionSubStatus.HOLD_HIRING_MANAGER_DEBRIEF

        elif hiring_fit_score >= self.SCORE_THRESHOLD_HOLD_FLOOR:
            # Moderate fit -> HOLD / REVIEW
            if risk_telemetry.overall_risk_level in [OverallRiskLevel.HIGH, OverallRiskLevel.MODERATE]:
                return FinalDecisionCategory.HOLD_REVIEW, DecisionSubStatus.HOLD_BORDERLINE_SKILL_RETEST
            return FinalDecisionCategory.HOLD_REVIEW, DecisionSubStatus.HOLD_HIRING_MANAGER_DEBRIEF

        else:
            # Sub-threshold fit (< 65.0%) -> REJECTED
            return FinalDecisionCategory.REJECTED, DecisionSubStatus.REJECT_LOW_OVERALL_FIT

    # =========================================================================
    # 3. DECISION CONFIDENCE FORMULATION
    # =========================================================================

    def compute_decision_confidence(
        self,
        hiring_fit_score: float,
        decision_category: FinalDecisionCategory,
        stage_scores: Dict[str, float],
        risk_telemetry: RiskFactorsTelemetry,
    ) -> DecisionConfidenceTelemetry:
        """
        Calculates quantified mathematical decision confidence % based on:
        - Distance from decision boundary margins
        - Cross-stage statistical variance stability
        - Telemetry completeness
        - Risk deduction drag
        """
        # 1. Boundary Distance Factor (0.0 to 100.0)
        # Distance from relevant threshold
        if decision_category == FinalDecisionCategory.SELECTED:
            dist = hiring_fit_score - self.SCORE_THRESHOLD_SELECTED
            # Closer to 82.0 has lower margin certainty, >90.0 has ~100%
            boundary_factor = min(100.0, 70.0 + (dist * 2.5))
        elif decision_category == FinalDecisionCategory.REJECTED:
            dist = self.SCORE_THRESHOLD_HOLD_FLOOR - hiring_fit_score
            # Deep rejection (<50%) has high certainty, borderline 64% has lower
            boundary_factor = min(100.0, 70.0 + (dist * 1.5))
        else: # HOLD_REVIEW
            # In the middle band, certainty is highest right in the center of the band (around 73.5)
            band_center = (self.SCORE_THRESHOLD_SELECTED + self.SCORE_THRESHOLD_HOLD_FLOOR) / 2.0
            dist_from_edge = min(
                abs(hiring_fit_score - self.SCORE_THRESHOLD_SELECTED),
                abs(hiring_fit_score - self.SCORE_THRESHOLD_HOLD_FLOOR),
            )
            boundary_factor = min(100.0, 60.0 + (dist_from_edge * 3.0))

        # 2. Signal Consistency Factor (0.0 to 100.0)
        scores = list(stage_scores.values())
        if len(scores) > 1:
            mean = sum(scores) / len(scores)
            var = sum((s - mean) ** 2 for s in scores) / len(scores)
            std = math.sqrt(var)
            consistency_factor = max(20.0, min(100.0, 100.0 - (std * 2.2)))
        else:
            std = 0.0
            consistency_factor = 70.0

        # 3. Data Completeness Factor (0.0 to 100.0)
        expected_stages = 5 # ATS, Screen, HR, Tech, Machine Test
        completeness_factor = (len(stage_scores) / expected_stages) * 100.0

        # 4. Weighted Aggregate Confidence
        raw_confidence = (
            (boundary_factor * 0.40)
            + (consistency_factor * 0.35)
            + (completeness_factor * 0.25)
        )

        # Risk Drag: High risk deductions reduce confidence in positive outcomes
        if decision_category == FinalDecisionCategory.SELECTED:
            confidence_penalty = risk_telemetry.total_risk_penalty_points * 1.2
            final_conf = max(45.0, min(99.5, raw_confidence - confidence_penalty))
        elif decision_category == FinalDecisionCategory.REJECTED:
            # In rejection, strong risk presence actually INCREASES certainty of rejection
            bonus = min(10.0, risk_telemetry.total_risk_penalty_points * 0.3)
            final_conf = max(50.0, min(99.5, raw_confidence + bonus))
        else:
            final_conf = max(40.0, min(90.0, raw_confidence))

        final_conf = round(final_conf, 1)

        # Categorize Band
        if final_conf >= 90.0:
            band = ConfidenceBand.VERY_HIGH
        elif final_conf >= 78.0:
            band = ConfidenceBand.HIGH
        elif final_conf >= 60.0:
            band = ConfidenceBand.MODERATE
        else:
            band = ConfidenceBand.LOW

        rationale = (
            f"Decision confidence computed at {final_conf}% ({band.value}). "
            f"Boundary distance factor: {boundary_factor:.1f}%, consistency factor: {consistency_factor:.1f}%, "
            f"data completeness: {completeness_factor:.1f}%."
        )

        return DecisionConfidenceTelemetry(
            confidence_score=final_conf,
            confidence_band=band,
            boundary_distance_factor=round(boundary_factor, 1),
            signal_consistency_factor=round(consistency_factor, 1),
            data_completeness_factor=round(completeness_factor, 1),
            confidence_rationale=rationale,
        )

    # =========================================================================
    # 4. EXPLAINABILITY & COUNTERFACTUAL PRESCRIPTION
    # =========================================================================

    def derive_explainable_drivers(
        self,
        stage_scores: Dict[str, float],
        rules: List[EvaluatedRule],
        risk_telemetry: RiskFactorsTelemetry,
        decision_category: FinalDecisionCategory,
        fit_score: float,
    ) -> Tuple[List[ExplainableDriver], List[ExplainableDriver], Optional[CounterfactualGuidance]]:
        """
        Generates positive drivers, risk blockers, and prescriptive counterfactual guidance.
        """
        positives: List[ExplainableDriver] = []
        blockers: List[ExplainableDriver] = []

        # Analyze Stage Contributions
        for stage, score in stage_scores.items():
            if score >= 85.0:
                positives.append(
                    ExplainableDriver(
                        driver_type="POSITIVE_STRENGTH",
                        dimension_name=stage,
                        impact_points=round(score * 0.15, 1),
                        explanation=f"Exemplary performance in {stage} ({score:.1f} pts) demonstrating high mastery.",
                    )
                )
            elif score < 60.0:
                blockers.append(
                    ExplainableDriver(
                        driver_type="RISK_BLOCKER",
                        dimension_name=stage,
                        impact_points=round((60.0 - score) * 0.25, 1),
                        explanation=f"Sub-threshold evaluation in {stage} ({score:.1f} pts) dragging overall fit.",
                    )
                )

        # Analyze Rule Blockers
        for r in rules:
            if r.status == RuleStatus.FAILED_CRITICAL:
                blockers.append(
                    ExplainableDriver(
                        driver_type="RISK_BLOCKER",
                        dimension_name=r.rule_name,
                        impact_points=15.0,
                        explanation=f"Critical rule violation: {r.reasoning}",
                    )
                )
            elif r.status == RuleStatus.FLAGGED:
                blockers.append(
                    ExplainableDriver(
                        driver_type="RISK_BLOCKER",
                        dimension_name=r.rule_name,
                        impact_points=5.0,
                        explanation=f"Operational policy warning: {r.reasoning}",
                    )
                )

        # Formulate Counterfactual Guidance
        counterfactual: Optional[CounterfactualGuidance] = None

        if decision_category == FinalDecisionCategory.HOLD_REVIEW:
            needed = round(self.SCORE_THRESHOLD_SELECTED - fit_score, 1)
            lowest_stage = min(stage_scores.items(), key=lambda x: x[1]) if stage_scores else ("STAGE", 0.0)
            counterfactual = CounterfactualGuidance(
                target_category=FinalDecisionCategory.SELECTED,
                required_modifications=[
                    f"Improve overall hiring fit by +{needed} points to cross the 82.0% threshold.",
                    f"Raise lowest-scoring stage ({lowest_stage[0]} from {lowest_stage[1]:.1f}) by at least +{needed * 2:.1f} pts.",
                    "Resolve flagged cross-round variance or behavioral reservations during Bar Raiser debrief.",
                ],
                feasibility_notes="Highly actionable: candidate is within striking distance of an unconditional offer.",
            )
        elif decision_category == FinalDecisionCategory.REJECTED:
            lowest_stage = min(stage_scores.items(), key=lambda x: x[1]) if stage_scores else ("STAGE", 0.0)
            needed = round(self.SCORE_THRESHOLD_HOLD_FLOOR - fit_score, 1)
            counterfactual = CounterfactualGuidance(
                target_category=FinalDecisionCategory.HOLD_REVIEW,
                required_modifications=[
                    f"Resolve all critical technical or gating breaches (require >= {self.CRITICAL_TECH_FLOOR} pts in core coding).",
                    f"Increase composite fit by +{needed} points to reach the 65.0% consideration floor.",
                    "Provide verified proof of credential authenticity to clear integrity flags.",
                ],
                feasibility_notes="Substantial skill or integrity remediation required before re-entering interview pipeline.",
            )

        return positives[:4], blockers[:4], counterfactual
