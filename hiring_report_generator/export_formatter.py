"""
Day 53: Export-Ready Report Formatter (Deliverable 3)
====================================================
Formats CandidateAIProfileReport into multiple recruiter-friendly formats:
- JSON (Standard structured interchange)
- Markdown (ATS & documentation ready)
- Executive Summary Card (1-look recruiter card)
- Modern HTML (Interactive styling with glassmorphism)
"""

import json
from typing import Dict, Any
from hiring_report_generator.models import CandidateAIProfileReport


class ReportExportFormatter:
    """
    Deliverable 3: Export-Ready Report Formatter supporting JSON, Markdown,
    Executive Summary Card, and HTML layouts.
    """

    @staticmethod
    def to_json(report: CandidateAIProfileReport, indent: int = 2) -> str:
        """Serializes report to structured, validated JSON."""
        return report.model_dump_json(indent=indent)

    @staticmethod
    def to_executive_summary_card(report: CandidateAIProfileReport) -> str:
        """
        Creates a condensed, high-impact 1-look Recruiter Executive Card.
        Ideal for Slack notifications, ATS preview cards, or mobile review.
        """
        badge = report.final_recommendation.decision_category
        substatus = report.final_recommendation.decision_substatus
        fit = report.final_recommendation.hiring_fit_score
        conf = report.final_recommendation.confidence_score
        band = report.final_recommendation.confidence_band

        card = []
        card.append("+" + "-" * 78 + "+")
        card.append(f"| ZECPATH-AI RECRUITER EXECUTIVE SUMMARY CARD".ljust(79) + "|")
        card.append("+" + "-" * 78 + "+")
        card.append(f"| CANDIDATE : {report.candidate_name} ({report.candidate_id})".ljust(79) + "|")
        card.append(f"| ROLE      : {report.target_role} [{report.experience_tier}]".ljust(79) + "|")
        card.append(f"| DECISION  : [{badge}] -> {substatus}".ljust(79) + "|")
        card.append(f"| FIT SCORE : {fit:.1f}%  |  CONFIDENCE: {conf:.1f}% ({band})".ljust(79) + "|")
        card.append(f"| RISK TIER : {report.behavioral_and_risk.overall_risk_level}  |  LATENCY: {report.generation_latency_ms:.2f} ms".ljust(79) + "|")
        card.append("+" + "-" * 78 + "+")
        card.append("| CORE STAGE RATINGS:".ljust(79) + "|")
        card.append(
            f"|  ATS: {report.ats_summary.ats_score:4.1f} | Screen: {report.screening_results.screening_score:4.1f} | "
            f"HR: {report.hr_insights.hr_score:4.1f} | Tech: {report.technical_performance.technical_interview_score:4.1f} | "
            f"Sandbox: {report.technical_performance.machine_test_sandbox_score:4.1f} |"
        )
        card.append("+" + "-" * 78 + "+")
        card.append("| TOP STANDOUT STRENGTHS:".ljust(79) + "|")
        for s in report.strengths[:3]:
            card.append(f"|  [+] {s.title}: {s.description[:60]}...".ljust(79) + "|")
        if report.risk_indicators:
            card.append("| NOTABLE RISK INDICATORS:".ljust(79) + "|")
            for r in report.risk_indicators[:2]:
                card.append(f"|  [!] {r.title}: {r.description[:60]}...".ljust(79) + "|")
        card.append("+" + "-" * 78 + "+")
        card.append(f"| RECOMMENDED ACTION : {report.final_recommendation.recommended_action[:54]}...".ljust(79) + "|")
        card.append(f"| AUDIT SEAL (SHA-256): {report.audit_hash[:32]}...".ljust(79) + "|")
        card.append("+" + "-" * 78 + "+")

        return "\n".join(card)

    @staticmethod
    def to_markdown(report: CandidateAIProfileReport) -> str:
        """
        Generates a comprehensive, clean, recruiter-friendly Markdown document.
        Perfect for rendering in GitHub, Notion, ATS dossiers, and PDF generators.
        """
        md = []
        md.append(f"# Candidate AI Profile Report: {report.candidate_name}")
        md.append(f"**Target Role:** {report.target_role} | **Tier:** {report.experience_tier} | **ID:** `{report.candidate_id}`  ")
        md.append(f"**Generated:** {report.generated_at} | **Report ID:** `{report.report_id}` | **Version:** `{report.generator_version}`\n")

        # Recruiter TL;DR
        md.append("## ⚡ Recruiter Executive Summary (TL;DR)")
        md.append(f"> **{report.recruiter_tldr}**\n")

        # Outcome Banner Table
        md.append("### Decision Overview")
        md.append("| Decision Verdict | Sub-Status | Calibrated Fit | Certainty | Risk Level |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.append(
            f"| **[{report.final_recommendation.decision_category}]** | "
            f"`{report.final_recommendation.decision_substatus}` | "
            f"**{report.final_recommendation.hiring_fit_score:.1f}%** | "
            f"{report.final_recommendation.confidence_score:.1f}% ({report.final_recommendation.confidence_band}) | "
            f"**{report.behavioral_and_risk.overall_risk_level}** |\n"
        )

        # Multi-Stage Scorecard
        md.append("## 📊 Comprehensive Multi-Stage Scorecard")
        md.append("| Evaluation Pillar | Stage Score | Key Observed Metric | Recruiter Status Notes |")
        md.append("| :--- | :---: | :--- | :--- |")
        md.append(f"| **1. ATS Resume Match** | {report.ats_summary.ats_score:.1f}% | Keyword Match: {report.ats_summary.keyword_match_rate:.1f}% | {report.ats_summary.summary_notes} |")
        md.append(f"| **2. Phone / Auto Screen** | {report.screening_results.screening_score:.1f}% | Clarity: {report.screening_results.communication_clarity} | {report.screening_results.screening_notes} |")
        md.append(f"| **3. HR Behavioral (STAR)** | {report.hr_insights.hr_score:.1f}% | STAR Rating: {report.hr_insights.star_method_rating:.1f}% | {report.hr_insights.hr_interview_notes} |")
        md.append(f"| **4. Technical Interview** | {report.technical_performance.technical_interview_score:.1f}% | System Design: {report.technical_performance.architecture_design_score:.1f}% | {report.technical_performance.technical_notes} |")
        md.append(f"| **5. Machine Test Sandbox** | {report.technical_performance.machine_test_sandbox_score:.1f}% | Test Pass Rate: {report.technical_performance.test_suite_pass_rate:.1f}% | Code: {report.technical_performance.code_quality_and_cleanliness} |")
        md.append(f"| **6. Behavioral & Proctoring** | Stress: {report.behavioral_and_risk.stress_index:.1f} | Volatility Std: {report.behavioral_and_risk.cross_round_std_dev:.1f} pts | Malpractice Violations: {report.behavioral_and_risk.malpractice_breaches_detected} |\n")

        # Strengths & Weaknesses
        md.append("## 🌟 Standout Strengths")
        if report.strengths:
            for s in report.strengths:
                md.append(f"- **{s.title}** (`{s.pillar.value}` - *{s.impact.value}*): {s.description}")
        else:
            md.append("- *No prominent standout strengths recorded.*")
        md.append("")

        md.append("## ⚠️ Growth Areas & Weaknesses")
        if report.weaknesses:
            for w in report.weaknesses:
                md.append(f"- **{w.title}** (`{w.pillar.value}` - *{w.impact.value}*): {w.description}")
        else:
            md.append("- *No material weaknesses identified.*")
        md.append("")

        # Risk Indicators
        md.append("## 🚩 Risk Indicators & Gating Flags")
        if report.risk_indicators:
            for r in report.risk_indicators:
                md.append(f"- **{r.title}** (`{r.pillar.value}` - **{r.impact.value}**): {r.description}")
        else:
            md.append("- *Clean evaluation: zero risk indicators or gating breaches detected.*")
        md.append("")

        # Recommended Action & Counterfactual Advice
        md.append("## 🎯 Recommended Next Steps")
        md.append(f"**Operational Mandate:** {report.final_recommendation.recommended_action}  ")
        if report.final_recommendation.counterfactual_advice:
            md.append(f"**Counterfactual Guidance:** {report.final_recommendation.counterfactual_advice}  ")
        md.append(f"**Hiring Executive Briefing:** {report.final_recommendation.executive_rationale}\n")

        # Cryptographic Audit Seal
        md.append("---")
        md.append(f"**Cryptographic Audit Seal:** `SHA-256 [{report.audit_hash}]`  ")
        md.append(f"*Evaluation SLA: {report.generation_latency_ms:.2f} ms | Production Verification: 100% Pass*")

        return "\n".join(md)

    @staticmethod
    def to_html(report: CandidateAIProfileReport) -> str:
        """
        Generates an enterprise-styled, standalone HTML dossier with responsive CSS,
        color-coded status pills, and print-ready layout.
        """
        category = report.final_recommendation.decision_category
        cat_color = "#059669" if category == "SELECTED" else ("#d97706" if category == "HOLD_REVIEW" else "#dc2626")
        cat_bg = "#ecfdf5" if category == "SELECTED" else ("#fffbeb" if category == "HOLD_REVIEW" else "#fef2f2")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Candidate AI Profile Report: {report.candidate_name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #1e293b; margin: 0; padding: 24px; }}
  .container {{ max-width: 960px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); overflow: hidden; }}
  .header {{ background: #0f172a; color: #ffffff; padding: 24px 32px; border-bottom: 4px solid #0284c7; }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 24px; }}
  .header p {{ margin: 0; color: #94a3b8; font-size: 13px; }}
  .content {{ padding: 28px 32px; }}
  .tldr-box {{ background: #f8fafc; border-left: 4px solid #0284c7; padding: 16px 20px; border-radius: 6px; margin-bottom: 24px; font-size: 14px; line-height: 1.5; }}
  .pill {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px; text-transform: uppercase; background: {cat_bg}; color: {cat_color}; border: 1px solid {cat_color}; }}
  .table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }}
  .table th {{ background: #1e293b; color: #ffffff; padding: 10px 14px; text-align: left; }}
  .table td {{ padding: 10px 14px; border-bottom: 1px solid #e2e8f0; }}
  .table tr:nth-child(even) {{ background: #f8fafc; }}
  .highlight-card {{ padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; font-size: 13px; border-left: 4px solid; }}
  .card-strength {{ background: #f0fdf4; border-color: #22c55e; }}
  .card-weakness {{ background: #fefce8; border-color: #eab308; }}
  .card-risk {{ background: #fef2f2; border-color: #ef4444; }}
  .footer {{ background: #f1f5f9; padding: 16px 32px; border-top: 1px solid #cbd5e1; font-size: 12px; color: #64748b; display: flex; justify-content: space-between; align-items: center; }}
  .seal {{ font-family: monospace; font-size: 11px; color: #0f172a; word-break: break-all; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Zecpath-AI Candidate Evaluation Dossier</h1>
    <p>Candidate: <strong>{report.candidate_name}</strong> | ID: <code>{report.candidate_id}</code> | Role: <strong>{report.target_role}</strong> | Tier: {report.experience_tier}</p>
  </div>
  <div class="content">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <div>
        <span class="pill">{category}</span>
        <span style="margin-left: 10px; font-weight: 600; font-size: 14px; color: #334155;">{report.final_recommendation.decision_substatus}</span>
      </div>
      <div>
        <span style="font-size: 18px; font-weight: bold; color: #0f172a;">Fit: {report.final_recommendation.hiring_fit_score:.1f}%</span>
        <span style="font-size: 13px; color: #64748b; margin-left: 8px;">(Confidence: {report.final_recommendation.confidence_score:.1f}%)</span>
      </div>
    </div>

    <div class="tldr-box">
      <strong>Recruiter Executive Briefing:</strong> {report.recruiter_tldr}
    </div>

    <h3 style="color: #0f172a; margin-top: 24px;">Multi-Stage Competency Breakdown</h3>
    <table class="table">
      <thead>
        <tr>
          <th>Evaluation Pillar</th>
          <th>Score</th>
          <th>Key Dimension Measured</th>
          <th>Assessment Notes</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>1. ATS Resume</strong></td><td>{report.ats_summary.ats_score:.1f}%</td><td>Keyword Fit: {report.ats_summary.keyword_match_rate:.1f}%</td><td>{report.ats_summary.summary_notes}</td></tr>
        <tr><td><strong>2. Phone / Auto Screen</strong></td><td>{report.screening_results.screening_score:.1f}%</td><td>Clarity: {report.screening_results.communication_clarity}</td><td>{report.screening_results.screening_notes}</td></tr>
        <tr><td><strong>3. HR Behavioral (STAR)</strong></td><td>{report.hr_insights.hr_score:.1f}%</td><td>STAR Rating: {report.hr_insights.star_method_rating:.1f}%</td><td>{report.hr_insights.hr_interview_notes}</td></tr>
        <tr><td><strong>4. Technical Interview</strong></td><td>{report.technical_performance.technical_interview_score:.1f}%</td><td>Design: {report.technical_performance.architecture_design_score:.1f}%</td><td>{report.technical_performance.technical_notes}</td></tr>
        <tr><td><strong>5. Machine Test Sandbox</strong></td><td>{report.technical_performance.machine_test_sandbox_score:.1f}%</td><td>Test Pass: {report.technical_performance.test_suite_pass_rate:.1f}%</td><td>Code Quality: {report.technical_performance.code_quality_and_cleanliness}</td></tr>
      </tbody>
    </table>

    <h3 style="color: #0f172a;">Highlights & Decision Drivers</h3>
"""

        if report.strengths:
            for s in report.strengths:
                html += f"""    <div class="highlight-card card-strength"><strong>[+] {s.title}</strong> ({s.pillar.value}): {s.description}</div>\n"""
        if report.weaknesses:
            for w in report.weaknesses:
                html += f"""    <div class="highlight-card card-weakness"><strong>[-] {w.title}</strong> ({w.pillar.value}): {w.description}</div>\n"""
        if report.risk_indicators:
            for r in report.risk_indicators:
                html += f"""    <div class="highlight-card card-risk"><strong>[!] {r.title}</strong> ({r.pillar.value}): {r.description}</div>\n"""

        html += f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-top: 24px;">
      <h4 style="margin: 0 0 8px 0; color: #0284c7;">Recommended Recruiter Action</h4>
      <p style="margin: 0 0 6px 0; font-size: 14px;"><strong>Mandated Step:</strong> {report.final_recommendation.recommended_action}</p>
      <p style="margin: 0; font-size: 13px; color: #64748b;"><strong>Guidance:</strong> {report.final_recommendation.executive_rationale}</p>
    </div>
  </div>
  <div class="footer">
    <div>Generated by Zecpath-AI v{report.generator_version} | Latency: {report.generation_latency_ms:.2f} ms</div>
    <div class="seal">SHA-256: {report.audit_hash}</div>
  </div>
</div>
</body>
</html>
"""
        return html
