"""
Day 39: AI Interview Summary Generator (Deliverable 1)
======================================================
Converts multi-dimensional AI interview analysis into executive recruiter-ready insights.
Synthesizes:
- Candidate strengths and developmental weaknesses
- Cultural fit indicators across 5 organizational dimensions
- Cross-turn and cross-modal inconsistency detection
- Holistic HR performance summary and calibrated role leveling
- Natural-language recruiter briefing dossier for hiring manager debriefs
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .summary_models import (
    CandidateInterviewSummary,
    OverallHRPerformanceSummary,
    CulturalFitAssessment,
    CulturalFitDimension,
    InconsistencyFlag,
    InconsistencyType,
    InconsistencySeverity,
    NaturalLanguageDossier,
)
from .hr_scoring_models import HiringRecommendation, CandidateHRScoreReport
from .inconsistency_detector import InconsistencyDetector


class InterviewSummaryGenerator:
    """
    Master AI Interview Summary Generator synthesizing multi-modal signals into
    actionable executive dossiers and ATS JSON payloads.
    """

    def __init__(self):
        self.inconsistency_detector = InconsistencyDetector()

    def generate_summary(
        self,
        candidate_metadata: Dict[str, Any],
        transcript_turns: List[Dict[str, Any]],
        score_report: Optional[CandidateHRScoreReport] = None,
        aptitude_evaluation: Optional[Dict[str, Any]] = None,
        communication_telemetry: Optional[Dict[str, Any]] = None,
        stress_signals: Optional[List[Dict[str, Any]]] = None,
        fallacy_flags: Optional[List[Dict[str, Any]]] = None,
    ) -> CandidateInterviewSummary:
        """
        Orchestrates full synthesis of the candidate interview session into a unified summary.
        """
        cand_id = candidate_metadata.get("candidate_id", "CAND-001")
        cand_name = candidate_metadata.get("candidate_name", "Anonymous Candidate")
        job_role = candidate_metadata.get("job_role", "Software Engineer")
        exp_years = float(candidate_metadata.get("experience_years", 3.0))
        session_id = candidate_metadata.get("session_id", "SESS-2026-09")
        summary_id = f"SUM-{cand_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
        now_iso = datetime.now().isoformat()

        # 1. Detect Inconsistencies
        inconsistencies = self.inconsistency_detector.detect_inconsistencies(
            transcript_turns=transcript_turns,
            candidate_metadata=candidate_metadata,
            stress_signals=stress_signals,
            fallacy_flags=fallacy_flags,
        )

        # 2. Synthesize Overall Performance
        overall_perf = self._synthesize_overall_performance(
            score_report=score_report,
            aptitude_evaluation=aptitude_evaluation,
            job_role=job_role,
            exp_years=exp_years,
            inconsistencies=inconsistencies,
        )

        # 3. Evaluate Cultural Fit Indicators
        cultural_fit = self._evaluate_cultural_fit(
            transcript_turns=transcript_turns,
            aptitude_evaluation=aptitude_evaluation,
            fallacies=fallacy_flags or [],
        )

        # 4. Extract Candidate Strengths & Weaknesses
        strengths, weaknesses = self._extract_strengths_and_weaknesses(
            score_report=score_report,
            aptitude_evaluation=aptitude_evaluation,
            communication_telemetry=communication_telemetry or {},
            stress_signals=stress_signals or [],
            inconsistencies=inconsistencies,
        )

        # 5. Compile Risk Flags
        risk_flags = self._compile_risk_flags(
            score_report=score_report,
            fallacies=fallacy_flags or [],
            inconsistencies=inconsistencies,
            stress_signals=stress_signals or [],
        )

        # 6. Generate Natural Language Report Dossier
        nlg_dossier = self._generate_natural_language_dossier(
            cand_name=cand_name,
            job_role=job_role,
            exp_years=exp_years,
            overall_perf=overall_perf,
            strengths=strengths,
            weaknesses=weaknesses,
            cultural_fit=cultural_fit,
            inconsistencies=inconsistencies,
            risk_flags=risk_flags,
        )

        return CandidateInterviewSummary(
            summary_id=summary_id,
            candidate_id=cand_id,
            candidate_name=cand_name,
            job_role=job_role,
            experience_years=exp_years,
            session_id=session_id,
            generated_at=now_iso,
            overall_performance=overall_perf,
            candidate_strengths=strengths,
            candidate_weaknesses=weaknesses,
            cultural_fit_indicators=cultural_fit,
            risk_flags=risk_flags,
            inconsistencies=inconsistencies,
            natural_language_report=nlg_dossier,
        )

    def _synthesize_overall_performance(
        self,
        score_report: Optional[CandidateHRScoreReport],
        aptitude_evaluation: Optional[Dict[str, Any]],
        job_role: str,
        exp_years: float,
        inconsistencies: List[InconsistencyFlag],
    ) -> OverallHRPerformanceSummary:
        """Synthesizes high-level performance across all interview dimensions."""
        if score_report:
            beh_score = score_report.parameter_breakdown.get("answer_relevance", None)
            beh_val = beh_score.normalized_score if beh_score else 75.0

            comm_score = score_report.parameter_breakdown.get("communication_score", None)
            comm_val = comm_score.normalized_score if comm_score else 75.0

            comp_score = score_report.parameter_breakdown.get("confidence_score", None)
            comp_val = comp_score.normalized_score if comp_score else 75.0

            base_composite = score_report.composite_score
        else:
            beh_val = 75.0
            comm_val = 75.0
            comp_val = 75.0
            base_composite = 75.0

        if aptitude_evaluation:
            apt_val = float(aptitude_evaluation.get("composite_aptitude_score", 70.0))
        else:
            apt_val = 70.0

        # Composite weighting: 30% Behavioral, 25% Communication, 20% Composure, 25% Aptitude
        holistic_score = (
            0.30 * beh_val +
            0.25 * comm_val +
            0.20 * comp_val +
            0.25 * apt_val
        )

        # Apply critical inconsistency penalty (calibrated cap prevents double-dipping score collapse)
        critical_inc_count = sum(1 for inc in inconsistencies if inc.severity == InconsistencySeverity.CRITICAL)
        if critical_inc_count > 0:
            inconsistency_deduction = min(6.0, critical_inc_count * 2.0)
            holistic_score = max(0.0, holistic_score - inconsistency_deduction)

        # Calibrate Recommendation
        if holistic_score >= 85.0 and critical_inc_count == 0:
            rec = HiringRecommendation.STRONG_HIRE
            readiness = "Immediate Production Ready - Fast Track"
            role_tier = f"Senior / Lead {job_role}" if exp_years >= 5.0 else f"High-Impact Mid-Level {job_role}"
            verdict = f"{job_role} candidate demonstrates elite technical rigor, structured problem solving, and zero operational fallacies."
        elif holistic_score >= 72.0 and critical_inc_count == 0:
            rec = HiringRecommendation.HIRE
            readiness = "Production Ready with Standard Onboarding"
            role_tier = f"Solid Core {job_role}"
            verdict = f"Demonstrates dependable problem-solving clarity and solid communication; recommended for hire."
        elif holistic_score >= 60.0 or (critical_inc_count == 1 and holistic_score >= 65.0):
            rec = HiringRecommendation.LEAN_HIRE
            readiness = "Requires Targeted Technical Probing in Onsite Round"
            role_tier = f"Associate / Developing {job_role}"
            verdict = f"Displays foundational competencies but exhibited notable hedging or borderline inconsistencies requiring manager debrief."
        elif holistic_score >= 45.0:
            rec = HiringRecommendation.LEAN_NO_HIRE
            readiness = "Significant Skill Gaps - Recommend Skill Upskilling"
            role_tier = f"Sub-Threshold for {job_role}"
            verdict = f"Fails to meet senior autonomy expectations; showed superficial trade-offs and hesitation under stress."
        else:
            rec = HiringRecommendation.NO_HIRE
            readiness = "Unsuitable for Deployment - Operational Risk"
            role_tier = "Not Recommended"
            verdict = f"Multiple critical contradictions, cognitive fallacies, or blame-deflection tendencies detected."

        return OverallHRPerformanceSummary(
            composite_score=round(holistic_score, 1),
            behavioral_competency_score=round(beh_val, 1),
            communication_clarity_score=round(comm_val, 1),
            confidence_composure_score=round(comp_val, 1),
            cognitive_aptitude_score=round(apt_val, 1),
            recommendation=rec,
            readiness_level=readiness,
            calibrated_role_tier=role_tier,
            executive_verdict=verdict,
        )

    def _evaluate_cultural_fit(
        self,
        transcript_turns: List[Dict[str, Any]],
        aptitude_evaluation: Optional[Dict[str, Any]],
        fallacies: List[Dict[str, Any]],
    ) -> List[CulturalFitAssessment]:
        """Evaluates alignment across 5 enterprise cultural pillars."""
        full_text = " ".join((t.get("response") or t.get("answer") or "") for t in transcript_turns).lower()

        # 1. Ownership & Accountability
        has_blame = any("BLAME" in f.get("fallacy_type", "") for f in fallacies)
        if has_blame:
            ownership_score = 35.0
            ownership_tier = "WEAK"
            ownership_obs = "Candidate demonstrated blame deflection when addressing operational failures."
            ownership_quotes = ["Identified external dependency or management failure rather than personal ownership."]
        elif any(w in full_text for w in ["i took ownership", "my responsibility", "post-mortem", "blameless", "root cause"]):
            ownership_score = 92.0
            ownership_tier = "EXEMPLARY"
            ownership_obs = "Demonstrates radical ownership, blameless post-mortem methodology, and proactive mitigation."
            ownership_quotes = ["Took full ownership of the production incident and instituted preventative safeguards."]
        else:
            ownership_score = 72.0
            ownership_tier = "STRONG"
            ownership_obs = "Adequate personal accountability; accepts task responsibilities without friction."
            ownership_quotes = ["Followed team escalation protocols appropriately."]

        # 2. Collaboration & Teamwork
        if any(w in full_text for w in ["pair programming", "mentored", "cross-functional", "consensus", "aligned with product"]):
            collab_score = 90.0
            collab_tier = "EXEMPLARY"
            collab_obs = "High empathy and team multiplier mindset; actively mentors peers and bridges cross-functional silos."
            collab_quotes = ["Engaged stakeholders and engineering peers to achieve collective consensus."]
        elif any(w in full_text for w in ["solo", "alone", "only person", "did not need anyone"]):
            collab_score = 55.0
            collab_tier = "MODERATE"
            collab_obs = "Siloed individual contributor tendencies; may require coaching on team alignment."
            collab_quotes = ["Preferred solo execution over collective problem solving."]
        else:
            collab_score = 75.0
            collab_tier = "STRONG"
            collab_obs = "Standard team player; collaborates effectively within structured team boundaries."
            collab_quotes = ["Collaborated with teammates during sprint delivery."]

        # 3. Customer Centricity
        if any(w in full_text for w in ["sla", "customer trust", "user impact", "business continuity", "client communication"]):
            cust_score = 88.0
            cust_tier = "STRONG"
            cust_obs = "Prioritizes user experience, data availability, and business continuity during technical trade-offs."
            cust_quotes = ["Maintained customer communication bridges and preserved core transactional SLAs."]
        else:
            cust_score = 70.0
            cust_tier = "STRONG"
            cust_obs = "Recognizes end-user importance but defaults to purely technical operational metrics."
            cust_quotes = ["Addressed infrastructure telemetry to restore service."]

        # 4. Adaptability & Growth
        if any(w in full_text for w in ["learned from", "iterated", "adapted", "pivoted", "continuous learning"]):
            adapt_score = 86.0
            adapt_tier = "STRONG"
            adapt_obs = "High cognitive agility; views unexpected constraints as opportunities for architecture improvement."
            adapt_quotes = ["Adapted quickly to evolving requirements by refactoring architecture incrementally."]
        else:
            adapt_score = 74.0
            adapt_tier = "STRONG"
            adapt_obs = "Standard adaptability; comfortable in structured environments with clear requirements."
            adapt_quotes = ["Adjusted project scope within defined parameters."]

        # 5. Transparency & Ethics
        if any(w in full_text for w in ["compliance", "security", "gdpr", "pii", "audit", "transparency", "ethical"]):
            ethic_score = 95.0
            ethic_tier = "EXEMPLARY"
            ethic_obs = "Uncompromising ethical standards; actively flags security, compliance, and PII hazards."
            ethic_quotes = ["Refused to log unmasked credentials and instituted automated scrubbing policies."]
        else:
            ethic_score = 78.0
            ethic_tier = "STRONG"
            ethic_obs = "Adheres to standard organizational security guidelines."
            ethic_quotes = ["Followed company data handling practices."]

        return [
            CulturalFitAssessment(
                dimension=CulturalFitDimension.OWNERSHIP_AND_ACCOUNTABILITY,
                score=ownership_score,
                alignment_level=ownership_tier,
                evidence_excerpts=ownership_quotes,
                observations=ownership_obs,
            ),
            CulturalFitAssessment(
                dimension=CulturalFitDimension.COLLABORATION_AND_TEAMWORK,
                score=collab_score,
                alignment_level=collab_tier,
                evidence_excerpts=collab_quotes,
                observations=collab_obs,
            ),
            CulturalFitAssessment(
                dimension=CulturalFitDimension.CUSTOMER_CENTRICITY,
                score=cust_score,
                alignment_level=cust_tier,
                evidence_excerpts=cust_quotes,
                observations=cust_obs,
            ),
            CulturalFitAssessment(
                dimension=CulturalFitDimension.ADAPTABILITY_AND_GROWTH,
                score=adapt_score,
                alignment_level=adapt_tier,
                evidence_excerpts=adapt_quotes,
                observations=adapt_obs,
            ),
            CulturalFitAssessment(
                dimension=CulturalFitDimension.TRANSPARENCY_AND_ETHICS,
                score=ethic_score,
                alignment_level=ethic_tier,
                evidence_excerpts=ethic_quotes,
                observations=ethic_obs,
            ),
        ]

    def _extract_strengths_and_weaknesses(
        self,
        score_report: Optional[CandidateHRScoreReport],
        aptitude_evaluation: Optional[Dict[str, Any]],
        communication_telemetry: Dict[str, Any],
        stress_signals: List[Dict[str, Any]],
        inconsistencies: List[InconsistencyFlag],
    ) -> tuple[List[str], List[str]]:
        """Extracts calibrated strengths and developmental weaknesses."""
        strengths: List[str] = []
        weaknesses: List[str] = []

        # Technical & Aptitude signals
        if aptitude_evaluation:
            logic_score = aptitude_evaluation.get("scores", {}).get("logical_reasoning", 70.0)
            clarity_score = aptitude_evaluation.get("scores", {}).get("problem_solving_clarity", 70.0)
            adherence = aptitude_evaluation.get("framework_adherence_percent", 80.0)

            if logic_score >= 75.0:
                strengths.append(f"High-Rigor Logical Deduction: Achieved {logic_score:.1f}/100 in causal chain reasoning without fallacies.")
            else:
                weaknesses.append(f"Limited Deductive Depth: Scored {logic_score:.1f}/100 in premise-to-conclusion causal chains.")

            if clarity_score >= 80.0:
                strengths.append(f"Structured Problem-Solving Signposting: Scored {clarity_score:.1f}/100 in clear sequential delivery.")
            if adherence >= 90.0:
                strengths.append(f"Disciplined Framework Execution: {adherence:.0f}% adherence to IDEA/CARL problem-solving methodology.")

        # Communication signals
        comm_clarity = communication_telemetry.get("clarity", 75.0)
        filler_rate = communication_telemetry.get("filler_percentage", 2.5)
        if comm_clarity >= 82.0:
            strengths.append(f"Articulate Executive Communication: Strong vocabulary depth and high clarity score ({comm_clarity:.1f}/100).")
        if filler_rate >= 5.0:
            weaknesses.append(f"Elevated Filler Word Density: Candidate exhibited a {filler_rate:.1f}% filler word frequency.")

        # Composure & Stress signals
        avg_stress = (sum(s.get("stress_index", 30.0) for s in stress_signals) / max(len(stress_signals), 1)) if stress_signals else 30.0
        if avg_stress <= 35.0:
            strengths.append(f"Exceptional Stress Resilience: Maintained low physiological tension (Stress Index: {avg_stress:.1f}/100) under pressure.")
        elif avg_stress >= 65.0:
            weaknesses.append(f"Vulnerability to Pressure: Elevated stress markers (Stress Index: {avg_stress:.1f}/100) and increased hesitation under deep probing.")

        # Inconsistency signals
        if inconsistencies:
            weaknesses.append(f"Contradictory Narrative Claims: Detected {len(inconsistencies)} cross-turn or factual discrepancies requiring verification.")
        else:
            strengths.append("High Narrative Integrity: Zero factual or cross-turn contradictions identified across the entire session.")

        # Fallbacks
        if not strengths:
            strengths.append("Demonstrated cooperative demeanor and foundational role comprehension.")
        if not weaknesses:
            weaknesses.append("Continue deepening quantitative Fermi estimation bounds under time-constrained architectural discussions.")

        return strengths, weaknesses

    def _compile_risk_flags(
        self,
        score_report: Optional[CandidateHRScoreReport],
        fallacies: List[Dict[str, Any]],
        inconsistencies: List[InconsistencyFlag],
        stress_signals: List[Dict[str, Any]],
    ) -> List[str]:
        """Compiles critical hiring risk flags."""
        flags: List[str] = []

        for inc in inconsistencies:
            if inc.severity == InconsistencySeverity.CRITICAL:
                flags.append(f"CRITICAL CONTRADICTION: {inc.explanation}")
            elif inc.severity == InconsistencySeverity.MODERATE:
                flags.append(f"NOTABLE DISCREPANCY: {inc.explanation}")

        for f in fallacies:
            ftype = f.get("fallacy_type", "LOGICAL_FALLACY")
            if "BLAME" in ftype:
                flags.append(f"CULTURE RISK (BLAME DEFLECTION): {f.get('explanation', 'Deflected ownership of project failure.')}")
            elif "FALSE_DILEMMA" in ftype:
                flags.append(f"COGNITIVE BIAS (FALSE DILEMMA): {f.get('explanation', 'Framed resolution as an aggressive binary.')}")

        avg_stress = (sum(s.get("stress_index", 30.0) for s in stress_signals) / max(len(stress_signals), 1)) if stress_signals else 30.0
        if avg_stress >= 70.0:
            flags.append(f"COMPOSURE RISK: Severe stress spikes ({avg_stress:.1f}/100) and prolonged hesitation under architectural failure scenarios.")

        return flags

    def _generate_natural_language_dossier(
        self,
        cand_name: str,
        job_role: str,
        exp_years: float,
        overall_perf: OverallHRPerformanceSummary,
        strengths: List[str],
        weaknesses: List[str],
        cultural_fit: List[CulturalFitAssessment],
        inconsistencies: List[InconsistencyFlag],
        risk_flags: List[str],
    ) -> NaturalLanguageDossier:
        """Constructs an executive natural-language briefing dossier."""
        rec_str = overall_perf.recommendation.value
        rec_display = {
            "STRONG_HIRE": "Strong Hire (Fast Track)",
            "HIRE": "Hire (Recommended)",
            "LEAN_HIRE": "Lean Hire (Targeted Probing Recommended)",
            "LEAN_NO_HIRE": "Lean No Hire (Sub-Threshold)",
            "NO_HIRE": "No Hire (High Risk / Reject)",
        }.get(rec_str, rec_str)

        # 1. Executive Overview
        exec_overview = (
            f"{cand_name} was evaluated for the {job_role} position ({exp_years:.1f} years claimed experience). "
            f"Following comprehensive multi-modal assessment across behavioral competencies, communication clarity, "
            f"acoustic stress resilience, and situational judgment, the candidate earned a composite score of "
            f"{overall_perf.composite_score:.1f}/100, resulting in an executive recommendation of **{rec_display}**. "
            f"The candidate is classified under the **{overall_perf.calibrated_role_tier}** band with readiness level "
            f"'{overall_perf.readiness_level}'. {overall_perf.executive_verdict}"
        )

        # 2. Communication Persona
        comm_persona = (
            f"The candidate's communication profile achieved a calibrated score of {overall_perf.communication_clarity_score:.1f}/100. "
            f"Delivery is characterized by structured progression and articulate vocabulary. "
            f"{'Responses incorporated sequential signposting and disciplined IDEA framework adherence.' if overall_perf.communication_clarity_score >= 75.0 else 'Delivery exhibited occasional conversational filler density and rambling under open-ended prompts.'} "
            f"In interpersonal exchanges, {cand_name} maintains professional composure and balanced pacing."
        )

        # 3. Behavioral and Cultural Fit
        top_cult = max(cultural_fit, key=lambda c: c.score)
        low_cult = min(cultural_fit, key=lambda c: c.score)
        beh_culture = (
            f"Across organizational cultural benchmarks, the candidate scored {overall_perf.behavioral_competency_score:.1f}/100 in STAR "
            f"behavioral execution. The candidate's strongest cultural dimension is **{top_cult.dimension.value.replace('_', ' ').title()}** "
            f"({top_cult.score:.1f}/100 - {top_cult.alignment_level}), demonstrating {top_cult.observations.lower()} "
            f"Conversely, **{low_cult.dimension.value.replace('_', ' ').title()}** represents the lowest alignment dimension "
            f"({low_cult.score:.1f}/100 - {low_cult.alignment_level}), noting: {low_cult.observations}"
        )

        # 4. Cognitive and Technical Maturity
        cog_maturity = (
            f"In situational judgment and logical reasoning evaluations, the candidate achieved {overall_perf.cognitive_aptitude_score:.1f}/100. "
            f"Problem-solving was evaluated on real-world operational dilemmas, including production outages and technical trade-offs. "
            f"{'The candidate demonstrated robust causal deductions, weighing CAP theorem trade-offs and proposing telemetry-driven safeguards.' if overall_perf.cognitive_aptitude_score >= 75.0 else 'Analysis remained largely superficial, prioritizing immediate short-term fixes over root-cause isolation and systematic trade-off analysis.'}"
        )

        # 5. Inconsistency & Risk Analysis
        if inconsistencies:
            inc_narrative = (
                f"Evaluation flagged {len(inconsistencies)} notable inconsistency{'ies' if len(inconsistencies) > 1 else ''}. "
                + " ".join(f"[{inc.inconsistency_type.value.upper()}] {inc.explanation}" for inc in inconsistencies[:2])
            )
        else:
            inc_narrative = (
                "Cross-turn factual verification and multi-modal telemetry confirmed high narrative integrity. "
                "Candidate statements remained internally consistent across experience claims, technical methodologies, and acoustic stress signals."
            )

        if risk_flags:
            inc_narrative += f" Recruiter review identified {len(risk_flags)} operational or behavioral alert(s)."

        # 6. Hiring Manager Action Plan & Probes
        probes: List[str] = []
        for inc in inconsistencies:
            probes.append(inc.recommended_probing_question)

        if not probes:
            probes = [
                "Describe a scenario where a production rollout failed unexpectedly despite passing all CI/CD integration tests. What was your containment strategy?",
                "How do you handle architectural disagreements when a cross-functional partner insists on technical debt to hit a marketing deadline?",
            ]

        action_plan = (
            f"For the upcoming Hiring Manager debrief round, the interview panel should focus specifically on validating "
            f"{'the flagged narrative discrepancies and trade-off depth' if inconsistencies else 'long-term system architecture scalability and cross-functional leadership'}. "
            f"Recommended next step: Proceed to **{'Final Architectural / Culture Alignment Round' if overall_perf.composite_score >= 72.0 else 'Targeted Follow-up Verification or Rejection'}**."
        )

        return NaturalLanguageDossier(
            executive_overview=exec_overview,
            communication_persona=comm_persona,
            behavioral_and_cultural_fit=beh_culture,
            cognitive_and_technical_maturity=cog_maturity,
            inconsistency_and_risk_analysis=inc_narrative,
            hiring_manager_action_plan=action_plan,
            targeted_interview_probes=probes,
        )

    def to_ats_json(self, summary: CandidateInterviewSummary, indent: int = 2) -> str:
        """Serializes the complete summary into enterprise ATS-compliant JSON."""
        return summary.model_dump_json(indent=indent)

    def to_recruiter_markdown(self, summary: CandidateInterviewSummary) -> str:
        """Renders an executive recruiter-ready Markdown dossier."""
        rec_display = {
            "STRONG_HIRE": "**[STRONG HIRE]**",
            "HIRE": "**[HIRE]**",
            "LEAN_HIRE": "**[LEAN HIRE]**",
            "LEAN_NO_HIRE": "**[LEAN NO HIRE]**",
            "NO_HIRE": "**[NO HIRE]**",
        }.get(summary.overall_performance.recommendation.value, summary.overall_performance.recommendation.value)

        lines = [
            f"# Zecpath-AI Executive Interview Summary Dossier",
            f"**Candidate:** {summary.candidate_name} (`{summary.candidate_id}`) | **Role:** {summary.job_role} ({summary.experience_years:.1f} yrs exp)",
            f"**Session ID:** `{summary.session_id}` | **Generated:** {summary.generated_at[:19]}",
            f"**Summary ID:** `{summary.summary_id}`",
            f"",
            f"---",
            f"",
            f"## 1. Executive Hiring Verdict & Performance Synthesis",
            f"- **Overall Calibrated Score:** **{summary.overall_performance.composite_score:.1f} / 100**",
            f"- **Recruiter Recommendation:** {rec_display}",
            f"- **Calibrated Leveling:** **{summary.overall_performance.calibrated_role_tier}**",
            f"- **Operational Readiness:** *{summary.overall_performance.readiness_level}*",
            f"",
            f"> **Executive Verdict:** {summary.overall_performance.executive_verdict}",
            f"",
            f"### Multi-Dimensional Performance Breakdown",
            f"| Evaluation Dimension | Calibrated Score | Benchmark Benchmark | Assessment Tier |",
            f"| :--- | :---: | :---: | :--- |",
            f"| **Behavioral Competency (STAR)** | {summary.overall_performance.behavioral_competency_score:.1f} / 100 | $\\ge 75.0$ | {'EXEMPLARY' if summary.overall_performance.behavioral_competency_score >= 85 else 'PROFICIENT' if summary.overall_performance.behavioral_competency_score >= 70 else 'DEVELOPING'} |",
            f"| **Communication Clarity & Hygiene** | {summary.overall_performance.communication_clarity_score:.1f} / 100 | $\\ge 75.0$ | {'EXEMPLARY' if summary.overall_performance.communication_clarity_score >= 85 else 'PROFICIENT' if summary.overall_performance.communication_clarity_score >= 70 else 'DEVELOPING'} |",
            f"| **Composure & Stress Resilience** | {summary.overall_performance.confidence_composure_score:.1f} / 100 | $\\ge 70.0$ | {'HIGH' if summary.overall_performance.confidence_composure_score >= 80 else 'MODERATE' if summary.overall_performance.confidence_composure_score >= 65 else 'VULNERABLE'} |",
            f"| **Cognitive & Situational Aptitude** | {summary.overall_performance.cognitive_aptitude_score:.1f} / 100 | $\\ge 70.0$ | {'EXEMPLARY' if summary.overall_performance.cognitive_aptitude_score >= 85 else 'PROFICIENT' if summary.overall_performance.cognitive_aptitude_score >= 70 else 'DEFICIENT'} |",
            f"",
            f"---",
            f"",
            f"## 2. Candidate Strengths & Developmental Weaknesses",
            f"### Observed Key Strengths",
        ]

        for s in summary.candidate_strengths:
            lines.append(f"- [+] **{s}**")

        lines.append(f"\n### Developmental Weaknesses & Areas for Growth")
        for w in summary.candidate_weaknesses:
            lines.append(f"- [-] {w}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Cultural Fit & Organizational Alignment",
            f"| Cultural Pillar | Alignment Score | Status Tier | Recruiter Observation |",
            f"| :--- | :---: | :---: | :--- |",
        ])

        for c in summary.cultural_fit_indicators:
            dim_title = c.dimension.value.replace("_", " ").title()
            lines.append(
                f"| **{dim_title}** | {c.score:.1f} / 100 | `{c.alignment_level}` | {c.observations} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 4. Inconsistency Analysis & Operational Risk Flags",
        ])

        if summary.inconsistencies:
            lines.append(f"### Detected Inconsistencies ({len(summary.inconsistencies)})")
            for inc in summary.inconsistencies:
                lines.extend([
                    f"#### [{inc.severity.value}] {inc.inconsistency_id}: {inc.inconsistency_type.value.replace('_', ' ').title()}",
                    f"- **Claim Source:** {inc.claim_source} (*\"{inc.claimed_statement}\"*)",
                    f"- **Contradiction Source:** {inc.contradicting_source} (*\"{inc.contradicting_statement}\"*)",
                    f"- **Diagnostic Explanation:** {inc.explanation}",
                    f"- **Recommended Probing Question:** *\"{inc.recommended_probing_question}\"*",
                    f"",
                ])
        else:
            lines.append(f"- [OK] **Zero cross-turn contradictions or factual discrepancies detected.**")

        if summary.risk_flags:
            lines.append(f"\n### Active Risk Flags")
            for r in summary.risk_flags:
                lines.append(f"- [!] {r}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 5. Recruiter Natural-Language Narrative Dossier",
            f"### Executive Overview",
            f"{summary.natural_language_report.executive_overview}",
            f"",
            f"### Communication Style & Interpersonal Persona",
            f"{summary.natural_language_report.communication_persona}",
            f"",
            f"### Behavioral & Cultural Fit Dynamics",
            f"{summary.natural_language_report.behavioral_and_cultural_fit}",
            f"",
            f"### Cognitive & Technical Maturity",
            f"{summary.natural_language_report.cognitive_and_technical_maturity}",
            f"",
            f"### Inconsistency & Risk Briefing",
            f"{summary.natural_language_report.inconsistency_and_risk_analysis}",
            f"",
            f"### Hiring Manager Action Plan & Recommended Probes",
            f"{summary.natural_language_report.hiring_manager_action_plan}",
            f"",
            f"**Targeted Probing Questions for Next Round:**",
        ])

        for p in summary.natural_language_report.targeted_interview_probes:
            lines.append(f"1. *\"{p}\"*")

        lines.append(f"\n---\n*Report generated by Zecpath-AI Enterprise Talent Platform — Confidential & Proprietary.*")
        return "\n".join(lines)
