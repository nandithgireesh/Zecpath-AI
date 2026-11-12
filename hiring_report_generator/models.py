"""
Day 53: Hiring Intelligence Report Generator - Domain Models (Deliverable 2 & 3)
================================================================================
Comprehensive, recruiter-friendly data schemas encapsulating:
- Full Candidate AI Profile Report (ATS, Screening, HR, Technical, Behavioral)
- Categorized Highlights: Strengths, Weaknesses, Risk Indicators
- Final Recommendation & Recruiter TL;DR Summary
- Export format schemas and cryptographic audit sealing
"""

import json
import hashlib
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# ==============================================================================
# 1. CORE ENUMS & TAXONOMIES
# ==============================================================================

class HighlightType(str, Enum):
    STRENGTH = "STRENGTH"
    WEAKNESS = "WEAKNESS"
    RISK_INDICATOR = "RISK_INDICATOR"


class CompetencyPillar(str, Enum):
    ATS_RESUME = "ATS_RESUME"
    SCREENING = "SCREENING"
    HR_INTERVIEW = "HR_INTERVIEW"
    TECHNICAL_EVALUATION = "TECHNICAL_EVALUATION"
    BEHAVIORAL_INTEGRITY = "BEHAVIORAL_INTEGRITY"


class ImpactLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReportExportFormat(str, Enum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    EXECUTIVE_CARD = "EXECUTIVE_CARD"


# ==============================================================================
# 2. MULTI-PILLAR REPORT SECTIONS
# ==============================================================================

class ATSSummarySection(BaseModel):
    """Resume keyword match, credentials, domain fit, and background telemetry."""
    ats_score: float = Field(..., ge=0.0, le=100.0, description="Composite ATS resume match score")
    keyword_match_rate: float = Field(..., ge=0.0, le=100.0, description="Job description keyword overlap %")
    experience_years: float = Field(..., ge=0.0, description="Total verified professional experience")
    education_tier: str = Field(..., description="Highest verified degree / accreditation tier")
    matched_skills: List[str] = Field(default_factory=list, description="Primary technical skills verified")
    missing_skills: List[str] = Field(default_factory=list, description="Desired JD skills missing from resume")
    summary_notes: str = Field(..., description="Recruiter-friendly resume analysis overview")


class ScreeningResultsSection(BaseModel):
    """Initial phone/automated screening performance and baseline qualifications."""
    screening_score: float = Field(..., ge=0.0, le=100.0, description="Screening round performance score")
    communication_clarity: str = Field(..., description="Verbal articulation & clarity rating")
    qualification_fit: str = Field(..., description="Role prerequisite match status")
    availability_timeline: str = Field(..., description="Notice period / start date availability")
    screening_notes: str = Field(..., description="Screening interviewer notes & assessment")


class HRInsightsSection(BaseModel):
    """STAR behavioral methodology, culture alignment, motivation, and leadership."""
    hr_score: float = Field(..., ge=0.0, le=100.0, description="HR behavioral interview score")
    star_method_rating: float = Field(..., ge=0.0, le=100.0, description="Adherence to STAR structure")
    leadership_teamwork_index: float = Field(..., ge=0.0, le=100.0, description="Collaboration & ownership metric")
    cultural_values_alignment: str = Field(..., description="Alignment with corporate core principles")
    motivation_and_adaptability: str = Field(..., description="Career trajectory motivation and adaptability")
    hr_interview_notes: str = Field(..., description="Summary of HR behavioral insights")


class TechnicalPerformanceSection(BaseModel):
    """System design, live coding, machine test sandbox execution, and code quality."""
    technical_interview_score: float = Field(..., ge=0.0, le=100.0, description="Technical interview round score")
    machine_test_sandbox_score: float = Field(..., ge=0.0, le=100.0, description="Automated sandbox code score")
    architecture_design_score: float = Field(..., ge=0.0, le=100.0, description="Distributed systems & design rating")
    test_suite_pass_rate: float = Field(..., ge=0.0, le=100.0, description="Sandbox test suite pass percentage")
    code_quality_and_cleanliness: str = Field(..., description="Clean architecture, SOLID principles rating")
    technical_notes: str = Field(..., description="Hands-on engineering delivery analysis")


class BehavioralAndRiskSection(BaseModel):
    """Stress indices, speech fluency, proctoring integrity, and variance stability."""
    stress_index: float = Field(..., ge=0.0, le=100.0, description="Voice pitch / hesitation stress index")
    hesitation_pause_count: int = Field(..., ge=0, description="Unusually long pauses (>4s)")
    speech_fluency_rating: str = Field(..., description="Verbal fluency & filler crutch analysis")
    integrity_penalty_points: float = Field(..., ge=0.0, description="Deductions from malpractice events")
    malpractice_breaches_detected: int = Field(..., ge=0, description="Disqualifying malpractice violations")
    cross_round_std_dev: float = Field(..., ge=0.0, description="Cross-stage score standard deviation")
    overall_risk_level: str = Field(..., description="Composite risk tier: LOW, MODERATE, HIGH, CRITICAL")


# ==============================================================================
# 3. HIGHLIGHTS: STRENGTHS, WEAKNESSES & RISK INDICATORS
# ==============================================================================

class CompetencyHighlight(BaseModel):
    """Specific positive driver, growth weakness, or critical risk indicator."""
    highlight_id: str = Field(..., description="Unique highlight identifier")
    highlight_type: HighlightType = Field(..., description="STRENGTH, WEAKNESS, or RISK_INDICATOR")
    pillar: CompetencyPillar = Field(..., description="Originating assessment pillar")
    title: str = Field(..., description="Short recruiter headline")
    description: str = Field(..., description="Detailed contextual reasoning")
    impact: ImpactLevel = Field(default=ImpactLevel.MEDIUM, description="Impact level on overall candidacy")


# ==============================================================================
# 4. FINAL RECOMMENDATION & RECRUITER ACTION SUMMARY
# ==============================================================================

class FinalRecommendationSummary(BaseModel):
    """Culmination of Day 52 final recommendation with recruiter next steps."""
    decision_category: str = Field(..., description="SELECTED, HOLD_REVIEW, or REJECTED")
    decision_substatus: str = Field(..., description="Granular operational status")
    hiring_fit_score: float = Field(..., ge=0.0, le=100.0, description="Calibrated composite fit %")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Certainty score (0-100%)")
    confidence_band: str = Field(..., description="Confidence tier: VERY_HIGH, HIGH, MODERATE, LOW")
    executive_rationale: str = Field(..., description="Concise briefing for hiring managers")
    recommended_action: str = Field(..., description="Actionable next operational step for recruiting team")
    counterfactual_advice: Optional[str] = Field(None, description="Specific delta required for upgrade")


# ==============================================================================
# 5. FULL CANDIDATE AI PROFILE REPORT (DELIVERABLE 2)
# ==============================================================================

class CandidateAIProfileReport(BaseModel):
    """
    Deliverable 2: Complete AI-Generated Candidate Evaluation Report.
    Combines ATS, screening, HR, technical, and behavioral telemetry into a single,
    recruiter-friendly dossier sealed with SHA-256 for audit compliance.
    """
    report_id: str = Field(..., description="Unique report identifier")
    candidate_id: str = Field(..., description="Unique candidate ID")
    candidate_name: str = Field(..., description="Candidate full name")
    target_role: str = Field(..., description="Role being evaluated for")
    experience_tier: str = Field(..., description="Seniority tier")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    generator_version: str = "1.0.0-PROD"

    # Multi-Pillar Deep Dive Sections
    ats_summary: ATSSummarySection
    screening_results: ScreeningResultsSection
    hr_insights: HRInsightsSection
    technical_performance: TechnicalPerformanceSection
    behavioral_and_risk: BehavioralAndRiskSection

    # Highlights (Strengths, Weaknesses, Risk Indicators)
    strengths: List[CompetencyHighlight] = Field(default_factory=list)
    weaknesses: List[CompetencyHighlight] = Field(default_factory=list)
    risk_indicators: List[CompetencyHighlight] = Field(default_factory=list)

    # Final Decision & Recruiter TL;DR
    final_recommendation: FinalRecommendationSummary
    recruiter_tldr: str = Field(..., description="30-second one-paragraph executive summary for recruiters")

    # Audit & Verification
    generation_latency_ms: float = 0.0
    audit_hash: str = ""

    def compute_sha256_audit_seal(self) -> str:
        """Computes deterministic SHA-256 seal for tamper-evident compliance."""
        payload = {
            "report_id": self.report_id,
            "candidate_id": self.candidate_id,
            "target_role": self.target_role,
            "decision": self.final_recommendation.decision_category,
            "substatus": self.final_recommendation.decision_substatus,
            "hiring_fit": round(self.final_recommendation.hiring_fit_score, 2),
            "confidence": round(self.final_recommendation.confidence_score, 2),
            "strengths_count": len(self.strengths),
            "weaknesses_count": len(self.weaknesses),
            "risks_count": len(self.risk_indicators),
        }
        raw_json = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    def finalize_and_seal(self) -> None:
        """Locks the report with a cryptographic audit signature."""
        self.audit_hash = self.compute_sha256_audit_seal()
