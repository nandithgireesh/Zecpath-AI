"""
Day 28: AI Screening Report Generator - Data Models
===================================================
Pydantic schemas and enums for structured, recruiter-ready screening reports.
Covers salary expectation highlights, availability analysis, skill confirmation,
strengths, risks, missing data gaps, key answer summaries, and hiring recommendations.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class HiringRecommendation(str, Enum):
    STRONG_HIRE = "STRONG_HIRE"                    # Outstanding technical & communication scores, zero blockers
    HIRE = "HIRE"                                  # Meets all criteria, solid skills, minor follow-up
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"  # Marginal fit, notice/salary friction, or technical gaps
    NO_HIRE = "NO_HIRE"                            # Severe gaps, missing core skills, defensive, or unworkable constraints


class RiskSeverity(str, Enum):
    CRITICAL = "CRITICAL"    # Disqualifying or high-risk blocker
    HIGH = "HIGH"            # Substantial risk requiring senior sign-off or deep probing
    MODERATE = "MODERATE"    # Manageable risk or friction point
    LOW = "LOW"              # Minor observation or easily trainable gap


class RiskCategory(str, Enum):
    SALARY = "SALARY"
    AVAILABILITY = "AVAILABILITY"
    SKILL_GAP = "SKILL_GAP"
    EXPERIENCE = "EXPERIENCE"
    BEHAVIORAL = "BEHAVIORAL"
    CONSISTENCY = "CONSISTENCY"


class DataGapImpact(str, Enum):
    BLOCKER = "BLOCKER"            # Cannot proceed to offer without this information
    IMPORTANT = "IMPORTANT"        # Needs resolution in the next interview round
    NICE_TO_HAVE = "NICE_TO_HAVE"  # Helpful supplementary information


class ExportFormat(str, Enum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"


class SalaryHighlight(BaseModel):
    """Structured breakdown of candidate compensation expectations against hiring budget."""
    current_ctc_lpa: Optional[float] = Field(default=None, description="Current compensation in Lakhs Per Annum.")
    expected_ctc_lpa: Optional[float] = Field(default=None, description="Expected compensation in Lakhs Per Annum.")
    budget_max_lpa: Optional[float] = Field(default=None, description="Client or role maximum budget ceiling.")
    budget_min_lpa: Optional[float] = Field(default=None, description="Client or role target minimum budget.")
    is_within_budget: bool = Field(default=True, description="Whether expected CTC is within the allocated budget.")
    is_negotiable: bool = Field(default=True, description="Whether the candidate expressed flexibility on compensation.")
    budget_variance_pct: Optional[float] = Field(
        default=None,
        description="Percentage variance of expectation vs budget maximum (positive means over budget)."
    )
    status: str = Field(default="WITHIN_BUDGET", description="WITHIN_BUDGET, EXCEEDS_BUDGET, or UNDISCLOSED.")
    summary: str = Field(description="Recruiter-friendly summary explanation of salary alignment.")


class AvailabilityHighlight(BaseModel):
    """Candidate availability, notice period, and onboarding feasibility."""
    notice_period_days: Optional[int] = Field(default=None, description="Candidate notice period in days.")
    is_immediate_joiner: bool = Field(default=False, description="Whether candidate can join immediately (0-7 days).")
    earliest_start_date: Optional[str] = Field(default=None, description="Projected start date or string descriptor.")
    max_acceptable_notice_days: Optional[int] = Field(
        default=None,
        description="Role maximum allowable notice period."
    )
    is_acceptable: bool = Field(default=True, description="Whether availability meets project timeline constraints.")
    buyout_possible: bool = Field(default=False, description="Whether candidate indicated notice buyout is possible.")
    status: str = Field(default="STANDARD", description="IMMEDIATE, STANDARD, EXTENDED, or UNKNOWN.")
    summary: str = Field(description="Recruiter-friendly summary explanation of availability and start timeline.")


class SkillConfirmationHighlight(BaseModel):
    """Analysis of candidate technical skills confirmed vs required."""
    confirmed_skills: List[str] = Field(default_factory=list, description="Skills explicitly validated through responses.")
    missing_mandatory_skills: List[str] = Field(default_factory=list, description="Mandatory role skills not demonstrated.")
    bonus_skills_found: List[str] = Field(default_factory=list, description="Additional beneficial skills mentioned.")
    skill_match_percentage: float = Field(ge=0.0, le=100.0, description="Percentage match against required skills.")
    strongest_areas: List[str] = Field(default_factory=list, description="Top validated domains or competencies.")
    areas_for_validation: List[str] = Field(default_factory=list, description="Areas requiring technical deep-dive.")
    status: str = Field(default="FULLY_CONFIRMED", description="FULLY_CONFIRMED, PARTIAL_MATCH, or CRITICAL_GAPS.")
    summary: str = Field(description="Recruiter-friendly summary of skill match and depth.")


class KeyAnswerSummary(BaseModel):
    """Concise distillation of a candidate answer to a pivotal screening question."""
    question_id: str
    category: str
    question_text: str
    candidate_answer: str
    answer_summary: str = Field(description="Crisp 1-2 sentence distillation of what the candidate conveyed.")
    score: float = Field(ge=0.0, le=100.0)
    grade: str = Field(description="EXCELLENT, STRONG, MODERATE, POOR, or UNSATISFACTORY.")
    key_takeaways: List[str] = Field(default_factory=list, description="Key bullet takeaways for the recruiter.")


class CandidateRisk(BaseModel):
    """Identified concern, red flag, or risk factor."""
    risk_id: str
    category: RiskCategory
    severity: RiskSeverity
    title: str
    description: str
    evidence: Optional[str] = Field(default=None, description="Transcript quote or data point supporting the risk.")
    mitigation_or_probe: str = Field(description="Suggested next step or question to mitigate or verify the risk.")


class MissingDataGap(BaseModel):
    """Unaddressed or ambiguous information required for hiring decisions."""
    gap_id: str
    field_name: str
    impact: DataGapImpact
    description: str
    suggested_action: str = Field(description="Action for the recruiter or technical interviewer to close this gap.")


class ScoreSummary(BaseModel):
    """Aggregated multi-dimensional score summary."""
    overall_score: float = Field(ge=0.0, le=100.0)
    technical_score: float = Field(ge=0.0, le=100.0)
    communication_score: float = Field(ge=0.0, le=100.0)
    relevance_score: float = Field(ge=0.0, le=100.0)
    confidence_score: float = Field(ge=0.0, le=100.0)
    overall_grade: str = Field(description="EXCELLENT (85+), STRONG (70-84), MODERATE (55-69), POOR (<55).")


class ScreeningReport(BaseModel):
    """Complete, recruiter-ready AI screening report."""
    report_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    role_name: str
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    recommendation: HiringRecommendation
    recommendation_badge: str = Field(description="Human-readable badge text (e.g., 'Strong Hire', 'Proceed with Caution').")
    executive_summary: str = Field(description="Concise 3-4 sentence narrative executive summary for hiring managers.")
    scores: ScoreSummary
    salary_highlight: SalaryHighlight
    availability_highlight: AvailabilityHighlight
    skills_highlight: SkillConfirmationHighlight
    strengths: List[str] = Field(default_factory=list, description="Top positive candidate attributes and advantages.")
    risks: List[CandidateRisk] = Field(default_factory=list, description="Concerns, red flags, or risk factors.")
    missing_data_gaps: List[MissingDataGap] = Field(default_factory=list, description="Information gaps requiring resolution.")
    key_answers: List[KeyAnswerSummary] = Field(default_factory=list, description="Distilled summaries of pivotal questions.")
    behavioral_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Day 27 behavioral metrics (WPM, sentiment, pacing, confidence)."
    )
    recommended_interviewer_probes: List[str] = Field(
        default_factory=list,
        description="Specific technical questions for Round-2 human interviewers."
    )
    report_version: str = "1.0.0"
