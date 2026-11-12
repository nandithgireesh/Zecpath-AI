"""
Day 39: HR Interview Summary Generator Data Models
===================================================
Pydantic data models and enumerations defining recruiter-ready insights:
- Structured candidate strengths and weaknesses
- Cultural fit dimensions and indicators
- Cross-turn and cross-modal inconsistency detection
- Overall HR performance summary and readiness tiers
- Natural-language recruiter dossier schemas
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .hr_scoring_models import HiringRecommendation


class CulturalFitDimension(str, Enum):
    """Core organizational culture and behavioral alignment dimensions."""
    OWNERSHIP_AND_ACCOUNTABILITY = "ownership_and_accountability"  # Owning outcomes vs blame deflection
    COLLABORATION_AND_TEAMWORK = "collaboration_and_teamwork"      # Cross-functional empathy and mentorship
    CUSTOMER_CENTRICITY = "customer_centricity"                    # SLA prioritization and user impact
    ADAPTABILITY_AND_GROWTH = "adaptability_and_growth"            # Navigating ambiguity and continuous learning
    TRANSPARENCY_AND_ETHICS = "transparency_and_ethics"            # Compliance, data privacy, and integrity


class InconsistencyType(str, Enum):
    """Categorization of detected candidate contradictions and discrepancies."""
    FACTUAL_EXPERIENCE_MISMATCH = "factual_experience_mismatch"      # Claims conflict with resume/profile
    CROSS_TURN_CONTRADICTION = "cross_turn_contradiction"            # Turn A statement conflicts with Turn B
    VERBAL_AFFECT_DISCORDANCE = "verbal_affect_discordance"          # Overconfident speech vs stress/hesitation spike
    COMPETENCY_PERFORMANCE_GAP = "competency_performance_gap"        # Claimed seniority vs flawed execution/fallacies
    ROLE_LEVELING_DISCREPANCY = "role_leveling_discrepancy"          # Junior operational mindset for senior candidate


class InconsistencySeverity(str, Enum):
    """Severity tier for detected discrepancies."""
    CRITICAL = "CRITICAL"  # High risk: direct factual fabrication or severe operational contradiction
    MODERATE = "MODERATE"  # Notable gap: noticeable inflation or conflicting claims requiring probing
    MINOR = "MINOR"        # Slight variance: minor phrasing divergence or mild hesitation discordance


class InconsistencyFlag(BaseModel):
    """Specific inconsistency identified during the interview session."""
    inconsistency_id: str = Field(..., description="Unique discrepancy identifier (e.g., INC-01)")
    inconsistency_type: InconsistencyType = Field(..., description="Type of detected inconsistency")
    severity: InconsistencySeverity = Field(..., description="Risk severity tier")
    claim_source: str = Field(..., description="Source of primary claim (e.g., Resume / Turn 1)")
    contradicting_source: str = Field(..., description="Contradicting statement (e.g., Turn 4 SJT)")
    claimed_statement: str = Field(..., description="Excerpt of the original claim")
    contradicting_statement: str = Field(..., description="Excerpt of the conflicting response")
    explanation: str = Field(..., description="Recruiter-facing explanation of why this is contradictory")
    recommended_probing_question: str = Field(..., description="Specific question for hiring manager follow-up")


class CulturalFitAssessment(BaseModel):
    """Evaluation of candidate alignment with a specific cultural dimension."""
    dimension: CulturalFitDimension = Field(..., description="Cultural dimension evaluated")
    score: float = Field(..., ge=0.0, le=100.0, description="Calibrated alignment score (0-100)")
    alignment_level: str = Field(..., description="Alignment tier: EXEMPLARY, STRONG, MODERATE, WEAK")
    evidence_excerpts: List[str] = Field(default_factory=list, description="Direct candidate quotes demonstrating alignment")
    observations: str = Field(..., description="Synthesized behavioral observation")


class OverallHRPerformanceSummary(BaseModel):
    """Synthesized overall HR performance across all evaluated modules."""
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Holistic composite score (0-100)")
    behavioral_competency_score: float = Field(..., ge=0.0, le=100.0, description="STAR and leadership execution score")
    communication_clarity_score: float = Field(..., ge=0.0, le=100.0, description="Fluency, hygiene, and structure score")
    confidence_composure_score: float = Field(..., ge=0.0, le=100.0, description="Composure and stress resilience score")
    cognitive_aptitude_score: float = Field(..., ge=0.0, le=100.0, description="Logical reasoning and SJT score")
    recommendation: HiringRecommendation = Field(..., description="Calibrated hiring verdict")
    readiness_level: str = Field(..., description="Candidate organizational readiness tier")
    calibrated_role_tier: str = Field(..., description="Recommended role level (e.g. Senior Lead, Mid-Level)")
    executive_verdict: str = Field(..., description="High-level briefing sentence for executive decision makers")


class NaturalLanguageDossier(BaseModel):
    """Synthesized natural language briefing paragraphs for hiring managers."""
    executive_overview: str = Field(..., description="Comprehensive executive summary of the candidate")
    communication_persona: str = Field(..., description="Natural language appraisal of communication style and presence")
    behavioral_and_cultural_fit: str = Field(..., description="Analysis of team dynamics, ethics, and cultural alignment")
    cognitive_and_technical_maturity: str = Field(..., description="Appraisal of problem-solving rigor and trade-off analysis")
    inconsistency_and_risk_analysis: str = Field(..., description="Narrative overview of identified contradictions and red flags")
    hiring_manager_action_plan: str = Field(..., description="Recommended focus areas and next steps for on-site debrief")
    targeted_interview_probes: List[str] = Field(default_factory=list, description="Targeted probing questions for follow-up")


class CandidateInterviewSummary(BaseModel):
    """Master candidate interview summary document mandated by Day 39 curriculum."""
    # Metadata
    summary_id: str = Field(..., description="Unique summary report ID")
    candidate_id: str = Field(..., description="Candidate unique ID")
    candidate_name: str = Field(..., description="Candidate full name")
    job_role: str = Field(..., description="Target role applied for")
    experience_years: float = Field(..., description="Years of professional experience")
    session_id: str = Field(..., description="Associated interview session ID")
    generated_at: str = Field(..., description="ISO timestamp of summary generation")

    # Overall HR Performance
    overall_performance: OverallHRPerformanceSummary = Field(..., description="Multi-dimensional performance synthesis")

    # Structured Insights
    candidate_strengths: List[str] = Field(default_factory=list, description="Key candidate strengths with evidence")
    candidate_weaknesses: List[str] = Field(default_factory=list, description="Key candidate developmental areas/weaknesses")
    cultural_fit_indicators: List[CulturalFitAssessment] = Field(default_factory=list, description="Cultural dimension ratings")
    risk_flags: List[str] = Field(default_factory=list, description="Critical risk indicators, biases, or compliance alerts")
    inconsistencies: List[InconsistencyFlag] = Field(default_factory=list, description="Cross-turn and cross-modal contradictions")

    # Natural Language Recruiter Report
    natural_language_report: NaturalLanguageDossier = Field(..., description="Recruiter-ready natural-language narrative dossier")
