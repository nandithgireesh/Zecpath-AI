"""
Day 37: Candidate HR Score Report Formatter (Deliverable 3)
===========================================================
Formats the CandidateHRScoreReport into ATS-compliant JSON, structured Markdown,
and human-readable terminal scorecards.
"""

import json
from typing import Dict, Any
from .hr_scoring_models import CandidateHRScoreReport


class HRScoreReportFormatter:
    """Serializes CandidateHRScoreReport into ATS JSON and markdown recruiter formats."""

    @staticmethod
    def to_ats_json(report: CandidateHRScoreReport, indent: int = 2) -> str:
        """Serializes the report to structured JSON compliant with enterprise ATS standards."""
        return report.model_dump_json(indent=indent)

    @staticmethod
    def to_markdown_summary(report: CandidateHRScoreReport) -> str:
        """Generates a professional Markdown dossier for hiring managers and interview debriefs."""
        rec_color = {
            "STRONG_HIRE": "**[STRONG HIRE]**",
            "HIRE": "**[HIRE]**",
            "LEAN_HIRE": "**[LEAN HIRE]**",
            "LEAN_NO_HIRE": "**[LEAN NO HIRE]**",
            "NO_HIRE": "**[NO HIRE]**",
        }.get(report.recommendation.value, report.recommendation.value)

        lines = [
            f"# Zecpath-AI Candidate HR Interview Score Report",
            f"**Candidate:** {report.candidate_name} | **Role:** {report.job_role} ({report.experience_years:.1f} yrs exp)",
            f"**Session ID:** `{report.session_id}` | **Date:** {report.evaluation_date[:10]}",
            f"**Weight Configuration Track:** {report.weight_profile_used}",
            f"",
            f"---",
            f"",
            f"## 1. Executive Hiring Verdict",
            f"- **Composite Calibrated Score:** **{report.composite_score:.1f} / 100**",
            f"- **Hiring Recommendation:** {rec_color}",
            f"- **Executive Summary:** {report.executive_summary}",
            f"",
            f"---",
            f"",
            f"## 2. Four Core Scoring Parameters Breakdown",
            f"| Scoring Parameter | Raw Score | Normalized Score | Weight | Points Contributed | % of Total Score |",
            f"| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        for key, p in report.parameter_breakdown.items():
            lines.append(
                f"| **{p.display_name}** | {p.raw_score:.1f} | {p.normalized_score:.1f} | {p.weight:.0%} | {p.weighted_contribution:.1f} pts | {p.percentage_of_total:.1f}% |"
            )

        lines.extend([
            f"",
            f"*Length Normalization Note:* Evaluated across {report.length_normalization.total_turns_evaluated} turns (Bayesian Prior $\\mu_0={report.length_normalization.prior_mean}$, $m={report.length_normalization.prior_weight_m}$, Completeness Factor: {report.length_normalization.session_completeness_factor:.2f}).",
            f"",
            f"---",
            f"",
            f"## 3. Sub-Dimensional Skill Ratings",
            f"",
            f"### Communication Sub-Dimensions (Day 35 6-Axis Pipeline)",
            f"- **Fluency:** {report.communication_subdimensions.get('fluency', 0.0):.1f} / 100",
            f"- **Grammar Hygiene:** {report.communication_subdimensions.get('grammar', 0.0):.1f} / 100",
            f"- **Vocabulary Depth:** {report.communication_subdimensions.get('vocabulary', 0.0):.1f} / 100",
            f"- **Clarity of Explanation:** {report.communication_subdimensions.get('clarity', 0.0):.1f} / 100",
            f"- **Filler Word Control:** {report.communication_subdimensions.get('filler_control', 0.0):.1f} / 100",
            f"- **Answer Structure (STAR/PREP):** {report.communication_subdimensions.get('structure', 0.0):.1f} / 100",
            f"",
            f"### Behavioral & Composure Signals (Day 36 4-Engine Pipeline)",
            f"- **Hesitation Control:** {report.behavioral_subdimensions.get('hesitation_control', 0.0):.1f} / 100",
            f"- **Sentiment Composure:** {report.behavioral_subdimensions.get('sentiment_composure', 0.0):.1f} / 100",
            f"- **Narrative Consistency:** {report.behavioral_subdimensions.get('narrative_consistency', 0.0):.1f} / 100",
            f"- **Psychological Resilience:** {report.behavioral_subdimensions.get('stress_resilience', 0.0):.1f} / 100",
            f"",
            f"---",
            f"",
            f"## 4. Turn-by-Turn Score Trajectory",
            f"| Turn | Phase | Category | Relevance | Communication | Confidence | Consistency | Composite |",
            f"| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for t in report.turn_score_trajectory:
            lines.append(
                f"| Turn {t['turn_index']} | {t['phase']} | {t['category']} | {t['relevance']:.1f} | {t['communication']:.1f} | {t['confidence']:.1f} | {t['consistency']:.1f} | **{t['composite_turn']:.1f}** |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 5. Recruiter Actionable Feedback",
            f"",
            f"### Key Observed Strengths",
        ])
        for s in report.key_strengths:
            lines.append(f"- [+] {s}")

        lines.append(f"\n### Risk Flags & Follow-up Alerts")
        if report.risk_flags:
            for f in report.risk_flags:
                lines.append(f"- [!] {f}")
        else:
            lines.append(f"- [OK] *Zero critical risk flags or contradiction alerts detected.*")

        lines.append(f"\n### Recommended Next Steps")
        for step in report.recommended_next_steps:
            lines.append(f"- [->] {step}")

        lines.append(f"\n---\n*Report generated by Zecpath-AI Enterprise Talent Platform — Confidential & Proprietary.*")
        return "\n".join(lines)
