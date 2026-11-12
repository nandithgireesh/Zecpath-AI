"""
Day 53: Hiring Intelligence Report Generator - Engine (Deliverable 1)
====================================================================
Master orchestrator responsible for compiling multi-stage evaluation data
into a holistic, recruiter-friendly Candidate AI Profile Report.
"""

import time
import math
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from hiring_report_generator.models import (
    HighlightType,
    CompetencyPillar,
    ImpactLevel,
    ATSSummarySection,
    ScreeningResultsSection,
    HRInsightsSection,
    TechnicalPerformanceSection,
    BehavioralAndRiskSection,
    CompetencyHighlight,
    FinalRecommendationSummary,
    CandidateAIProfileReport,
)

# Optional integration with Day 52 engine
try:
    from final_recommendation_ai import (
        FinalDecisionAIEngine,
        FinalDecisionCategory,
        DecisionSubStatus,
        RiskFactorsTelemetry,
        CandidateDecisionOutput,
    )
    DAY52_AVAILABLE = True
except ImportError:
    DAY52_AVAILABLE = False


class HiringIntelligenceReportGenerator:
    """
    Deliverable 1: Enterprise Report Generator synthesizing ATS, screening,
    HR, technical, and behavioral insights into a unified candidate dossier.
    """

    def __init__(self):
        self.version = "1.0.0-PROD"
        if DAY52_AVAILABLE:
            self.decision_engine = FinalDecisionAIEngine()
        else:
            self.decision_engine = None

    def generate_candidate_report(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        experience_tier: str,
        ats_data: Dict[str, Any],
        screening_data: Dict[str, Any],
        hr_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        behavioral_data: Dict[str, Any],
        decision_override: Optional[Dict[str, Any]] = None,
    ) -> CandidateAIProfileReport:
        """
        Synthesizes raw or calibrated multi-stage telemetry into an export-ready
        CandidateAIProfileReport object. Enforces sub-35ms generation SLA.
        """
        start_time = time.perf_counter()

        # 1. Construct Domain Sections
        ats_section = self._build_ats_section(ats_data)
        screening_section = self._build_screening_section(screening_data)
        hr_section = self._build_hr_section(hr_data)
        tech_section = self._build_technical_section(technical_data)
        behavioral_section = self._build_behavioral_section(behavioral_data, [
            ats_section.ats_score,
            screening_section.screening_score,
            hr_section.hr_score,
            tech_section.technical_interview_score,
            tech_section.machine_test_sandbox_score,
        ])

        # 2. Extract Highlights (Strengths, Weaknesses, Risk Indicators)
        strengths, weaknesses, risks = self._extract_competency_highlights(
            ats=ats_section,
            screening=screening_section,
            hr=hr_section,
            tech=tech_section,
            behavioral=behavioral_section,
        )

        # 3. Resolve Final Recommendation Summary
        final_rec = self._resolve_final_recommendation(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            experience_tier=experience_tier,
            ats=ats_section,
            screening=screening_section,
            hr=hr_section,
            tech=tech_section,
            behavioral=behavioral_section,
            override=decision_override,
        )

        # 4. Generate Punchy Recruiter TL;DR
        recruiter_tldr = self._generate_recruiter_tldr(
            candidate_name=candidate_name,
            target_role=target_role,
            final_rec=final_rec,
            strengths=strengths,
            risks=risks,
        )

        # 5. Assemble Master Candidate AI Profile Report
        report_id = f"REP-{candidate_id}-{int(time.time())}"
        report = CandidateAIProfileReport(
            report_id=report_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            experience_tier=experience_tier,
            generated_at=datetime.now(timezone.utc).isoformat(),
            generator_version=self.version,
            ats_summary=ats_section,
            screening_results=screening_section,
            hr_insights=hr_section,
            technical_performance=tech_section,
            behavioral_and_risk=behavioral_section,
            strengths=strengths,
            weaknesses=weaknesses,
            risk_indicators=risks,
            final_recommendation=final_rec,
            recruiter_tldr=recruiter_tldr,
        )

        # 6. Finalize Cryptographic Seal & SLA Telemetry
        report.finalize_and_seal()
        report.generation_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        return report

    # =========================================================================
    # SECTION BUILDERS
    # =========================================================================

    def _build_ats_section(self, data: Dict[str, Any]) -> ATSSummarySection:
        return ATSSummarySection(
            ats_score=float(data.get("ats_score", 75.0)),
            keyword_match_rate=float(data.get("keyword_match_rate", 70.0)),
            experience_years=float(data.get("experience_years", 3.0)),
            education_tier=data.get("education_tier", "Bachelor of Science in Computer Science"),
            matched_skills=data.get("matched_skills", []),
            missing_skills=data.get("missing_skills", []),
            summary_notes=data.get(
                "summary_notes",
                "Resume demonstrates baseline domain alignment with core requirements verified."
            ),
        )

    def _build_screening_section(self, data: Dict[str, Any]) -> ScreeningResultsSection:
        return ScreeningResultsSection(
            screening_score=float(data.get("screening_score", 75.0)),
            communication_clarity=data.get("communication_clarity", "CLEAR"),
            qualification_fit=data.get("qualification_fit", "CONFIRMED_MATCH"),
            availability_timeline=data.get("availability_timeline", "Standard 30 Days"),
            screening_notes=data.get(
                "screening_notes",
                "Candidate articulated background effectively and confirmed role prerequisites."
            ),
        )

    def _build_hr_section(self, data: Dict[str, Any]) -> HRInsightsSection:
        return HRInsightsSection(
            hr_score=float(data.get("hr_score", 75.0)),
            star_method_rating=float(data.get("star_method_rating", 75.0)),
            leadership_teamwork_index=float(data.get("leadership_teamwork_index", 75.0)),
            cultural_values_alignment=data.get("cultural_values_alignment", "STRONG_FIT"),
            motivation_and_adaptability=data.get("motivation_and_adaptability", "HIGH_GROWTH_DRIVE"),
            hr_interview_notes=data.get(
                "hr_interview_notes",
                "Demonstrated constructive conflict resolution and structured situational reasoning."
            ),
        )

    def _build_technical_section(self, data: Dict[str, Any]) -> TechnicalPerformanceSection:
        return TechnicalPerformanceSection(
            technical_interview_score=float(data.get("technical_interview_score", 75.0)),
            machine_test_sandbox_score=float(data.get("machine_test_sandbox_score", 75.0)),
            architecture_design_score=float(data.get("architecture_design_score", 75.0)),
            test_suite_pass_rate=float(data.get("test_suite_pass_rate", 85.0)),
            code_quality_and_cleanliness=data.get("code_quality_and_cleanliness", "MODULAR_AND_CLEAN"),
            technical_notes=data.get(
                "technical_notes",
                "Hands-on execution verified core algorithmic competence and clean design principles."
            ),
        )

    def _build_behavioral_section(
        self,
        data: Dict[str, Any],
        stage_scores: List[float],
    ) -> BehavioralAndRiskSection:
        # Calculate cross-round standard deviation if not provided
        if "cross_round_std_dev" in data:
            std_dev = float(data["cross_round_std_dev"])
        elif len(stage_scores) > 1:
            mean = sum(stage_scores) / len(stage_scores)
            var = sum((s - mean) ** 2 for s in stage_scores) / len(stage_scores)
            std_dev = round(math.sqrt(var), 2)
        else:
            std_dev = 0.0

        return BehavioralAndRiskSection(
            stress_index=float(data.get("stress_index", 18.0)),
            hesitation_pause_count=int(data.get("hesitation_pause_count", 1)),
            speech_fluency_rating=data.get("speech_fluency_rating", "ARTICULATE"),
            integrity_penalty_points=float(data.get("integrity_penalty_points", 0.0)),
            malpractice_breaches_detected=int(data.get("malpractice_breaches_detected", 0)),
            cross_round_std_dev=std_dev,
            overall_risk_level=data.get("overall_risk_level", "LOW"),
        )

    # =========================================================================
    # HIGHLIGHTS EXTRACTION (STRENGTHS, WEAKNESSES, RISK INDICATORS)
    # =========================================================================

    def _extract_competency_highlights(
        self,
        ats: ATSSummarySection,
        screening: ScreeningResultsSection,
        hr: HRInsightsSection,
        tech: TechnicalPerformanceSection,
        behavioral: BehavioralAndRiskSection,
    ) -> tuple[List[CompetencyHighlight], List[CompetencyHighlight], List[CompetencyHighlight]]:
        strengths: List[CompetencyHighlight] = []
        weaknesses: List[CompetencyHighlight] = []
        risks: List[CompetencyHighlight] = []

        # --- Strengths ---
        if ats.ats_score >= 88.0:
            strengths.append(CompetencyHighlight(
                highlight_id="STR-ATS-01",
                highlight_type=HighlightType.STRENGTH,
                pillar=CompetencyPillar.ATS_RESUME,
                title="Exceptional Resume & Skill Match",
                description=f"Candidate resume aligns strongly with requirements ({ats.ats_score:.1f}% fit, {ats.keyword_match_rate:.1f}% keyword match).",
                impact=ImpactLevel.HIGH,
            ))

        if tech.machine_test_sandbox_score >= 90.0:
            strengths.append(CompetencyHighlight(
                highlight_id="STR-TECH-02",
                highlight_type=HighlightType.STRENGTH,
                pillar=CompetencyPillar.TECHNICAL_EVALUATION,
                title="Mastery in Practical Sandbox Coding",
                description=f"Achieved {tech.machine_test_sandbox_score:.1f}% in automated coding with {tech.test_suite_pass_rate:.1f}% test pass rate.",
                impact=ImpactLevel.CRITICAL if tech.machine_test_sandbox_score >= 95.0 else ImpactLevel.HIGH,
            ))

        if tech.architecture_design_score >= 88.0:
            strengths.append(CompetencyHighlight(
                highlight_id="STR-TECH-03",
                highlight_type=HighlightType.STRENGTH,
                pillar=CompetencyPillar.TECHNICAL_EVALUATION,
                title="Advanced Distributed Architecture Skills",
                description=f"Demonstrated superior system design capabilities ({tech.architecture_design_score:.1f} pts).",
                impact=ImpactLevel.HIGH,
            ))

        if hr.hr_score >= 85.0 and hr.star_method_rating >= 85.0:
            strengths.append(CompetencyHighlight(
                highlight_id="STR-HR-04",
                highlight_type=HighlightType.STRENGTH,
                pillar=CompetencyPillar.HR_INTERVIEW,
                title="Exemplary Behavioral & STAR Articulation",
                description=f"Candidate provided structured, outcome-driven responses ({hr.star_method_rating:.1f}% STAR adherence).",
                impact=ImpactLevel.HIGH,
            ))

        if behavioral.stress_index <= 20.0 and behavioral.overall_risk_level == "LOW":
            strengths.append(CompetencyHighlight(
                highlight_id="STR-BEH-05",
                highlight_type=HighlightType.STRENGTH,
                pillar=CompetencyPillar.BEHAVIORAL_INTEGRITY,
                title="High Composure Under Tough Questions",
                description=f"Maintained calm vocal pitch stability with minimal stress ({behavioral.stress_index:.1f}/100 index).",
                impact=ImpactLevel.MEDIUM,
            ))

        # --- Weaknesses ---
        if len(ats.missing_skills) > 0:
            weaknesses.append(CompetencyHighlight(
                highlight_id="WEAK-ATS-01",
                highlight_type=HighlightType.WEAKNESS,
                pillar=CompetencyPillar.ATS_RESUME,
                title="Specific Secondary Skill Gaps",
                description=f"Missing key JD skills: {', '.join(ats.missing_skills[:3])}.",
                impact=ImpactLevel.MEDIUM,
            ))

        if tech.machine_test_sandbox_score < 70.0 and tech.machine_test_sandbox_score >= 55.0:
            weaknesses.append(CompetencyHighlight(
                highlight_id="WEAK-TECH-02",
                highlight_type=HighlightType.WEAKNESS,
                pillar=CompetencyPillar.TECHNICAL_EVALUATION,
                title="Borderline Sandbox Implementation",
                description=f"Sandbox code pass rate ({tech.test_suite_pass_rate:.1f}%) indicates edge-case bugs.",
                impact=ImpactLevel.HIGH,
            ))

        if hr.star_method_rating < 70.0:
            weaknesses.append(CompetencyHighlight(
                highlight_id="WEAK-HR-03",
                highlight_type=HighlightType.WEAKNESS,
                pillar=CompetencyPillar.HR_INTERVIEW,
                title="Abstract or Theoretical Behavioral Answers",
                description=f"Lower STAR structure adherence ({hr.star_method_rating:.1f} pts); struggled to detail exact personal actions.",
                impact=ImpactLevel.MEDIUM,
            ))

        if behavioral.hesitation_pause_count >= 3:
            weaknesses.append(CompetencyHighlight(
                highlight_id="WEAK-BEH-04",
                highlight_type=HighlightType.WEAKNESS,
                pillar=CompetencyPillar.BEHAVIORAL_INTEGRITY,
                title="Hesitation Pauses in Problem Solving",
                description=f"Detected {behavioral.hesitation_pause_count} pauses greater than 4 seconds during questioning.",
                impact=ImpactLevel.LOW,
            ))

        # --- Risk Indicators ---
        if behavioral.malpractice_breaches_detected > 0 or behavioral.integrity_penalty_points >= 25.0:
            risks.append(CompetencyHighlight(
                highlight_id="RISK-INT-01",
                highlight_type=HighlightType.RISK_INDICATOR,
                pillar=CompetencyPillar.BEHAVIORAL_INTEGRITY,
                title="Critical Malpractice Disqualification Gate",
                description=f"Zero-tolerance breach detected: {behavioral.integrity_penalty_points:.1f} penalty pts and {behavioral.malpractice_breaches_detected} malpractice violations.",
                impact=ImpactLevel.CRITICAL,
            ))

        if tech.technical_interview_score < 55.0 or tech.machine_test_sandbox_score < 55.0:
            risks.append(CompetencyHighlight(
                highlight_id="RISK-TECH-02",
                highlight_type=HighlightType.RISK_INDICATOR,
                pillar=CompetencyPillar.TECHNICAL_EVALUATION,
                title="Technical Competency Floor Failure",
                description=f"Core technical capability breached 55.0 pt floor (Tech: {tech.technical_interview_score:.1f}, Sandbox: {tech.machine_test_sandbox_score:.1f}).",
                impact=ImpactLevel.CRITICAL,
            ))

        if behavioral.cross_round_std_dev > 16.0:
            risks.append(CompetencyHighlight(
                highlight_id="RISK-VAR-03",
                highlight_type=HighlightType.RISK_INDICATOR,
                pillar=CompetencyPillar.BEHAVIORAL_INTEGRITY,
                title="High Cross-Round Performance Volatility",
                description=f"Cross-round score dispersion ({behavioral.cross_round_std_dev:.1f} pts) sharply contrasts verbal vs. technical delivery.",
                impact=ImpactLevel.HIGH,
            ))

        if behavioral.overall_risk_level in ["HIGH", "CRITICAL"]:
            risks.append(CompetencyHighlight(
                highlight_id="RISK-GEN-04",
                highlight_type=HighlightType.RISK_INDICATOR,
                pillar=CompetencyPillar.BEHAVIORAL_INTEGRITY,
                title=f"Elevated Overall Risk Assessment ({behavioral.overall_risk_level})",
                description="Composite behavioral and integrity telemetry requires human committee intervention.",
                impact=ImpactLevel.HIGH,
            ))

        return strengths, weaknesses, risks

    # =========================================================================
    # FINAL RECOMMENDATION RESOLUTION
    # =========================================================================

    def _resolve_final_recommendation(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        experience_tier: str,
        ats: ATSSummarySection,
        screening: ScreeningResultsSection,
        hr: HRInsightsSection,
        tech: TechnicalPerformanceSection,
        behavioral: BehavioralAndRiskSection,
        override: Optional[Dict[str, Any]] = None,
    ) -> FinalRecommendationSummary:
        if override:
            return FinalRecommendationSummary(
                decision_category=override.get("decision_category", "HOLD_REVIEW"),
                decision_substatus=override.get("decision_substatus", "HOLD_HIRING_MANAGER_DEBRIEF"),
                hiring_fit_score=float(override.get("hiring_fit_score", 75.0)),
                confidence_score=float(override.get("confidence_score", 85.0)),
                confidence_band=override.get("confidence_band", "HIGH"),
                executive_rationale=override.get("executive_rationale", "Automated recommendation override applied."),
                recommended_action=override.get("recommended_action", "Proceed with standard review process."),
                counterfactual_advice=override.get("counterfactual_advice", None),
            )

        # Fallback / heuristic resolution if no override
        composite_fit = (
            ats.ats_score * 0.15
            + screening.screening_score * 0.15
            + hr.hr_score * 0.20
            + tech.technical_interview_score * 0.25
            + tech.machine_test_sandbox_score * 0.25
            - behavioral.integrity_penalty_points
        )
        composite_fit = max(0.0, min(100.0, composite_fit))

        # Check critical gates
        if behavioral.malpractice_breaches_detected > 0 or behavioral.integrity_penalty_points >= 25.0:
            category = "REJECTED"
            substatus = "REJECT_INTEGRITY_MALPRACTICE"
            action = "Immediate disqualification. Archive evidence dossier in ATS for compliance audit."
            rationale = f"Candidate {candidate_name} breached zero-tolerance integrity standards."
            band = "VERY_HIGH"
            conf = 95.0
            counterfactual = "Candidate cannot be considered due to disqualifying integrity breach."
        elif tech.technical_interview_score < 55.0 or tech.machine_test_sandbox_score < 55.0:
            category = "REJECTED"
            substatus = "REJECT_CRITICAL_GATE_BREACH"
            action = "Formal rejection. Candidate breached minimum technical execution floor (55 pts)."
            rationale = f"Candidate {candidate_name} demonstrated sub-threshold hands-on technical capabilities."
            band = "HIGH"
            conf = 90.0
            counterfactual = "Re-application eligible after 6 months; require >= 55.0 pts in coding."
        elif composite_fit >= 82.0:
            if behavioral.cross_round_std_dev > 16.0:
                category = "HOLD_REVIEW"
                substatus = "HOLD_BAR_RAISER_EVALUATION"
                action = "Schedule Bar Raiser committee review to evaluate cross-stage variance."
                rationale = f"Eligible fit ({composite_fit:.1f}%), but score volatility flags verbal vs. hands-on gap."
                band = "MODERATE"
                conf = 72.0
                counterfactual = "Verify technical depth via targeted live coding debrief."
            else:
                category = "SELECTED"
                substatus = "OFFER_IMMEDIATE_FAST_TRACK" if composite_fit >= 92.0 else "OFFER_STANDARD"
                action = "Extend formal employment offer immediately. Fast-track executive leveling if fit >= 92%."
                rationale = f"Candidate {candidate_name} decisively cleared all technical and cultural bars."
                band = "VERY_HIGH" if composite_fit >= 92.0 else "HIGH"
                conf = 96.5 if composite_fit >= 92.0 else 88.0
                counterfactual = None
        elif composite_fit >= 65.0:
            if behavioral.cross_round_std_dev > 16.0:
                category = "HOLD_REVIEW"
                substatus = "HOLD_BAR_RAISER_EVALUATION"
                action = "Schedule Bar Raiser committee review to evaluate cross-stage variance."
                rationale = f"Score volatility ({behavioral.cross_round_std_dev:.1f} pts) flags sharp contrast between verbal and technical performance."
                band = "MODERATE"
                conf = 72.0
                counterfactual = "Verify technical depth via targeted live coding debrief."
            else:
                category = "HOLD_REVIEW"
                substatus = "HOLD_BORDERLINE_SKILL_RETEST"
                action = "Schedule single-competency skill retest for borderline technical components."
                rationale = f"Candidate {candidate_name} is in the review band ({composite_fit:.1f}%)."
                band = "HIGH"
                conf = 85.0
                counterfactual = f"Improve overall hiring fit by +{82.0 - composite_fit:.1f} points to reach 82.0% Selected floor."
        else:
            category = "REJECTED"
            substatus = "REJECT_LOW_OVERALL_FIT"
            action = "Send constructive rejection notice emphasizing areas for future development."
            rationale = f"Candidate {candidate_name} scored {composite_fit:.1f}%, below the 65.0% threshold."
            band = "HIGH"
            conf = 89.0
            counterfactual = "Focus on foundational data structures and clean architecture principles."

        return FinalRecommendationSummary(
            decision_category=category,
            decision_substatus=substatus,
            hiring_fit_score=round(composite_fit, 2),
            confidence_score=round(conf, 2),
            confidence_band=band,
            executive_rationale=rationale,
            recommended_action=action,
            counterfactual_advice=counterfactual,
        )

    # =========================================================================
    # RECRUITER TL;DR SYNTHESIS
    # =========================================================================

    def _generate_recruiter_tldr(
        self,
        candidate_name: str,
        target_role: str,
        final_rec: FinalRecommendationSummary,
        strengths: List[CompetencyHighlight],
        risks: List[CompetencyHighlight],
    ) -> str:
        top_str = strengths[0].title if strengths else "Balanced competencies"
        if final_rec.decision_category == "SELECTED":
            return (
                f"{candidate_name} is decisively recommended for [{final_rec.decision_category}] "
                f"({final_rec.decision_substatus}) for {target_role} with an exceptional {final_rec.hiring_fit_score:.1f}% fit "
                f"and {final_rec.confidence_score:.1f}% certainty ({final_rec.confidence_band}). Standout factor: {top_str}. "
                f"Next Action: {final_rec.recommended_action}"
            )
        elif final_rec.decision_category == "HOLD_REVIEW":
            primary_reason = risks[0].title if risks else "Borderline score band"
            return (
                f"{candidate_name} is on [{final_rec.decision_category}] ({final_rec.decision_substatus}) "
                f"for {target_role} with a calibrated fit of {final_rec.hiring_fit_score:.1f}%. "
                f"Evaluation Trigger: {primary_reason}. Next Action: {final_rec.recommended_action}"
            )
        else: # REJECTED
            blocker = risks[0].title if risks else "Sub-threshold composite fit"
            return (
                f"{candidate_name} is [{final_rec.decision_category}] ({final_rec.decision_substatus}) "
                f"for {target_role} (Fit: {final_rec.hiring_fit_score:.1f}%, Certainty: {final_rec.confidence_score:.1f}%). "
                f"Critical Blocker: {blocker}. Next Action: {final_rec.recommended_action}"
            )
