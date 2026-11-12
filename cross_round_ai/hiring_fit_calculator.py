"""
Zecpath-AI: Day 51 - Hiring Fit Calculator
==========================================
Calculates the final calibrated Hiring Fit Score (%) across all 5 evaluation stages:
1. Mathematical multi-stage score aggregation and profile-aware normalization
2. Synthesizes 4-dimensional holistic radar competency scores
3. Calculates transparent risk discount deductions (inconsistencies, gate breaches)
4. Maps aggregate scores to organizational readiness tiers and hiring decisions

Curriculum Reference: Day 51 - Deliverable 1: Hiring Fit Calculator
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from .models import (
    AssessmentStage,
    StageScoreInput,
    CrossStageWeightConfig,
    CandidateProfileTier,
    StageScoreContribution,
    RadarDimensionScore,
    RiskDiscountTelemetry,
    HiringDecision,
    ReadinessTier,
)


class HiringFitCalculator:
    """
    Mathematical calculation engine evaluating cross-round telemetry into a
    calibrated, profile-normalized Hiring Fit Score (%).
    """

    def __init__(self):
        pass

    def calculate_stage_contributions(
        self,
        stage_scores: Dict[AssessmentStage, StageScoreInput],
        weight_config: CrossStageWeightConfig,
    ) -> Tuple[Dict[AssessmentStage, StageScoreContribution], bool, float]:
        """
        Computes the weighted contribution of each of the 5 assessment stages
        and verifies hard gating floors.
        """
        contributions: Dict[AssessmentStage, StageScoreContribution] = {}
        all_gates_passed = True
        base_aggregate = 0.0

        for stage, score_input in stage_scores.items():
            spec = weight_config.weights.get(stage)
            if not spec:
                continue

            passed_gate = score_input.normalized_score >= spec.min_cutoff_score
            if spec.is_critical_gate and not passed_gate:
                all_gates_passed = False

            points = round(score_input.normalized_score * spec.weight, 2)
            base_aggregate += points

            contributions[stage] = StageScoreContribution(
                stage=stage,
                stage_name=score_input.stage_name,
                raw_score=round(score_input.raw_score, 1),
                normalized_score=round(score_input.normalized_score, 1),
                weight=spec.weight,
                points_contributed=points,
                percentage_of_final=round(spec.weight * 100.0, 1),
                passed_gate=passed_gate,
                cutoff_threshold=spec.min_cutoff_score,
                key_strengths=score_input.key_strengths,
                risk_observations=score_input.risk_flags,
            )

        base_aggregate = round(max(0.0, min(100.0, base_aggregate)), 2)
        return contributions, all_gates_passed, base_aggregate

    def compute_radar_competencies(
        self,
        stage_scores: Dict[AssessmentStage, StageScoreInput],
        experience_tier: CandidateProfileTier,
    ) -> List[RadarDimensionScore]:
        """
        Synthesizes 4 core orthogonal competency radar dimensions.
        """
        ats = stage_scores.get(AssessmentStage.ATS_RESUME)
        screen = stage_scores.get(AssessmentStage.CONVERSATIONAL_SCREENING)
        hr = stage_scores.get(AssessmentStage.HR_BEHAVIORAL_INTERVIEW)
        tech = stage_scores.get(AssessmentStage.TECHNICAL_INTERVIEW)
        mach = stage_scores.get(AssessmentStage.MACHINE_TEST)

        # 1. Technical Problem Solving & Architecture (Tech 50% + Machine 50%)
        t_score = tech.normalized_score if tech else 50.0
        m_score = mach.normalized_score if mach else 50.0
        tech_dim = round((t_score * 0.50) + (m_score * 0.50), 1)

        # 2. Communication & Cultural Alignment (Screening 40% + HR 60%)
        s_score = screen.normalized_score if screen else 50.0
        h_score = hr.normalized_score if hr else 50.0
        comm_dim = round((s_score * 0.40) + (h_score * 0.60), 1)

        # 3. Domain Background & Credentials (ATS 100%)
        bg_dim = round(ats.normalized_score if ats else 50.0, 1)

        # 4. Practical Delivery & Execution Efficiency (Machine Test + Composure)
        exec_dim = round((m_score * 0.70) + (h_score * 0.30), 1)

        # Profile normalization percentile offsets
        tier_multipliers = {
            CandidateProfileTier.ENTRY_LEVEL_0_2: 1.05,
            CandidateProfileTier.MID_LEVEL_3_5: 1.00,
            CandidateProfileTier.SENIOR_LEAD_5_PLUS: 0.95,
            CandidateProfileTier.PRINCIPAL_ARCHITECT: 0.90,
        }
        mult = tier_multipliers.get(experience_tier, 1.00)

        radar = [
            RadarDimensionScore(
                dimension_name="Technical Problem Solving & Architecture",
                score=tech_dim,
                percentile_benchmark=round(min(99.0, tech_dim * mult), 1),
                summary="Synthesized technical reasoning and sandbox machine test performance.",
            ),
            RadarDimensionScore(
                dimension_name="Communication & Cultural Alignment",
                score=comm_dim,
                percentile_benchmark=round(min(99.0, comm_dim * mult), 1),
                summary="Spoken fluency, hesitation control, and STAR behavioral leadership.",
            ),
            RadarDimensionScore(
                dimension_name="Domain Background & Credentials",
                score=bg_dim,
                percentile_benchmark=round(min(99.0, bg_dim * mult), 1),
                summary="ATS resume relevance, tech stack alignment, and verified experience.",
            ),
            RadarDimensionScore(
                dimension_name="Practical Delivery & Operational Execution",
                score=exec_dim,
                percentile_benchmark=round(min(99.0, exec_dim * mult), 1),
                summary="Sandbox runtime efficiency, error-recovery agility, and composure under pressure.",
            ),
        ]
        return radar

    def calculate_risk_discounts(
        self,
        stage_scores: Dict[AssessmentStage, StageScoreInput],
        all_gates_passed: bool,
    ) -> RiskDiscountTelemetry:
        """
        Detects cross-round contradictions and computes calibrated risk discount deductions.
        """
        risk_explanations = []
        inconsistency_penalty = 0.0
        gate_penalty = 0.0

        ats = stage_scores.get(AssessmentStage.ATS_RESUME)
        tech = stage_scores.get(AssessmentStage.TECHNICAL_INTERVIEW)
        mach = stage_scores.get(AssessmentStage.MACHINE_TEST)

        # Contradiction: High ATS claim vs. Failed Technical/Machine Test
        if ats and tech and ats.normalized_score >= 85.0 and tech.normalized_score < 55.0:
            inconsistency_penalty += 8.0
            risk_explanations.append(
                f"Competency Gap: High resume claim ({ats.normalized_score:.1f}) contradicted by poor Technical Interview ({tech.normalized_score:.1f})."
            )

        if ats and mach and ats.normalized_score >= 85.0 and mach.normalized_score < 50.0:
            inconsistency_penalty += 7.0
            risk_explanations.append(
                f"Execution Gap: Claimed senior credentials ({ats.normalized_score:.1f}) but failed sandbox Machine Test ({mach.normalized_score:.1f})."
            )

        # Hard Gate Breach
        if not all_gates_passed:
            gate_penalty = 15.0
            risk_explanations.append("Disqualification Trigger: One or more critical stage cutoffs were breached.")

        total_discount = round(inconsistency_penalty + gate_penalty, 2)

        return RiskDiscountTelemetry(
            cross_round_inconsistency_penalty=inconsistency_penalty,
            integrity_malpractice_penalty=0.0,
            gate_failure_penalty=gate_penalty,
            total_risk_discount=total_discount,
            risk_explanations=risk_explanations,
        )

    def determine_hiring_verdict(
        self,
        hiring_fit_score: float,
        all_gates_passed: bool,
        experience_tier: CandidateProfileTier,
    ) -> Tuple[HiringDecision, ReadinessTier, str]:
        """
        Determines the official hiring decision, readiness tier, and calibrated leveling.
        """
        if not all_gates_passed or hiring_fit_score < 45.0:
            decision = HiringDecision.NO_HIRE
            readiness = ReadinessTier.DISQUALIFIED_HIGH_RISK
            leveling = "Not Recommended for Offer"
        elif hiring_fit_score >= 85.0:
            decision = HiringDecision.STRONG_HIRE
            readiness = ReadinessTier.FAST_TRACK_OFFER
            if experience_tier in (CandidateProfileTier.SENIOR_LEAD_5_PLUS, CandidateProfileTier.PRINCIPAL_ARCHITECT):
                leveling = "Staff / Principal Technical Architect"
            else:
                leveling = "Senior Software Engineer"
        elif hiring_fit_score >= 72.0:
            decision = HiringDecision.HIRE
            readiness = ReadinessTier.PRODUCTION_DEPLOYABLE
            leveling = "Mid-to-Senior Software Engineer"
        elif hiring_fit_score >= 60.0:
            decision = HiringDecision.LEAN_HIRE
            readiness = ReadinessTier.DEVELOPING_WITH_ONBOARDING
            leveling = "Associate / Mid Software Engineer"
        else:
            decision = HiringDecision.LEAN_NO_HIRE
            readiness = ReadinessTier.BELOW_BAR_UPSKILL
            leveling = "Junior Developer (Upskill Required)"

        return decision, readiness, leveling
