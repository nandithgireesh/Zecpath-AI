"""
Day 41: Hiring Fit Calculator (Deliverable 2)
============================================
Calculates calibrated multi-dimensional hiring fit percentage (0-100%),
percentile rankings, organizational readiness levels, and safety-gated
hiring recommendations across:
1. Technical Competence Fit
2. Communication Clarity Fit
3. Behavioral & Culture Fit
4. Adaptability & Trajectory Fit
5. Risk & Integrity Discounts
"""

import math
from typing import Dict, List, Tuple, Optional
from .models import (
    RoundType,
    RoundScoreInput,
    CrossRoundWeightProfile,
    RoundContribution,
    HiringFitBreakdown,
    HiringDecisionTier,
    ReadinessLevel,
)


class HiringFitCalculator:
    """
    Deliverable 2: Mathematical calculator transforming cross-round telemetry
    into a calibrated 0-100% hiring fit metric and decision recommendation.
    """

    # Empirical distribution parameters for percentile calculation
    POPULATION_MEAN: float = 68.0
    POPULATION_STD_DEV: float = 14.5

    @classmethod
    def _compute_normal_cdf(cls, x: float, mean: float, std_dev: float) -> float:
        """Approximates standard normal cumulative distribution function (CDF)."""
        z = (x - mean) / (std_dev * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    @classmethod
    def calculate_round_contributions(
        cls,
        round_inputs: Dict[RoundType, RoundScoreInput],
        weight_profile: CrossRoundWeightProfile,
    ) -> Tuple[Dict[RoundType, RoundContribution], float, bool, List[str]]:
        """
        Computes weighted point contributions and evaluates hard safety gates for each round.
        Returns:
            (contributions_dict, composite_score, all_gates_passed, gate_failure_reasons)
        """
        contributions: Dict[RoundType, RoundContribution] = {}
        composite_score = 0.0
        all_gates_passed = True
        failure_reasons: List[str] = []

        weights_map = {
            RoundType.ATS_RESUME: weight_profile.ats_weight,
            RoundType.CONVERSATIONAL_SCREENING: weight_profile.screening_weight,
            RoundType.HR_INTERVIEW: weight_profile.hr_interview_weight,
        }

        for r_type, weight in weights_map.items():
            r_input = round_inputs.get(r_type)
            if not r_input:
                # Missing round defaults to 0 with gate failure
                score = 0.0
                name = r_type.value
                passed = False
                thresh = weight_profile.minimum_thresholds.get(r_type, 50.0)
                failure_reasons.append(f"Missing mandatory evaluation round: {r_type.value}")
                all_gates_passed = False
            else:
                score = r_input.normalized_score
                name = r_input.round_name
                thresh = weight_profile.minimum_thresholds.get(r_type, 0.0)
                passed = (score >= thresh)
                if not passed:
                    all_gates_passed = False
                    failure_reasons.append(
                        f"{name} score ({score:.1f}) fell below minimum required threshold ({thresh:.1f})."
                    )

            weighted_pts = round(score * weight, 2)
            composite_score += weighted_pts

            contributions[r_type] = RoundContribution(
                round_type=r_type,
                display_name=name,
                raw_score=round(score, 1),
                effective_weight=round(weight, 3),
                weighted_points=weighted_pts,
                passed_gate=passed,
                gate_threshold=thresh,
                status_note="PASSED GATE" if passed else f"FAILED GATE (< {thresh:.1f})",
            )

        composite_score = max(0.0, min(100.0, round(composite_score, 1)))
        return contributions, composite_score, all_gates_passed, failure_reasons

    @classmethod
    def calculate_hiring_fit(
        cls,
        round_inputs: Dict[RoundType, RoundScoreInput],
        composite_score: float,
    ) -> HiringFitBreakdown:
        """
        Synthesizes multi-dimensional hiring fit indices across technical, communication,
        behavioral, and trajectory dimensions, discounting for detected risk flags.
        """
        ats = round_inputs.get(RoundType.ATS_RESUME)
        screening = round_inputs.get(RoundType.CONVERSATIONAL_SCREENING)
        hr = round_inputs.get(RoundType.HR_INTERVIEW)

        ats_score = ats.normalized_score if ats else 50.0
        screen_score = screening.normalized_score if screening else 50.0
        hr_score = hr.normalized_score if hr else 50.0

        # Sub-dimension extractions with fallbacks
        ats_dims = ats.dimension_breakdown if ats else {}
        screen_dims = screening.dimension_breakdown if screening else {}
        hr_dims = hr.dimension_breakdown if hr else {}

        skill_val = ats_dims.get("skill_score", ats_score)
        exp_val = ats_dims.get("experience_score", ats_score)
        apt_val = hr_dims.get("aptitude_score", hr_score)

        screen_clarity = screen_dims.get("clarity_score", screen_score)
        hr_comm = hr_dims.get("communication_score", hr_score)

        screen_beh = screen_dims.get("behavioral_score", screen_score)
        hr_cult = hr_dims.get("cultural_fit", hr_score)

        screen_cons = screen_dims.get("consistency_score", screen_score)
        hr_comp = hr_dims.get("confidence_score", hr_score)

        # 1. Technical Competence Fit (40% ATS Skill, 20% ATS Exp, 40% HR Aptitude)
        tech_fit = round(0.40 * skill_val + 0.20 * exp_val + 0.40 * apt_val, 1)

        # 2. Communication Clarity Fit (45% Screening Clarity, 55% HR Communication)
        comm_fit = round(0.45 * screen_clarity + 0.55 * hr_comm, 1)

        # 3. Behavioral & Culture Fit (40% Screening, 60% HR Cultural Alignment)
        beh_fit = round(0.40 * screen_beh + 0.60 * hr_cult, 1)

        # 4. Adaptability & Trajectory Fit (50% Screening Consistency, 50% HR Composure)
        traj_fit = round(0.50 * screen_cons + 0.50 * hr_comp, 1)

        # 5. Risk & Integrity Discount (Fallacies, Contradictions, Blame Deflection)
        total_penalties = 0.0
        all_flags = []
        for r_inp in [ats, screening, hr]:
            if r_inp and r_inp.flags_or_penalties:
                all_flags.extend(r_inp.flags_or_penalties)

        for flag in all_flags:
            flag_upper = flag.upper()
            if "CONTRADICTION" in flag_upper:
                total_penalties += 6.0
            elif "BLAME" in flag_upper:
                total_penalties += 5.0
            elif "FALSE_DILEMMA" in flag_upper or "FALLACY" in flag_upper:
                total_penalties += 4.0
            elif "VAGUENESS" in flag_upper:
                total_penalties += 2.5
            else:
                total_penalties += 2.0

        # Non-linear bounded discount (capped at 20.0 pts to prevent double-dipping score collapse)
        risk_discount = round(min(20.0, total_penalties), 1)

        # Multi-dimensional average
        sub_fit_avg = (tech_fit + comm_fit + beh_fit + traj_fit) / 4.0

        # Calibrated Net Hiring Fit Percentage
        net_fit = round(0.50 * composite_score + 0.50 * sub_fit_avg - (risk_discount * 0.5), 1)
        net_fit = max(0.0, min(100.0, net_fit))

        # Percentile calculation
        percentile_val = cls._compute_normal_cdf(net_fit, cls.POPULATION_MEAN, cls.POPULATION_STD_DEV) * 100.0
        percentile = round(min(99.9, max(0.1, percentile_val)), 1)

        # Qualitative fit summary
        if net_fit >= 85.0:
            summary = "Elite cross-round alignment across technical depth, verbal articulation, and cultural ownership."
        elif net_fit >= 72.0:
            summary = "Strong multi-round performance with dependable technical capabilities and clear communication."
        elif net_fit >= 60.0:
            summary = "Moderate competency with notable hesitation or minor gaps requiring targeted manager probing."
        elif net_fit >= 45.0:
            summary = "Sub-threshold autonomous readiness; exhibits significant trade-off or communication deficiencies."
        else:
            summary = "Critical misalignment, operational contradictions, or disqualifying cognitive fallacies detected."

        return HiringFitBreakdown(
            technical_competence_fit=tech_fit,
            communication_clarity_fit=comm_fit,
            behavioral_culture_fit=beh_fit,
            adaptability_trajectory_fit=traj_fit,
            risk_and_integrity_discount=risk_discount,
            net_hiring_fit_percentage=net_fit,
            calibrated_percentile=percentile,
            fit_summary=summary,
        )

    @classmethod
    def synthesize_decision(
        cls,
        hiring_fit: HiringFitBreakdown,
        all_gates_passed: bool,
        candidate_experience_years: float,
        target_role: str,
    ) -> Tuple[HiringDecisionTier, ReadinessLevel, str, str]:
        """
        Synthesizes final decision tier, readiness classification, calibrated role level,
        and executive recruiter verdict.
        """
        fit = hiring_fit.net_hiring_fit_percentage
        discount = hiring_fit.risk_and_integrity_discount

        # Hard safety gate: If critical integrity risk or failed gate, cannot hire
        if discount >= 12.0 or (not all_gates_passed and fit < 60.0):
            decision = HiringDecisionTier.NO_HIRE
            readiness = ReadinessLevel.OPERATIONAL_RISK_REJECT
            role_tier = "Not Recommended for Placement"
            verdict = (
                f"Candidate exhibited critical operational contradictions or disqualified on mandatory safety gates. "
                f"Disqualified with a net hiring fit of {fit:.1f}%."
            )
        elif not all_gates_passed:
            decision = HiringDecisionTier.LEAN_NO_HIRE
            readiness = ReadinessLevel.SUB_THRESHOLD_UPSKILL
            role_tier = f"Associate / Sub-Threshold {target_role}"
            verdict = (
                f"Candidate demonstrated potential but failed minimum round gating thresholds. "
                f"Recommended for developmental upskilling prior to re-interview consideration."
            )
        elif fit >= 85.0:
            decision = HiringDecisionTier.STRONG_HIRE
            readiness = ReadinessLevel.IMMEDIATE_FAST_TRACK
            if candidate_experience_years >= 12.0:
                role_tier = f"Principal / Staff Architect (Leveling Upgrade for {target_role})"
            elif candidate_experience_years >= 5.0:
                role_tier = f"Senior / Lead {target_role}"
            else:
                role_tier = f"High-Impact Mid-Level {target_role}"
            verdict = (
                f"Exceptional candidate demonstrating elite cross-round mastery (Fit: {fit:.1f}%, {hiring_fit.calibrated_percentile}th percentile). "
                f"Immediate fast-track hire recommended for {role_tier}."
            )
        elif fit >= 72.0:
            decision = HiringDecisionTier.HIRE
            readiness = ReadinessLevel.PRODUCTION_READY
            role_tier = f"Core {target_role}"
            verdict = (
                f"Strong candidate satisfying all technical and behavioral requisites (Fit: {fit:.1f}%). "
                f"Production ready with standard enterprise onboarding."
            )
        elif fit >= 60.0:
            decision = HiringDecisionTier.LEAN_HIRE
            readiness = ReadinessLevel.DEVELOPING_WITH_MENTORSHIP
            role_tier = f"Associate / Developing {target_role}"
            verdict = (
                f"Demonstrates foundational aptitude with conversational hesitation or skill boundaries (Fit: {fit:.1f}%). "
                f"Recommended for hire with targeted onboarding mentorship."
            )
        elif fit >= 45.0:
            decision = HiringDecisionTier.LEAN_NO_HIRE
            readiness = ReadinessLevel.SUB_THRESHOLD_UPSKILL
            role_tier = f"Sub-Threshold for {target_role}"
            verdict = (
                f"Candidate falls below senior autonomy expectations (Fit: {fit:.1f}%). "
                f"Consider for junior placement or recommend 6-month skill upskilling."
            )
        else:
            decision = HiringDecisionTier.NO_HIRE
            readiness = ReadinessLevel.OPERATIONAL_RISK_REJECT
            role_tier = "Not Recommended"
            verdict = (
                f"Low composite score and cross-round deficiencies (Fit: {fit:.1f}%). "
                f"Unsuitable for current enterprise deployment."
            )

        return decision, readiness, role_tier, verdict
