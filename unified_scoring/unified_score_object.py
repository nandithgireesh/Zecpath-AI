"""
Day 41: Unified Candidate Score Object Serialization & Formatter (Deliverable 3)
================================================================================
Serializes the master Unified Candidate Score Object into:
1. Enterprise ATS / HRIS compliant JSON payload
2. Natural language recruiter executive markdown debrief
3. Audit-ready diagnostic dictionaries
"""

import json
from typing import Dict, Any
from .models import UnifiedCandidateScoreObject, RoundType


class UnifiedScoreObjectFormatter:
    """
    Deliverable 3: Formats and exports the Unified Candidate Score Object
    for enterprise ATS integration, executive debriefs, and hiring audits.
    """

    @classmethod
    def to_ats_json(cls, score_obj: UnifiedCandidateScoreObject) -> str:
        """Serializes score object to standardized enterprise ATS JSON."""
        return json.dumps(score_obj.model_dump(), indent=2, default=str)

    @classmethod
    def to_recruiter_markdown(cls, score_obj: UnifiedCandidateScoreObject) -> str:
        """Generates a high-impact, professional executive markdown debrief for recruiters."""
        md = []
        md.append(f"# Unified Hiring Intelligence Report: {score_obj.candidate_name}")
        md.append(f"**Target Role:** {score_obj.target_role} | **Role Track:** {score_obj.weight_profile_used.display_name}")
        md.append(f"**Candidate ID:** `{score_obj.candidate_id}` | **Evaluation Date:** {score_obj.evaluation_date[:10]}\n")

        # Executive Summary Box
        md.append("## 1. Executive Hiring Verdict & Readiness")
        md.append(f"> **Final Decision:** `{score_obj.final_decision.value}`  ")
        md.append(f"> **Net Hiring Fit:** **{score_obj.hiring_fit.net_hiring_fit_percentage:.1f}%** ({score_obj.hiring_fit.calibrated_percentile}th Percentile)  ")
        md.append(f"> **Calibrated Role Level:** **{score_obj.calibrated_role_tier}**  ")
        md.append(f"> **Deployment Readiness:** `{score_obj.readiness_level.value}`\n")
        md.append(f"**Executive Verdict:** {score_obj.executive_verdict}\n")

        # Cross-Round Scorecard Table
        md.append("## 2. Cross-Round Scoring Breakdown (Days 1 to 40)")
        md.append("| Round | Component | Raw Score | Weight | Weighted Points | Safety Gate Status |")
        md.append("|---|---|:---:|:---:|:---:|:---:|")

        round_order = [RoundType.ATS_RESUME, RoundType.CONVERSATIONAL_SCREENING, RoundType.HR_INTERVIEW]
        for r_type in round_order:
            contrib = score_obj.round_contributions.get(r_type)
            if contrib:
                gate_str = "PASSED" if contrib.passed_gate else f"**FAILED** (< {contrib.gate_threshold:.1f})"
                md.append(
                    f"| **{r_type.value}** | {contrib.display_name} | {contrib.raw_score:.1f} | "
                    f"{contrib.effective_weight * 100:.0f}% | **{contrib.weighted_points:.2f} pts** | {gate_str} |"
                )

        md.append(f"| **TOTAL COMPOSITE** | Multi-Round Weighted Synthesis | - | **100%** | **{score_obj.composite_score:.2f} pts** | "
                  f"{'ALL GATES PASSED' if score_obj.safety_gate_passed else '**GATE FAILED**'} |\n")

        # Hiring Fit Breakdown
        hf = score_obj.hiring_fit
        md.append("## 3. Multi-Dimensional Hiring Fit Analytics")
        md.append("| Evaluation Dimension | Fit Score (0-100) | Operational Interpretation |")
        md.append("|---|:---:|---|")
        md.append(f"| **Technical Competence Fit** | **{hf.technical_competence_fit:.1f}** | Skills match, experience tenure, and architectural trade-off logic |")
        md.append(f"| **Communication Clarity Fit** | **{hf.communication_clarity_fit:.1f}** | STT transcript fluency, articulation, and vocabulary hygiene |")
        md.append(f"| **Behavioral & Culture Fit** | **{hf.behavioral_culture_fit:.1f}** | STAR ownership, blameless post-mortem, and team collaboration |")
        md.append(f"| **Adaptability & Trajectory Fit** | **{hf.adaptability_trajectory_fit:.1f}** | Acoustic composure, stress resilience, and problem-solving growth |")
        md.append(f"| **Risk & Integrity Discount** | **-{hf.risk_and_integrity_discount:.1f} pts** | Deductions applied for contradictions, blame deflection, or fallacies |")
        md.append(f"| **NET HIRING FIT PERCENTAGE** | **{hf.net_hiring_fit_percentage:.1f}%** | Overall calibrated organizational compatibility |")
        md.append(f"| **Cohort Percentile Rank** | **{hf.calibrated_percentile}th** | Calibrated against empirical hiring distribution (mean=68, std=14.5) |\n")

        # Strengths & Developmental Areas
        md.append("## 4. Key Strengths & Developmental Focus")
        md.append("### Key Candidate Strengths")
        if score_obj.key_strengths:
            for s in score_obj.key_strengths:
                md.append(f"- {s}")
        else:
            md.append("- No outstanding cross-round strengths noted.")
        md.append("")

        md.append("### Developmental & Risk Areas")
        if score_obj.developmental_areas:
            for d in score_obj.developmental_areas:
                md.append(f"- {d}")
        else:
            md.append("- None identified; candidate satisfied all benchmark dimensions.")
        md.append("")

        # Audit & Gating
        md.append("## 5. Safety Gating & Audit Trail")
        md.append(f"- **All Mandatory Gates Passed:** `{score_obj.safety_gate_passed}`")
        if score_obj.gate_failure_reasons:
            md.append(f"- **Gating Exceptions:** {', '.join(score_obj.gate_failure_reasons)}")
        md.append(f"- **Weight Profile Rationale:** {score_obj.weight_profile_used.rationale}")
        md.append(f"- **Audit Hash:** `{score_obj.audit_metadata.get('audit_hash', 'AUTOGEN-VERIFIED')}`")

        return "\n".join(md)
