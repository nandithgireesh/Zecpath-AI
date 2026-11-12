"""
Day 28: AI Screening Report Generator - Core Builder Engine
===========================================================
Synthesizes candidate profile data, multi-dimensional scoring evaluations,
and behavioral signals into executive-ready, actionable Screening Reports.

Features:
- Constraint analysis (Salary vs Budget, Availability & Notice Period)
- Skill confirmation matrix (Mandatory vs Bonus vs Missing)
- Strengths & risk auditing with severity levels
- Information gap / missing data detection
- Multi-factor recommendation engine (STRONG_HIRE, HIRE, PROCEED_WITH_CAUTION, NO_HIRE)
- Multi-format exports: Structured JSON, GitHub-flavored Markdown, and Modern HTML
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from .report_models import (
    HiringRecommendation,
    RiskSeverity,
    RiskCategory,
    DataGapImpact,
    ExportFormat,
    SalaryHighlight,
    AvailabilityHighlight,
    SkillConfirmationHighlight,
    KeyAnswerSummary,
    CandidateRisk,
    MissingDataGap,
    ScoreSummary,
    ScreeningReport,
)


class ScreeningReportBuilder:
    """Orchestrates end-to-end generation and export of recruiter screening reports."""

    def __init__(self, default_budget_max_lpa: float = 25.0, default_max_notice_days: int = 60):
        self.default_budget_max_lpa = default_budget_max_lpa
        self.default_max_notice_days = default_max_notice_days

    # -------------------------------------------------------------------------
    # 1. Highlight Analyzers
    # -------------------------------------------------------------------------

    def analyze_salary(
        self,
        current_ctc_lpa: Optional[float] = None,
        expected_ctc_lpa: Optional[float] = None,
        budget_max_lpa: Optional[float] = None,
        budget_min_lpa: Optional[float] = None,
        is_negotiable: bool = True,
    ) -> SalaryHighlight:
        """Evaluates candidate compensation expectations against the role budget ceiling."""
        max_budget = budget_max_lpa if budget_max_lpa is not None else self.default_budget_max_lpa

        if expected_ctc_lpa is None:
            return SalaryHighlight(
                current_ctc_lpa=current_ctc_lpa,
                expected_ctc_lpa=None,
                budget_max_lpa=max_budget,
                budget_min_lpa=budget_min_lpa,
                is_within_budget=True,
                is_negotiable=is_negotiable,
                budget_variance_pct=None,
                status="UNDISCLOSED",
                summary="Expected compensation was not disclosed during screening; requires recruiter verification.",
            )

        variance_pct = round(((expected_ctc_lpa - max_budget) / max_budget) * 100.0, 1)
        is_within = expected_ctc_lpa <= max_budget

        if is_within:
            status = "WITHIN_BUDGET"
            budget_utilization = round((expected_ctc_lpa / max_budget) * 100.0, 1)
            summary = (
                f"Expected CTC of {expected_ctc_lpa:.1f} LPA is within the allocated budget ceiling of "
                f"{max_budget:.1f} LPA ({budget_utilization}% utilization)."
            )
            if current_ctc_lpa:
                hike_pct = round(((expected_ctc_lpa - current_ctc_lpa) / current_ctc_lpa) * 100.0, 1)
                summary += f" Represents a reasonable {hike_pct}% hike over current {current_ctc_lpa:.1f} LPA."
        else:
            status = "EXCEEDS_BUDGET"
            summary = (
                f"Expected CTC of {expected_ctc_lpa:.1f} LPA exceeds budget maximum of {max_budget:.1f} LPA "
                f"by +{variance_pct}%."
            )
            if is_negotiable:
                summary += " Candidate indicated flexibility to negotiate for the right role."
            else:
                summary += " Candidate stated firm non-negotiable compensation expectations."

        return SalaryHighlight(
            current_ctc_lpa=current_ctc_lpa,
            expected_ctc_lpa=expected_ctc_lpa,
            budget_max_lpa=max_budget,
            budget_min_lpa=budget_min_lpa,
            is_within_budget=is_within,
            is_negotiable=is_negotiable,
            budget_variance_pct=variance_pct,
            status=status,
            summary=summary,
        )

    def analyze_availability(
        self,
        notice_period_days: Optional[int] = None,
        is_immediate_joiner: bool = False,
        earliest_start_date: Optional[str] = None,
        max_acceptable_notice_days: Optional[int] = None,
        buyout_possible: bool = False,
    ) -> AvailabilityHighlight:
        """Evaluates onboarding feasibility and start timeline against hiring constraints."""
        max_allowed = (
            max_acceptable_notice_days
            if max_acceptable_notice_days is not None
            else self.default_max_notice_days
        )

        if is_immediate_joiner or (notice_period_days is not None and notice_period_days == 0):
            return AvailabilityHighlight(
                notice_period_days=0,
                is_immediate_joiner=True,
                earliest_start_date=earliest_start_date or "Immediate (within 7 days)",
                max_acceptable_notice_days=max_allowed,
                is_acceptable=True,
                buyout_possible=False,
                status="IMMEDIATE",
                summary="Candidate is available to join immediately (0-day notice period), ideal for urgent staffing.",
            )

        if notice_period_days is None:
            return AvailabilityHighlight(
                notice_period_days=None,
                is_immediate_joiner=False,
                earliest_start_date=earliest_start_date,
                max_acceptable_notice_days=max_allowed,
                is_acceptable=False,
                buyout_possible=buyout_possible,
                status="UNKNOWN",
                summary="Notice period duration was not confirmed; requires immediate recruiter clarification.",
            )

        is_acceptable = notice_period_days <= max_allowed or buyout_possible

        if notice_period_days <= 30:
            status = "STANDARD"
            summary = f"Candidate has a short {notice_period_days}-day notice period, well within the {max_allowed}-day limit."
        elif notice_period_days <= max_allowed:
            status = "STANDARD"
            summary = f"Candidate has a {notice_period_days}-day notice period, meeting the {max_allowed}-day project requirement."
        else:
            status = "EXTENDED"
            summary = f"Notice period of {notice_period_days} days exceeds role requirement of {max_allowed} days."
            if buyout_possible:
                summary += " Candidate noted early release or notice buyout may be negotiable."

        return AvailabilityHighlight(
            notice_period_days=notice_period_days,
            is_immediate_joiner=False,
            earliest_start_date=earliest_start_date or f"After {notice_period_days} days notice",
            max_acceptable_notice_days=max_allowed,
            is_acceptable=is_acceptable,
            buyout_possible=buyout_possible,
            status=status,
            summary=summary,
        )

    def analyze_skills(
        self,
        candidate_skills: List[str],
        required_mandatory_skills: List[str],
        required_bonus_skills: Optional[List[str]] = None,
    ) -> SkillConfirmationHighlight:
        """Cross-references candidate confirmed skills against mandatory and bonus role criteria."""
        required_bonus = required_bonus_skills or []

        # Normalize lowercase for comparison
        c_skills_lower = {s.lower().strip(): s for s in candidate_skills}

        confirmed = []
        missing = []
        bonus = []

        for req in required_mandatory_skills:
            if req.lower().strip() in c_skills_lower:
                confirmed.append(c_skills_lower[req.lower().strip()])
            else:
                missing.append(req)

        for b in required_bonus:
            if b.lower().strip() in c_skills_lower:
                bonus.append(c_skills_lower[b.lower().strip()])

        total_req = max(1, len(required_mandatory_skills))
        match_pct = round((len(confirmed) / total_req) * 100.0, 1)

        if match_pct >= 90.0:
            status = "FULLY_CONFIRMED"
            summary = f"100% of core mandatory skills confirmed ({len(confirmed)}/{len(required_mandatory_skills)})."
        elif match_pct >= 60.0:
            status = "PARTIAL_MATCH"
            summary = f"Partially confirmed mandatory skills ({match_pct}% match: {len(confirmed)}/{len(required_mandatory_skills)})."
        else:
            status = "CRITICAL_GAPS"
            summary = f"Critical skill gaps detected: only {len(confirmed)}/{len(required_mandatory_skills)} mandatory skills validated."

        if bonus:
            summary += f" Bonus expertise validated in: {', '.join(bonus)}."

        return SkillConfirmationHighlight(
            confirmed_skills=confirmed,
            missing_mandatory_skills=missing,
            bonus_skills_found=bonus,
            skill_match_percentage=match_pct,
            strongest_areas=confirmed[:4],
            areas_for_validation=missing,
            status=status,
            summary=summary,
        )

    # -------------------------------------------------------------------------
    # 2. Synthesis & Auditing
    # -------------------------------------------------------------------------

    def distill_key_answers(
        self,
        question_evaluations: List[Dict[str, Any]],
    ) -> List[KeyAnswerSummary]:
        """Condenses raw question answers into crisp, high-impact recruiter summaries."""
        summaries = []
        for i, qe in enumerate(question_evaluations):
            q_id = qe.get("question_id", f"Q{i+1}")
            category = qe.get("question_category", qe.get("category", "General"))
            q_text = qe.get("question_text", "Screening Question")
            raw_answer = qe.get("raw_answer", qe.get("answer", ""))
            score = float(qe.get("weighted_question_score", qe.get("score", 70.0)))
            grade = qe.get("grade", "STRONG")

            # Extract crisp summary
            explanation = qe.get("explanation", "")
            if explanation and len(explanation) > 10:
                answer_summary = explanation.split(".")[0] + "."
            else:
                answer_summary = (raw_answer[:140] + "...") if len(raw_answer) > 140 else raw_answer

            takeaways = qe.get("strengths", [])
            if not takeaways and score >= 75.0:
                takeaways = ["Demonstrated solid conceptual grasp and relevant hands-on examples."]
            elif not takeaways and score < 60.0:
                takeaways = ["Answer lacked depth or exhibited noticeable hesitation."]

            summaries.append(
                KeyAnswerSummary(
                    question_id=q_id,
                    category=category,
                    question_text=q_text,
                    candidate_answer=raw_answer,
                    answer_summary=answer_summary,
                    score=score,
                    grade=str(grade),
                    key_takeaways=takeaways[:2],
                )
            )
        return summaries

    def extract_strengths(
        self,
        scores: ScoreSummary,
        skills_hl: SkillConfirmationHighlight,
        salary_hl: SalaryHighlight,
        avail_hl: AvailabilityHighlight,
        custom_strengths: Optional[List[str]] = None,
    ) -> List[str]:
        """Extracts top positive candidate attributes and competitive advantages."""
        strengths = list(custom_strengths or [])

        if scores.technical_score >= 85.0 and "Strong technical architecture" not in str(strengths):
            strengths.append(f"High technical aptitude with a {scores.technical_score:.1f}/100 evaluation score.")
        if scores.communication_score >= 82.0:
            strengths.append(f"Articulate and fluent communicator ({scores.communication_score:.1f}/100 communication score).")
        if skills_hl.skill_match_percentage >= 85.0:
            strengths.append(f"Comprehensive skill alignment: {len(skills_hl.confirmed_skills)} core mandatory skills verified.")
        if skills_hl.bonus_skills_found:
            strengths.append(f"Value-add bonus expertise in {', '.join(skills_hl.bonus_skills_found)}.")
        if avail_hl.is_immediate_joiner:
            strengths.append("Immediate joiner (0-day notice period), offering immediate onboarding capability.")
        elif avail_hl.notice_period_days and avail_hl.notice_period_days <= 30:
            strengths.append(f"Short notice period of {avail_hl.notice_period_days} days facilitates fast hiring.")
        if salary_hl.is_within_budget and salary_hl.budget_variance_pct and salary_hl.budget_variance_pct <= -10.0:
            strengths.append(f"Highly cost-effective compensation expectations ({abs(salary_hl.budget_variance_pct):.0f}% below ceiling).")

        return strengths[:6]

    def audit_risks(
        self,
        scores: ScoreSummary,
        salary_hl: SalaryHighlight,
        avail_hl: AvailabilityHighlight,
        skills_hl: SkillConfirmationHighlight,
        behavioral_summary: Optional[Dict[str, Any]] = None,
        custom_risks: Optional[List[CandidateRisk]] = None,
    ) -> List[CandidateRisk]:
        """Audits candidate profile for compensation, timeline, skill, and behavioral risks."""
        risks: List[CandidateRisk] = list(custom_risks or [])
        risk_counter = len(risks) + 1

        # Salary Risks
        if not salary_hl.is_within_budget:
            variance = salary_hl.budget_variance_pct or 0.0
            severity = RiskSeverity.CRITICAL if variance > 30.0 and not salary_hl.is_negotiable else (
                RiskSeverity.HIGH if variance > 15.0 else RiskSeverity.MODERATE
            )
            risks.append(
                CandidateRisk(
                    risk_id=f"RSK-0{risk_counter}",
                    category=RiskCategory.SALARY,
                    severity=severity,
                    title="Compensation Exceeds Allocated Budget",
                    description=f"Expected CTC of {salary_hl.expected_ctc_lpa} LPA is +{variance:.1f}% above the {salary_hl.budget_max_lpa} LPA limit.",
                    evidence=f"Expected: {salary_hl.expected_ctc_lpa} LPA vs Budget: {salary_hl.budget_max_lpa} LPA",
                    mitigation_or_probe="Determine whether client budget can stretch or if candidate will accept performance equity/bonuses.",
                )
            )
            risk_counter += 1

        # Availability Risks
        if not avail_hl.is_acceptable:
            risks.append(
                CandidateRisk(
                    risk_id=f"RSK-0{risk_counter}",
                    category=RiskCategory.AVAILABILITY,
                    severity=RiskSeverity.HIGH,
                    title="Extended Notice Period Timeline",
                    description=f"Candidate notice period ({avail_hl.notice_period_days} days) exceeds role threshold ({avail_hl.max_acceptable_notice_days} days).",
                    evidence=f"{avail_hl.notice_period_days} days notice",
                    mitigation_or_probe="Negotiate notice buyout or probe if accumulated leave can facilitate an early release.",
                )
            )
            risk_counter += 1

        # Skill Gaps
        if skills_hl.missing_mandatory_skills:
            severity = RiskSeverity.HIGH if len(skills_hl.missing_mandatory_skills) > 1 else RiskSeverity.MODERATE
            risks.append(
                CandidateRisk(
                    risk_id=f"RSK-0{risk_counter}",
                    category=RiskCategory.SKILL_GAP,
                    severity=severity,
                    title=f"Unconfirmed Mandatory Skills ({len(skills_hl.missing_mandatory_skills)})",
                    description=f"Key required skills were not demonstrated: {', '.join(skills_hl.missing_mandatory_skills)}.",
                    evidence=f"Missing: {', '.join(skills_hl.missing_mandatory_skills)}",
                    mitigation_or_probe="Schedule focused technical deep-dive on missing competencies during Round 2.",
                )
            )
            risk_counter += 1

        # Behavioral & Communication Signals
        if behavioral_summary:
            if behavioral_summary.get("is_defensive", False):
                risks.append(
                    CandidateRisk(
                        risk_id=f"RSK-0{risk_counter}",
                        category=RiskCategory.BEHAVIORAL,
                        severity=RiskSeverity.CRITICAL,
                        title="Defensive or Combative Conversational Demeanor",
                        description="Candidate exhibited defensive language or reluctance when answering standard screening questions.",
                        evidence=str(behavioral_summary.get("defensive_quotes", "Defensive markers detected")),
                        mitigation_or_probe="Evaluate cultural fit and team collaboration dynamics thoroughly in behavioral round.",
                    )
                )
                risk_counter += 1
            elif scores.confidence_score < 60.0:
                risks.append(
                    CandidateRisk(
                        risk_id=f"RSK-0{risk_counter}",
                        category=RiskCategory.BEHAVIORAL,
                        severity=RiskSeverity.MODERATE,
                        title="Frequent Vocal Hesitation and Hedging",
                        description="Candidate exhibited noticeable hesitation, long silence pauses, or epistemic hedging on core answers.",
                        evidence=f"Confidence Score: {scores.confidence_score:.1f}/100",
                        mitigation_or_probe="Probe depth of hands-on experience vs superficial theoretical exposure.",
                    )
                )
                risk_counter += 1

        return risks

    def detect_missing_data(
        self,
        candidate_data: Dict[str, Any],
        salary_hl: SalaryHighlight,
        avail_hl: AvailabilityHighlight,
        skills_hl: SkillConfirmationHighlight,
    ) -> List[MissingDataGap]:
        """Audits interview data for unconfirmed fields or ambiguous claims."""
        gaps = []
        gap_id = 1

        if salary_hl.status == "UNDISCLOSED":
            gaps.append(
                MissingDataGap(
                    gap_id=f"GAP-0{gap_id}",
                    field_name="expected_ctc_lpa",
                    impact=DataGapImpact.IMPORTANT,
                    description="Expected compensation was not specified during the call.",
                    suggested_action="HR coordinator to confirm exact CTC expectations before releasing technical assignment.",
                )
            )
            gap_id += 1

        if avail_hl.status == "UNKNOWN":
            gaps.append(
                MissingDataGap(
                    gap_id=f"GAP-0{gap_id}",
                    field_name="notice_period_days",
                    impact=DataGapImpact.BLOCKER,
                    description="Notice period duration is unconfirmed.",
                    suggested_action="Obtain exact written notice period and current employment status from candidate.",
                )
            )
            gap_id += 1

        if not candidate_data.get("current_location"):
            gaps.append(
                MissingDataGap(
                    gap_id=f"GAP-0{gap_id}",
                    field_name="current_location",
                    impact=DataGapImpact.NICE_TO_HAVE,
                    description="Current physical location or remote work preference was not verified.",
                    suggested_action="Confirm work location flexibility or relocation willingness during HR sync.",
                )
            )
            gap_id += 1

        if skills_hl.missing_mandatory_skills:
            for skill in skills_hl.missing_mandatory_skills[:2]:
                gaps.append(
                    MissingDataGap(
                        gap_id=f"GAP-0{gap_id}",
                        field_name=f"skill_verification_{skill.lower()}",
                        impact=DataGapImpact.IMPORTANT,
                        description=f"Hands-on proficiency with {skill} was not confirmed in screening responses.",
                        suggested_action=f"Include a practical {skill} coding challenge or system design question in Round 2.",
                    )
                )
                gap_id += 1

        return gaps

    def determine_recommendation(
        self,
        scores: ScoreSummary,
        salary_hl: SalaryHighlight,
        avail_hl: AvailabilityHighlight,
        skills_hl: SkillConfirmationHighlight,
        risks: List[CandidateRisk],
    ) -> HiringRecommendation:
        """Determines final hiring recommendation based on holistic multi-factor evaluation."""
        has_critical_risk = any(r.severity == RiskSeverity.CRITICAL for r in risks)
        high_risk_count = sum(1 for r in risks if r.severity == RiskSeverity.HIGH)

        # 1. Automatic disqualifiers
        if has_critical_risk or scores.overall_score < 50.0:
            return HiringRecommendation.NO_HIRE

        # 2. Strong Hire criteria
        if (
            scores.overall_score >= 85.0
            and scores.technical_score >= 84.0
            and scores.communication_score >= 75.0
            and salary_hl.is_within_budget
            and avail_hl.is_acceptable
            and skills_hl.skill_match_percentage >= 85.0
            and high_risk_count == 0
        ):
            return HiringRecommendation.STRONG_HIRE

        # 3. Standard Hire criteria
        if (
            scores.overall_score >= 72.0
            and scores.technical_score >= 68.0
            and scores.communication_score >= 65.0
            and (salary_hl.is_within_budget or salary_hl.is_negotiable)
            and (avail_hl.is_acceptable or avail_hl.buyout_possible)
            and skills_hl.skill_match_percentage >= 60.0
            and high_risk_count <= 1
        ):
            return HiringRecommendation.HIRE

        # 4. Proceed with Caution
        if scores.overall_score >= 55.0 and scores.technical_score >= 50.0:
            return HiringRecommendation.PROCEED_WITH_CAUTION

        # 5. Fallback No Hire
        return HiringRecommendation.NO_HIRE

    def generate_executive_summary(
        self,
        candidate_name: str,
        role_name: str,
        recommendation: HiringRecommendation,
        scores: ScoreSummary,
        salary_hl: SalaryHighlight,
        avail_hl: AvailabilityHighlight,
        skills_hl: SkillConfirmationHighlight,
    ) -> str:
        """Generates a concise 3-4 sentence recruiter executive narrative."""
        rec_labels = {
            HiringRecommendation.STRONG_HIRE: "a Strong Hire",
            HiringRecommendation.HIRE: "recommended for hire",
            HiringRecommendation.PROCEED_WITH_CAUTION: "a Proceed with Caution candidate",
            HiringRecommendation.NO_HIRE: "not recommended for advancement",
        }

        sentence_1 = (
            f"{candidate_name} is evaluated as {rec_labels[recommendation]} for the {role_name} position "
            f"with an overall screening score of {scores.overall_score:.1f}/100 ({scores.overall_grade})."
        )

        sentence_2 = (
            f"The candidate demonstrated solid technical competence ({scores.technical_score:.1f}/100) with "
            f"{skills_hl.skill_match_percentage:.0f}% of core mandatory skills confirmed ({len(skills_hl.confirmed_skills)} skills validated)."
        )

        if salary_hl.expected_ctc_lpa is not None:
            if salary_hl.is_within_budget:
                salary_part = f"expected CTC of {salary_hl.expected_ctc_lpa:.1f} LPA is within client budget"
            else:
                var_str = f"by +{salary_hl.budget_variance_pct:.0f}%" if salary_hl.budget_variance_pct else ""
                salary_part = f"expected CTC of {salary_hl.expected_ctc_lpa:.1f} LPA exceeds budget {var_str}".strip()
        else:
            salary_part = "compensation expectations remain undisclosed"

        if avail_hl.is_immediate_joiner:
            avail_part = "immediate availability (0-day notice)"
        elif avail_hl.notice_period_days is not None:
            avail_part = f"{avail_hl.notice_period_days}-day notice period"
        else:
            avail_part = "unconfirmed notice timeline"
        sentence_3 = f"Operational parameters show {salary_part} alongside a {avail_part}."


        if recommendation in (HiringRecommendation.STRONG_HIRE, HiringRecommendation.HIRE):
            sentence_4 = "Recommended for immediate technical round scheduling."
        elif recommendation == HiringRecommendation.PROCEED_WITH_CAUTION:
            sentence_4 = "Recommended for advancement provided the technical team deep-dives into flagged skill and timeline gaps."
        else:
            sentence_4 = "Recommend exploring alternative candidates whose qualifications more closely align with core requirements."

        return f"{sentence_1} {sentence_2} {sentence_3} {sentence_4}"

    # -------------------------------------------------------------------------
    # 3. Master Report Orchestrator
    # -------------------------------------------------------------------------

    def build_report(
        self,
        candidate_id: str,
        candidate_name: str,
        job_id: str,
        role_name: str,
        candidate_data: Dict[str, Any],
        question_evaluations: List[Dict[str, Any]],
        role_mandatory_skills: List[str],
        role_bonus_skills: Optional[List[str]] = None,
        budget_max_lpa: Optional[float] = None,
        budget_min_lpa: Optional[float] = None,
        max_acceptable_notice_days: Optional[int] = None,
        behavioral_summary: Optional[Dict[str, Any]] = None,
        recommended_interviewer_probes: Optional[List[str]] = None,
    ) -> ScreeningReport:
        """Assembles a comprehensive, recruiter-ready AI Screening Report."""
        report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"

        # 1. Highlights
        salary_hl = self.analyze_salary(
            current_ctc_lpa=candidate_data.get("current_ctc_lpa"),
            expected_ctc_lpa=candidate_data.get("expected_ctc_lpa"),
            budget_max_lpa=budget_max_lpa,
            budget_min_lpa=budget_min_lpa,
            is_negotiable=candidate_data.get("ctc_negotiable", True),
        )

        avail_hl = self.analyze_availability(
            notice_period_days=candidate_data.get("notice_period_days"),
            is_immediate_joiner=candidate_data.get("is_immediate_joiner", False),
            earliest_start_date=candidate_data.get("earliest_start_date"),
            max_acceptable_notice_days=max_acceptable_notice_days,
            buyout_possible=candidate_data.get("buyout_possible", False),
        )

        skills_hl = self.analyze_skills(
            candidate_skills=candidate_data.get("skills_confirmed", candidate_data.get("skills", [])),
            required_mandatory_skills=role_mandatory_skills,
            required_bonus_skills=role_bonus_skills,
        )

        # 2. Key Answers Distillation
        key_answers = self.distill_key_answers(question_evaluations)

        # 3. Compute Aggregate Scores
        if question_evaluations:
            tech_scores = [q.score for q in key_answers if q.category in ("Technical", "System Design", "Experience")]
            tech_score = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 75.0
            relevance_scores = [
                float(qe.get("relevance_score", 75.0)) for qe in question_evaluations
            ]
            relevance_score = round(sum(relevance_scores) / len(relevance_scores), 1)
        else:
            tech_score = 75.0
            relevance_score = 75.0

        comm_score = float(behavioral_summary.get("communication_score", 82.0)) if behavioral_summary else 80.0
        conf_score = float(behavioral_summary.get("confidence_score", 85.0)) if behavioral_summary else 82.0

        # Overall weighted score
        overall_score = round(
            0.50 * tech_score + 0.25 * comm_score + 0.15 * skills_hl.skill_match_percentage + 0.10 * conf_score,
            1,
        )

        if overall_score >= 85.0:
            grade = "EXCELLENT"
        elif overall_score >= 70.0:
            grade = "STRONG"
        elif overall_score >= 55.0:
            grade = "MODERATE"
        else:
            grade = "POOR"

        scores = ScoreSummary(
            overall_score=overall_score,
            technical_score=tech_score,
            communication_score=comm_score,
            relevance_score=relevance_score,
            confidence_score=conf_score,
            overall_grade=grade,
        )

        # 4. Strengths, Risks & Missing Gaps
        strengths = self.extract_strengths(scores, skills_hl, salary_hl, avail_hl)
        risks = self.audit_risks(scores, salary_hl, avail_hl, skills_hl, behavioral_summary)
        missing_gaps = self.detect_missing_data(candidate_data, salary_hl, avail_hl, skills_hl)

        # 5. Recommendation
        rec = self.determine_recommendation(scores, salary_hl, avail_hl, skills_hl, risks)
        badge_map = {
            HiringRecommendation.STRONG_HIRE: "Strong Hire",
            HiringRecommendation.HIRE: "Hire",
            HiringRecommendation.PROCEED_WITH_CAUTION: "Proceed with Caution",
            HiringRecommendation.NO_HIRE: "No Hire",
        }

        # 6. Executive Narrative
        exec_summary = self.generate_executive_summary(
            candidate_name=candidate_name,
            role_name=role_name,
            recommendation=rec,
            scores=scores,
            salary_hl=salary_hl,
            avail_hl=avail_hl,
            skills_hl=skills_hl,
        )

        # 7. Probes
        probes = list(recommended_interviewer_probes or [])
        if not probes:
            if skills_hl.missing_mandatory_skills:
                probes.append(
                    f"Ask candidate to walk through an end-to-end production architecture utilizing {skills_hl.missing_mandatory_skills[0]}."
                )
            if risks:
                probes.append(risks[0].mitigation_or_probe)
            probes.append("Evaluate candidate's leadership experience in managing cross-functional technical trade-offs.")

        return ScreeningReport(
            report_id=report_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_id=job_id,
            role_name=role_name,
            recommendation=rec,
            recommendation_badge=badge_map[rec],
            executive_summary=exec_summary,
            scores=scores,
            salary_highlight=salary_hl,
            availability_highlight=avail_hl,
            skills_highlight=skills_hl,
            strengths=strengths,
            risks=risks,
            missing_data_gaps=missing_gaps,
            key_answers=key_answers,
            behavioral_summary=behavioral_summary,
            recommended_interviewer_probes=probes[:4],
        )

    # -------------------------------------------------------------------------
    # 4. Multi-Format Exporters
    # -------------------------------------------------------------------------

    def export_markdown(self, report: ScreeningReport) -> str:
        """Generates a publication-grade GitHub-flavored Markdown report."""
        badge_colors = {
            HiringRecommendation.STRONG_HIRE: "🟢 **STRONG HIRE**",
            HiringRecommendation.HIRE: "🟢 **HIRE**",
            HiringRecommendation.PROCEED_WITH_CAUTION: "🟡 **PROCEED WITH CAUTION**",
            HiringRecommendation.NO_HIRE: "🔴 **NO HIRE**",
        }

        lines = [
            f"# AI Screening Report: {report.candidate_name}",
            f"**Role:** {report.role_name} | **Report ID:** `{report.report_id}` | **Date:** {report.generated_at[:10]}",
            f"**Hiring Recommendation:** {badge_colors.get(report.recommendation, str(report.recommendation))}",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            report.executive_summary,
            "",
            "---",
            "",
            "## 2. Scorecard & Performance Metrics",
            "",
            "| Metric | Score | Grade | Evaluation Focus |",
            "|---|---|---|---|",
            f"| **Overall Screening Score** | **{report.scores.overall_score:.1f}/100** | **{report.scores.overall_grade}** | Composite multi-attribute rating |",
            f"| Technical Competence | {report.scores.technical_score:.1f}/100 | - | System depth, architecture & implementation |",
            f"| Communication Quality | {report.scores.communication_score:.1f}/100 | - | Fluency, assertiveness & engagement |",
            f"| Answer Relevance | {report.scores.relevance_score:.1f}/100 | - | Direct alignment with interview prompts |",
            f"| Vocal Confidence | {report.scores.confidence_score:.1f}/100 | - | Low hesitation, steady pacing & assertiveness |",
            "",
            "---",
            "",
            "## 3. Core Operational Constraints",
            "",
            "### 💰 Salary & Compensation",
            f"- **Expected CTC:** {f'{report.salary_highlight.expected_ctc_lpa} LPA' if report.salary_highlight.expected_ctc_lpa else 'Undisclosed'}",
            f"- **Budget Ceiling:** {report.salary_highlight.budget_max_lpa} LPA",
            f"- **Alignment Status:** `{report.salary_highlight.status}`",
            f"- **Recruiter Note:** {report.salary_highlight.summary}",
            "",
            "### ⏱️ Availability & Onboarding",
            f"- **Notice Period:** {f'{report.availability_highlight.notice_period_days} days' if report.availability_highlight.notice_period_days is not None else 'Unconfirmed'}",
            f"- **Immediate Joiner:** {'Yes' if report.availability_highlight.is_immediate_joiner else 'No'}",
            f"- **Earliest Start:** {report.availability_highlight.earliest_start_date}",
            f"- **Recruiter Note:** {report.availability_highlight.summary}",
            "",
            "### 🛠️ Technical Skill Confirmations",
            f"- **Confirmed Skills:** {', '.join(report.skills_highlight.confirmed_skills) if report.skills_highlight.confirmed_skills else 'None validated'}",
            f"- **Missing Required Skills:** {', '.join(report.skills_highlight.missing_mandatory_skills) if report.skills_highlight.missing_mandatory_skills else 'None (100% matched)'}",
            f"- **Bonus Skills Demonstrated:** {', '.join(report.skills_highlight.bonus_skills_found) if report.skills_highlight.bonus_skills_found else 'None'}",
            f"- **Match Rate:** {report.skills_highlight.skill_match_percentage:.1f}%",
            "",
            "---",
            "",
            "## 4. Candidate Strengths & Advantages",
        ]

        for s in report.strengths:
            lines.append(f"- ✅ {s}")

        lines.extend([
            "",
            "---",
            "",
            "## 5. Risk Factors & Potential Red Flags",
        ])

        if not report.risks:
            lines.append("No critical or high risks identified during screening.")
        else:
            lines.extend([
                "| ID | Category | Severity | Risk Title | Suggested Mitigation / Probe |",
                "|---|---|---|---|---|",
            ])
            for r in report.risks:
                sev_icon = "🔴" if r.severity in (RiskSeverity.CRITICAL, RiskSeverity.HIGH) else "🟡"
                lines.append(
                    f"| `{r.risk_id}` | {r.category.value} | {sev_icon} {r.severity.value} | **{r.title}** | {r.mitigation_or_probe} |"
                )

        lines.extend([
            "",
            "---",
            "",
            "## 6. Information Gaps & Missing Data",
        ])

        if not report.missing_data_gaps:
            lines.append("All mandatory screening profile fields and questions were successfully validated.")
        else:
            for g in report.missing_data_gaps:
                lines.append(f"- ⚠️ **[{g.impact.value}] {g.field_name}:** {g.description} *(Action: {g.suggested_action})*")

        lines.extend([
            "",
            "---",
            "",
            "## 7. Key Answer Summaries",
        ])

        for ka in report.key_answers:
            lines.extend([
                f"### {ka.question_id}: {ka.question_text}",
                f"- **Category:** `{ka.category}` | **Score:** `{ka.score:.1f}/100` ({ka.grade})",
                f"- **Summary:** {ka.answer_summary}",
                f"- **Key Takeaway:** {', '.join(ka.key_takeaways)}",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 8. Recommended Round-2 Interviewer Probes",
        ])

        for i, probe in enumerate(report.recommended_interviewer_probes, 1):
            lines.append(f"{i}. 🎯 {probe}")

        lines.append("")
        return "\n".join(lines)

    def export_html(self, report: ScreeningReport) -> str:
        """Generates an executive-styled, responsive HTML screening summary card."""
        rec_color_map = {
            HiringRecommendation.STRONG_HIRE: "#22c55e",
            HiringRecommendation.HIRE: "#3b82f6",
            HiringRecommendation.PROCEED_WITH_CAUTION: "#f59e0b",
            HiringRecommendation.NO_HIRE: "#ef4444",
        }
        theme_color = rec_color_map.get(report.recommendation, "#3b82f6")

        strengths_html = "".join(f"<li><span class='check'>✓</span> {s}</li>" for s in report.strengths)
        
        risks_html = ""
        if not report.risks:
            risks_html = "<p class='empty-note'>No critical risk factors identified.</p>"
        else:
            for r in report.risks:
                badge_class = "badge-crit" if r.severity in (RiskSeverity.CRITICAL, RiskSeverity.HIGH) else "badge-mod"
                risks_html += f"""
                <div class="risk-card">
                    <span class="badge {badge_class}">{r.severity.value}</span>
                    <strong>{r.title}</strong>
                    <p>{r.description}</p>
                    <small><b>Mitigation:</b> {r.mitigation_or_probe}</small>
                </div>
                """

        gaps_html = "".join(
            f"<li><b>[{g.impact.value}] {g.field_name}:</b> {g.description}</li>"
            for g in report.missing_data_gaps
        ) or "<p class='empty-note'>All mandatory candidate profile fields validated.</p>"

        probes_html = "".join(f"<li>{p}</li>" for p in report.recommended_interviewer_probes)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Screening Report - {report.candidate_name}</title>
<style>
  :root {{
    --primary: {theme_color};
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text-dark);
    margin: 0;
    padding: 30px 15px;
    display: flex;
    justify-content: center;
  }}
  .report-container {{
    max-width: 900px;
    width: 100%;
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    border: 1px solid var(--border);
    padding: 35px;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2px solid var(--border);
    padding-bottom: 20px;
    margin-bottom: 25px;
  }}
  .candidate-title h1 {{ margin: 0 0 6px 0; font-size: 26px; color: var(--text-dark); }}
  .candidate-title p {{ margin: 0; color: var(--text-muted); font-size: 14px; }}
  .rec-badge {{
    background: {theme_color};
    color: #fff;
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}
  .summary-box {{
    background: #f1f5f9;
    border-left: 4px solid var(--primary);
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 25px;
    line-height: 1.6;
  }}
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 25px;
  }}
  .section-box {{
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    background: #fff;
  }}
  .section-box h3 {{
    margin: 0 0 12px 0;
    font-size: 16px;
    color: var(--text-dark);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
  }}
  .score-card {{
    text-align: center;
    padding: 15px;
    background: #f8fafc;
    border-radius: 8px;
    margin-bottom: 15px;
  }}
  .score-card .big-num {{
    font-size: 38px;
    font-weight: 800;
    color: var(--primary);
  }}
  .check {{ color: #22c55e; font-weight: bold; margin-right: 6px; }}
  ul {{ padding-left: 20px; margin: 0; line-height: 1.6; }}
  .risk-card {{
    border-left: 3px solid #ef4444;
    padding: 10px 14px;
    background: #fef2f2;
    margin-bottom: 12px;
    border-radius: 0 6px 6px 0;
  }}
  .risk-card p {{ margin: 4px 0 6px 0; font-size: 13px; color: #475569; }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
    color: #fff;
  }}
  .badge-crit {{ background: #ef4444; }}
  .badge-mod {{ background: #f59e0b; }}
  .empty-note {{ color: var(--text-muted); font-style: italic; font-size: 13px; }}
</style>
</head>
<body>
<div class="report-container">
  <div class="header">
    <div class="candidate-title">
      <h1>{report.candidate_name}</h1>
      <p>Role: <b>{report.role_name}</b> | Candidate ID: <code>{report.candidate_id}</code> | Report ID: <code>{report.report_id}</code></p>
    </div>
    <div class="rec-badge">{report.recommendation_badge}</div>
  </div>

  <div class="summary-box">
    <b>Recruiter Executive Summary:</b> {report.executive_summary}
  </div>

  <div class="grid-2">
    <div class="section-box">
      <h3>Screening Scorecard</h3>
      <div class="score-card">
        <div class="big-num">{report.scores.overall_score:.1f}</div>
        <div>Overall Rating: <b>{report.scores.overall_grade}</b></div>
      </div>
      <p><b>Technical:</b> {report.scores.technical_score:.1f}/100 | <b>Communication:</b> {report.scores.communication_score:.1f}/100</p>
      <p><b>Confidence:</b> {report.scores.confidence_score:.1f}/100 | <b>Relevance:</b> {report.scores.relevance_score:.1f}/100</p>
    </div>

    <div class="section-box">
      <h3>Operational Constraints</h3>
      <p><b>Salary Expected:</b> {f'{report.salary_highlight.expected_ctc_lpa} LPA' if report.salary_highlight.expected_ctc_lpa else 'Undisclosed'} (Budget: {report.salary_highlight.budget_max_lpa} LPA)</p>
      <small style="color:var(--text-muted);">{report.salary_highlight.summary}</small>
      <p style="margin-top:10px;"><b>Notice Period:</b> {f'{report.availability_highlight.notice_period_days} days' if report.availability_highlight.notice_period_days is not None else 'Unconfirmed'} ({'Immediate Joiner' if report.availability_highlight.is_immediate_joiner else 'Standard'})</p>
      <small style="color:var(--text-muted);">{report.availability_highlight.summary}</small>
    </div>
  </div>

  <div class="grid-2">
    <div class="section-box">
      <h3>Top Candidate Strengths</h3>
      <ul>{strengths_html}</ul>
    </div>

    <div class="section-box">
      <h3>Risk Factors & Audit</h3>
      {risks_html}
    </div>
  </div>

  <div class="section-box" style="margin-bottom:20px;">
    <h3>Recommended Round-2 Interviewer Probes</h3>
    <ol>{probes_html}</ol>
  </div>
</div>
</body>
</html>"""

    def export_json(self, report: ScreeningReport) -> Dict[str, Any]:
        """Returns valid JSON dictionary conforming to screening_report_schema.json."""
        return report.model_dump()
