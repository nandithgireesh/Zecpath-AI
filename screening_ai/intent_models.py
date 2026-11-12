from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CandidateIntent(str, Enum):
    PROVIDING_EXPERIENCE = "PROVIDING_EXPERIENCE"
    CONFIRMING_SKILL = "CONFIRMING_SKILL"
    DECLINING_SKILL = "DECLINING_SKILL"
    STATING_SALARY = "STATING_SALARY"
    STATING_AVAILABILITY = "STATING_AVAILABILITY"
    ASKING_CLARIFICATION = "ASKING_CLARIFICATION"
    OFF_TOPIC = "OFF_TOPIC"
    VAGUE_ANSWER = "VAGUE_ANSWER"
    GENERAL_ACKNOWLEDGEMENT = "GENERAL_ACKNOWLEDGEMENT"


class ProficiencyLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    UNSPECIFIED = "UNSPECIFIED"


class SkillDetail(BaseModel):
    skill: str
    proficiency: ProficiencyLevel = ProficiencyLevel.UNSPECIFIED
    years_used: Optional[float] = None
    sentiment: str = "positive"
    is_confirmed: bool = True


class ExperienceDetail(BaseModel):
    total_years: Optional[float] = None
    primary_role: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    key_technologies: List[str] = Field(default_factory=list)
    responsibilities_summary: Optional[str] = None


class AvailabilityDetail(BaseModel):
    notice_period_days: Optional[int] = None
    is_immediate_joiner: bool = False
    can_buyout_notice: bool = False
    serving_notice: bool = False
    earliest_join_date: Optional[str] = None


class SalaryDetail(BaseModel):
    current_ctc_lpa: Optional[float] = None
    expected_ctc_lpa: Optional[float] = None
    is_negotiable: bool = True
    flexibility_note: Optional[str] = None


class SemanticQualityScore(BaseModel):
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    clarity_score: float = Field(default=1.0, ge=0.0, le=1.0)
    is_off_topic: bool = False
    is_vague: bool = False
    missing_slots: List[str] = Field(default_factory=list)
    follow_up_needed: bool = False


class StructuredAnswerObject(BaseModel):
    turn_id: Optional[str] = None
    question_id: Optional[str] = None
    question_category: Optional[str] = None
    raw_text: str
    cleaned_text: str
    primary_intent: CandidateIntent = CandidateIntent.GENERAL_ACKNOWLEDGEMENT
    intent_confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    secondary_intents: List[CandidateIntent] = Field(default_factory=list)
    extracted_skills: List[SkillDetail] = Field(default_factory=list)
    experience: Optional[ExperienceDetail] = None
    availability: Optional[AvailabilityDetail] = None
    salary: Optional[SalaryDetail] = None
    quality: SemanticQualityScore = Field(default_factory=SemanticQualityScore)
    follow_up_recommendation: Optional[str] = None
