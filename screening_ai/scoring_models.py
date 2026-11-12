from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ScoringDimension(str, Enum):
    CLARITY = "CLARITY"
    RELEVANCE = "RELEVANCE"
    COMPLETENESS = "COMPLETENESS"
    CONSISTENCY = "CONSISTENCY"


class RecommendationTier(str, Enum):
    STRONGLY_RECOMMENDED = "STRONGLY_RECOMMENDED"
    RECOMMENDED = "RECOMMENDED"
    RECOMMENDED_WITH_RESERVATIONS = "RECOMMENDED_WITH_RESERVATIONS"
    NOT_RECOMMENDED = "NOT_RECOMMENDED"


class ScoreGrade(str, Enum):
    EXCELLENT = "EXCELLENT"          # 85 - 100
    STRONG = "STRONG"                # 70 - 84
    MODERATE = "MODERATE"            # 55 - 69
    POOR = "POOR"                    # 40 - 54
    UNSATISFACTORY = "UNSATISFACTORY" # 0 - 39


class DimensionScore(BaseModel):
    dimension: ScoringDimension
    score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(default=0.25, ge=0.0, le=1.0)
    weighted_score: float = Field(default=0.0, ge=0.0, le=100.0)
    explanation: str = ""
    penalties_applied: List[str] = Field(default_factory=list)


class QuestionScoreBreakdown(BaseModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    question_category: Optional[str] = None
    raw_answer: str
    cleaned_answer: str
    clarity_score: float = Field(..., ge=0.0, le=100.0)
    relevance_score: float = Field(..., ge=0.0, le=100.0)
    completeness_score: float = Field(..., ge=0.0, le=100.0)
    consistency_score: float = Field(..., ge=0.0, le=100.0)
    weighted_question_score: float = Field(..., ge=0.0, le=100.0)
    grade: ScoreGrade = ScoreGrade.MODERATE
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    penalties: List[str] = Field(default_factory=list)
    explanation: str = ""
    dimension_scores: Dict[str, DimensionScore] = Field(default_factory=dict)


class CategoryScoreSummary(BaseModel):
    category: str
    average_score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(default=0.25, ge=0.0, le=1.0)
    weighted_contribution: float = Field(default=0.0, ge=0.0, le=100.0)
    question_count: int = 1


class ExplainableReport(BaseModel):
    executive_summary: str
    key_strengths: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    consistency_audit: Dict[str, Any] = Field(default_factory=dict)
    recommended_interview_probes: List[str] = Field(default_factory=list)


class FinalScreeningScoreObject(BaseModel):
    candidate_id: Optional[str] = None
    call_id: Optional[str] = None
    job_id: Optional[str] = None
    overall_score: float = Field(..., ge=0.0, le=100.0)
    normalized_score: float = Field(..., ge=0.0, le=1.0)
    recommendation_tier: RecommendationTier
    grade: ScoreGrade
    dimension_averages: Dict[str, float] = Field(default_factory=dict)
    category_breakdowns: Dict[str, CategoryScoreSummary] = Field(default_factory=dict)
    per_question_breakdowns: List[QuestionScoreBreakdown] = Field(default_factory=list)
    explainability: ExplainableReport
    evaluated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
