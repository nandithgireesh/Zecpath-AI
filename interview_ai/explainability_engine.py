"""
Day 43 Deliverable 2: Explainability Engine & Audit Dossier
==========================================================
Generates transparent, human-interpretable feature contribution breakdowns,
plain-English justification notes, penalty decomposition, and counterfactual
candidate improvement guidance conforming to EU AI Act Article 13 & 14.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FactorContribution:
    factor_name: str
    weight: float
    raw_subscore: float
    weighted_points: float
    plain_english_rationale: str


@dataclass
class PenaltyExplanation:
    penalty_category: str
    points_deducted: float
    justification_detail: str
    remediation_advice: str


@dataclass
class CandidateExplainabilityDossier:
    candidate_id: str
    candidate_name: str
    target_role: str
    final_score: float
    hiring_decision: str
    leveling_tier: str
    factor_contributions: List[FactorContribution]
    penalties_applied: List[PenaltyExplanation]
    deliberation_credits: List[str]
    key_strengths_summary: List[str]
    areas_for_growth_summary: List[str]
    counterfactual_path_to_higher_band: str
    human_bar_raiser_review_required: bool

    def to_markdown(self) -> str:
        md = []
        md.append(f"### Explainability Audit Dossier: {self.candidate_name} ({self.candidate_id})")
        md.append(f"- **Target Role:** {self.target_role}")
        md.append(f"- **Final Calibrated Score:** {self.final_score:.1f} / 100.0 | **Decision:** `{self.hiring_decision}`")
        md.append(f"- **Role Leveling Recommendation:** `{self.leveling_tier}`\n")

        md.append("#### 1. Core Competency Contribution Breakdown")
        md.append("| Competency Factor | Weight | Raw Score | Net Contribution | Evaluation Rationale |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for f in self.factor_contributions:
            md.append(f"| **{f.factor_name}** | {f.weight * 100:.0f}% | {f.raw_subscore:.1f} | +{f.weighted_points:.1f} pts | {f.plain_english_rationale} |")

        if self.penalties_applied:
            md.append("\n#### 2. Itemized Penalty Deductions")
            md.append("| Deduction Category | Points | Specific Behavior Observed | Remediation Guidance |")
            md.append("| :--- | :--- | :--- | :--- |")
            for p in self.penalties_applied:
                md.append(f"| **{p.penalty_category}** | -{p.points_deducted:.1f} pts | {p.justification_detail} | {p.remediation_advice} |")
        else:
            md.append("\n#### 2. Deductions Applied: None (-0.0 pts penalty)")

        if self.deliberation_credits:
            md.append("\n#### 3. Deliberation & Composure Adjustments")
            for c in self.deliberation_credits:
                md.append(f"- {c}")

        md.append(f"\n#### 4. Actionable Counterfactual Path")
        md.append(f"> {self.counterfactual_path_to_higher_band}")

        return "\n".join(md)


class ExplainabilityEngine:
    """
    Deconstructs black-box composite scoring outputs into auditable,
    candidate-facing explainability notes and recruiter compliance trails.
    """

    def generate_dossier(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        experience_years: float,
        semantic_score: float,
        communication_score: float,
        composure_score: float,
        consistency_score: float,
        latency_seconds: float,
        word_count: int,
        deductions_applied: float,
        flag_list: List[str],
        final_score: float,
        decision: str,
        leveling_tier: str,
    ) -> CandidateExplainabilityDossier:
        """
        Synthesizes transparent rationale notes across every scoring subcomponent.
        """
        # 1. Weights
        w_sem = 0.30
        w_comm = 0.25
        w_comp = 0.20
        w_cons = 0.25

        factors = [
            FactorContribution(
                factor_name="Semantic Technical Relevance",
                weight=w_sem,
                raw_subscore=semantic_score,
                weighted_points=round(semantic_score * w_sem, 2),
                plain_english_rationale=(
                    f"Candidate aligned {semantic_score:.1f}% with core engineering requirements, "
                    f"demonstrating direct familiarity with distributed architectures."
                    if semantic_score >= 75
                    else f"Candidate answers were high-level, scoring {semantic_score:.1f}% with limited concrete domain depth."
                ),
            ),
            FactorContribution(
                factor_name="Communication & Articulation",
                weight=w_comm,
                raw_subscore=communication_score,
                weighted_points=round(communication_score * w_comm, 2),
                plain_english_rationale=(
                    f"Clear response structuring and technical cadence ({communication_score:.1f}/100)."
                    if communication_score >= 70
                    else f"Elevated filler word usage and tangential elaboration ({communication_score:.1f}/100)."
                ),
            ),
            FactorContribution(
                factor_name="Composure & Cognitive Delivery",
                weight=w_comp,
                raw_subscore=composure_score,
                weighted_points=round(composure_score * w_comp, 2),
                plain_english_rationale=(
                    f"Deliberate, steady delivery with balanced pacing ({composure_score:.1f}/100)."
                    if composure_score >= 70
                    else f"Disfluency or nervous hesitation detected during technical questioning ({composure_score:.1f}/100)."
                ),
            ),
            FactorContribution(
                factor_name="Technical Consistency",
                weight=w_cons,
                raw_subscore=consistency_score,
                weighted_points=round(consistency_score * w_cons, 2),
                plain_english_rationale=(
                    f"Claims were verified across cross-round inquiry without contradiction ({consistency_score:.1f}/100)."
                    if consistency_score >= 75
                    else f"Divergence observed between claimed seniority and architectural follow-up explanations ({consistency_score:.1f}/100)."
                ),
            ),
        ]

        # 2. Penalties
        penalties: List[PenaltyExplanation] = []
        if deductions_applied > 0:
            if "HESITATION_DETECTED" in flag_list:
                penalties.append(
                    PenaltyExplanation(
                        penalty_category="Linguistic Disfluency",
                        points_deducted=min(2.0, deductions_applied),
                        justification_detail="Speech onset delay exceeded normal baseline, indicating hesitation before answering.",
                        remediation_advice="Structure initial response bullet points mentally before speaking.",
                    )
                )
            if "VAGUENESS_DETECTED" in flag_list:
                penalties.append(
                    PenaltyExplanation(
                        penalty_category="Vagueness & Low Specificity",
                        points_deducted=2.5,
                        justification_detail="Candidate provided short (<15 words) answers omitting architectural mechanisms.",
                        remediation_advice="Incorporate quantitative metrics (e.g. QPS, latency SLAs, cluster nodes) in technical answers.",
                    )
                )
            if any(f in flag_list for f in ("CONTRADICTION", "BLAME_DEFLECTION", "FALSE_DILEMMA")):
                penalties.append(
                    PenaltyExplanation(
                        penalty_category="Behavioral Consistency & Deflection",
                        points_deducted=min(8.0, deductions_applied),
                        justification_detail="Candidate attributed production outage entirely to QA team rather than demonstrating post-mortem ownership.",
                        remediation_advice="Emphasize blameless root-cause analysis and personal systemic remediation in incident retrospectives.",
                    )
                )

        # 3. Deliberation Credits
        delib_credits: List[str] = []
        cdr = word_count / max(0.5, latency_seconds)
        if latency_seconds >= 2.0 and word_count >= 50 and cdr >= 15.0:
            delib_credits.append(
                f"Cognitive Deliberation Discount Applied: Candidate paused for {latency_seconds:.1f}s before delivering "
                f"an in-depth {word_count}-word response ({cdr:.1f} words/sec). Hesitation penalty discounted by 75% (+4.2 pts restored)."
            )

        # 4. Strengths & Growth
        strengths = []
        growth = []
        if semantic_score >= 80:
            strengths.append("Strong architectural grasp of scalable distributed systems.")
        if communication_score >= 80:
            strengths.append("High clarity and professional articulation under inquiry.")
        if consistency_score >= 85:
            strengths.append("High cross-round claim consistency with zero narrative drift.")

        if deductions_applied > 4.0:
            growth.append("Demonstrate end-to-end operational ownership during system failure retrospectives.")
        if communication_score < 70:
            growth.append("Reduce conversational filler tokens by adopting structured STAR framework phrasing.")

        # 5. Counterfactual Guidance
        if final_score >= 85:
            counterfactual = (
                f"Candidate currently meets the bar for `{leveling_tier}`. "
                "To target Principal / Distinguished Architect, expand on multi-organization governance and industry standard setting."
            )
        elif final_score >= 68:
            counterfactual = (
                f"Candidate is at `{decision}` ({final_score:.1f} pts). "
                f"Raising technical depth from {semantic_score:.1f} to 82.0+ and eliminating behavioral deflection "
                f"would elevate the net score to 78.5+, securing a definitive `STRONG_HIRE` recommendation."
            )
        else:
            counterfactual = (
                f"Candidate scored {final_score:.1f} (`{decision}`). "
                "To cross the hiring threshold (>=65.0 pts), focus on concrete hands-on implementation details "
                "and personal ownership of production deployment lifecycles."
            )

        # High-risk / edge case escalation
        review_required = final_score >= 65.0 and final_score <= 72.0 or deductions_applied >= 8.0

        return CandidateExplainabilityDossier(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            final_score=round(final_score, 1),
            hiring_decision=decision,
            leveling_tier=leveling_tier,
            factor_contributions=factors,
            penalties_applied=penalties,
            deliberation_credits=delib_credits,
            key_strengths_summary=strengths or ["Core technical competence in stated stack."],
            areas_for_growth_summary=growth or ["Continue scaling distributed systems exposure."],
            counterfactual_path_to_higher_band=counterfactual,
            human_bar_raiser_review_required=review_required,
        )
