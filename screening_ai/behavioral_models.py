"""
Day 27: Behavioral Models and Schemas
=====================================
Pydantic schemas and enums for Confidence Analysis, Response Pacing,
Sentiment Scoring, Uncertainty/Contradiction detection, and
Communication Strength Indicators.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HesitationType(str, Enum):
    FILLER_WORD = "FILLER_WORD"
    EXTENDED_PAUSE = "EXTENDED_PAUSE"
    REPETITION = "REPETITION"
    FALSE_START = "FALSE_START"
    LATENCY_DELAY = "LATENCY_DELAY"


class PaceRating(str, Enum):
    VERY_SLOW = "VERY_SLOW"      # < 100 WPM
    SLOW = "SLOW"                # 100 - 120 WPM
    OPTIMAL = "OPTIMAL"          # 120 - 165 WPM
    FAST = "FAST"                # 165 - 185 WPM
    RUSHED = "RUSHED"            # > 185 WPM


class SentimentPolarity(str, Enum):
    VERY_POSITIVE = "VERY_POSITIVE"  # Compound > 0.5
    POSITIVE = "POSITIVE"            # Compound 0.15 to 0.5
    NEUTRAL = "NEUTRAL"              # Compound -0.15 to 0.15
    NEGATIVE = "NEGATIVE"            # Compound -0.5 to -0.15
    DEFENSIVE = "DEFENSIVE"          # Explicit defensive / hostile language


class EngagementLevel(str, Enum):
    HIGHLY_ENGAGED = "HIGHLY_ENGAGED"
    COOPERATIVE = "COOPERATIVE"
    PASSIVE = "PASSIVE"
    RELUCTANT = "RELUCTANT"
    DEFENSIVE = "DEFENSIVE"


class CommunicationGrade(str, Enum):
    EXCELLENT = "EXCELLENT"          # >= 85
    GOOD = "GOOD"                    # 72 - 84
    ACCEPTABLE = "ACCEPTABLE"        # 60 - 71
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"  # < 60


class HesitationIncident(BaseModel):
    """Specific hesitation event detected in spoken candidate audio or transcript."""
    type: HesitationType
    pattern: str
    count: int = 1
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None
    penalty: float = Field(default=0.0, description="Confidence deduction for this hesitation event.")
    description: str


class PaceMetrics(BaseModel):
    """Rhythm, duration, and Words Per Minute (WPM) metrics for a response."""
    duration_seconds: float = Field(ge=0.0)
    word_count: int = Field(ge=0)
    wpm: float = Field(ge=0.0, description="Words Per Minute pace.")
    pace_rating: PaceRating
    latency_ms: Optional[int] = Field(default=None, description="Pause duration before candidate began speaking.")
    latency_rating: Optional[str] = None
    pacing_score: float = Field(ge=0.0, le=100.0, description="Pacing quality score (optimal around 130-160 WPM).")


class UncertaintySignal(BaseModel):
    """Detection of epistemic hedges, qualifiers, and uncertain statements."""
    hedging_phrases: List[str] = Field(default_factory=list)
    hedging_count: int = 0
    uncertainty_score: float = Field(ge=0.0, le=100.0, description="0 is completely certain, 100 is highly uncertain.")
    confidence_discount: float = Field(default=0.0, description="Confidence penalty incurred by uncertainty.")
    flagged_statements: List[str] = Field(default_factory=list)


class TurnConfidenceMetrics(BaseModel):
    """Consolidated confidence breakdown for a single candidate turn."""
    raw_confidence: float = Field(ge=0.0, le=100.0)
    hesitation_incidents: List[HesitationIncident] = Field(default_factory=list)
    total_hesitation_penalty: float = 0.0
    pace_metrics: PaceMetrics
    uncertainty: UncertaintySignal
    final_confidence_score: float = Field(ge=0.0, le=100.0)
    confidence_tier: str = Field(description="HIGH (>=80), MODERATE (60-79), LOW (<60).")


class SentimentAnalysisResult(BaseModel):
    """Sentiment polarity and emotional demeanor metrics."""
    polarity: SentimentPolarity
    compound_score: float = Field(ge=-1.0, le=1.0, description="Compound sentiment score from -1.0 to +1.0.")
    positive_score: float = Field(ge=0.0, le=1.0)
    neutral_score: float = Field(ge=0.0, le=1.0)
    negative_score: float = Field(ge=0.0, le=1.0)
    engagement_level: EngagementLevel
    positive_keywords: List[str] = Field(default_factory=list)
    negative_keywords: List[str] = Field(default_factory=list)
    defensive_keywords: List[str] = Field(default_factory=list)
    emotional_tone: str = Field(description="Human-readable tone summary (e.g. enthusiastic, cooperative, defensive).")


class CommunicationStrengthIndicator(BaseModel):
    """Granular communication competencies scored from 0 to 100."""
    fluency_score: float = Field(ge=0.0, le=100.0, description="Smoothness of speech without verbal stumbles.")
    assertiveness_score: float = Field(ge=0.0, le=100.0, description="Directness without excessive hedging.")
    engagement_score: float = Field(ge=0.0, le=100.0, description="Enthusiasm and constructive collaborative tone.")
    pacing_score: float = Field(ge=0.0, le=100.0, description="Control over speaking speed and pauses.")
    articulation_score: float = Field(ge=0.0, le=100.0, description="Clarity and substance of spoken thoughts.")
    overall_strength_score: float = Field(ge=0.0, le=100.0, description="Weighted aggregate communication strength.")
    grade: CommunicationGrade
    summary: str


class TurnBehavioralAnalysis(BaseModel):
    """Consolidated behavioral and communication analysis for a single candidate turn."""
    turn_id: str
    speaker: str = "CANDIDATE"
    raw_text: str
    confidence_metrics: TurnConfidenceMetrics
    sentiment: SentimentAnalysisResult
    communication_indicators: CommunicationStrengthIndicator
    key_observations: List[str] = Field(default_factory=list)


class BehavioralIndicatorsReport(BaseModel):
    """Comprehensive interview session behavioral and communication report for recruiters."""
    candidate_id: str
    session_id: str
    total_turns_analyzed: int
    overall_confidence_score: float = Field(ge=0.0, le=100.0)
    overall_sentiment: SentimentPolarity
    average_compound_sentiment: float = Field(ge=-1.0, le=1.0)
    average_wpm: float = Field(ge=0.0)
    overall_pace_rating: PaceRating
    communication_indicators: CommunicationStrengthIndicator
    behavioral_green_flags: List[str] = Field(default_factory=list)
    behavioral_red_flags: List[str] = Field(default_factory=list)
    recruiter_executive_summary: str
    recommended_interviewer_probes: List[str] = Field(default_factory=list)
    turn_breakdowns: List[TurnBehavioralAnalysis] = Field(default_factory=list)
