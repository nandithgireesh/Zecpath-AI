"""
Day 33: HR Interview Engine Models & State Schemas
===================================================
Defines foundational data structures for the AI HR Interview system:
- 6 HR Interview Categories (Self-intro, Career journey, Strengths/weaknesses, Teamwork/culture, Career goals, Availability)
- 4 Role & Experience Matrix Quadrants (Fresher vs Experienced x Technical vs Non-Technical)
- 4 Conversation Phases (Introduction, Core HR, Role-based Evaluation, Closing)
- Interview State tracking: Question ID, response capture, and follow-up eligibility triggers
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from interview_ai.confidence_models import TurnConfidenceBreakdown


# =====================================================
# 1. Core Enumerations
# =====================================================

class HRCategory(str, Enum):
    """The 6 mandatory HR interview categories defined in Day 33 curriculum."""
    SELF_INTRODUCTION = "self_introduction"
    CAREER_JOURNEY = "career_journey"
    STRENGTHS_AND_WEAKNESSES = "strengths_and_weaknesses"
    TEAMWORK_AND_CULTURE_FIT = "teamwork_and_culture_fit"
    CAREER_GOALS = "career_goals"
    AVAILABILITY_AND_COMMITMENT = "availability_and_commitment"


class ExperienceTier(str, Enum):
    """Candidate experience level governing question depth and expectations."""
    FRESHER = "fresher"            # 0 to 1 year: Academic projects, internships, learning aptitude
    EXPERIENCED = "experienced"    # 2+ years: Production impact, stakeholder management, system ownership


class RoleTrack(str, Enum):
    """Role domain track tailoring behavioral scenarios."""
    TECHNICAL = "technical"          # Engineering, DevOps, Data Science, QA, Cloud, Architecture
    NON_TECHNICAL = "non_technical"  # Sales, Marketing, HR, Finance, Operations, Product Management


class InterviewPhase(str, Enum):
    """The 4 sequential conversation phases of an HR interview."""
    INTRODUCTION = "introduction"                        # Phase 1: Greeting, purpose, self-introduction
    CORE_HR = "core_hr"                                  # Phase 2: Strengths, weaknesses, culture fit, teamwork
    ROLE_BASED_EVALUATION = "role_based_evaluation"      # Phase 3: Career journey & role-specific behavioral scenarios
    CLOSING = "closing"                                  # Phase 4: Career goals, availability, candidate Q&A


class FollowUpTriggerReason(str, Enum):
    """Reasons triggering adaptive follow-up probing."""
    NONE = "none"
    TERSE_RESPONSE = "terse_response"          # Less than 15 words; lacked sufficient detail
    MISSING_METRIC = "missing_metric"          # Did not state measurable outcome or concrete metric
    VAGUE_CONTRIBUTION = "vague_contribution"  # Used "we" without clarifying individual responsibility
    CONFLICT_AVOIDANCE = "conflict_avoidance"  # Avoided answering interpersonal challenge
    SURFACE_LEVEL = "surface_level"            # Generic buzzwords without practical examples
    CLICHE_PLATITUDE = "cliche_platitude"      # Cliché without genuine introspection ("perfectionist")
    AMBIGUOUS_TERMS = "ambiguous_terms"        # Unexplained acronyms or vague jargon
    THEORETICAL_ONLY = "theoretical_only"      # Textbook theory without personal experience
    HIGH_CONFIDENCE = "high_confidence"        # Advanced confidence warranting scenario challenge


class FollowUpProbeCategory(str, Enum):
    """Standardized Day 34 follow-up probing categories."""
    NONE = "none"
    CLARIFICATION = "clarification"          # Clarify ambiguous terms, acronyms, or terse fragments
    DEEPENING = "deepening"                  # Deepen technical mechanics, data structures, trade-offs
    EXAMPLE_BASED = "example_based"          # Request concrete STAR past situations & measurable impact
    SCENARIO_CHALLENGE = "scenario_challenge"# Complex real-world failure, scale, or dilemma scenario


class AdaptationTier(str, Enum):
    """Dynamic difficulty adaptation tiers based on candidate response sophistication."""
    STANDARD = "standard"                    # Normal conversational progression
    DEEP_PROBE = "deep_probe"                # Simple response -> Deeper probe to test depth
    SCENARIO_CHALLENGE = "scenario_challenge"# Confident response -> Scenario-based challenge


# =====================================================
# 2. Question Template & Bank Schemas
# =====================================================

class HRQuestionTemplate(BaseModel):
    """Template for role- and experience-calibrated HR interview questions."""
    question_id: str = Field(..., description="Unique immutable question identifier (e.g. HR-INTRO-F-TECH-01)")
    category: HRCategory = Field(..., description="HR category classification")
    experience_tier: ExperienceTier = Field(..., description="Target experience level")
    role_track: RoleTrack = Field(..., description="Target role domain")
    phase: InterviewPhase = Field(..., description="Conversation phase in which this question is asked")
    prompt_text: str = Field(..., description="Main spoken AI prompt")
    follow_up_prompt: str = Field(..., description="Micro-probing question if answer is incomplete or terse")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Target rubric indicators")
    expected_competencies: List[str] = Field(default_factory=list, description="Key skills/traits assessed")


# =====================================================
# 3. Turn & Session State Schemas
# =====================================================

class CommunicationScoreBreakdown(BaseModel):
    """Detailed multi-dimensional communication evaluation breakdown."""
    fluency_score: float = Field(0.0, ge=0.0, le=100.0, description="Sentence continuity & flow (0-100)")
    grammar_score: float = Field(0.0, ge=0.0, le=100.0, description="Grammar quality & agreement (0-100)")
    vocabulary_score: float = Field(0.0, ge=0.0, le=100.0, description="Lexical range & domain sophistication (0-100)")
    clarity_score: float = Field(0.0, ge=0.0, le=100.0, description="Readability, idea density & clarity (0-100)")
    filler_score: float = Field(0.0, ge=0.0, le=100.0, description="Filler word discipline (0-100, 100=clean)")
    structure_score: float = Field(0.0, ge=0.0, le=100.0, description="Answer structure (STAR/PREP alignment) (0-100)")
    raw_composite_score: float = Field(0.0, ge=0.0, le=100.0, description="Weighted composite communication score before normalization")
    normalized_score: float = Field(0.0, ge=0.0, le=100.0, description="Bias-normalized communication score (0-100)")
    detected_fillers: Dict[str, int] = Field(default_factory=dict, description="Counts of detected filler words")
    filler_count: int = Field(0, description="Total filler words detected")
    filler_percentage: float = Field(0.0, description="Filler word percentage relative to total words")
    structure_framework: str = Field("UNSTRUCTURED", description="Detected structural pattern (STAR, PREP, or UNSTRUCTURED)")
    structure_elements_detected: List[str] = Field(default_factory=list, description="Specific elements matched (e.g. ['Situation', 'Action'])")
    strengths: List[str] = Field(default_factory=list, description="Identified communication strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Targeted communication coaching feedback")


class InterviewTurnState(BaseModel):
    """State record capturing an individual conversational turn."""
    turn_index: int = Field(..., description="Sequential turn index (1-based)")
    phase: InterviewPhase = Field(..., description="Current conversation phase")
    category: HRCategory = Field(..., description="HR category assessed in this turn")
    question_id: str = Field(..., description="Unique question ID")
    ai_prompt: str = Field(..., description="Spoken prompt presented to candidate")
    candidate_response: Optional[str] = Field(None, description="Captured candidate speech transcript")
    response_timestamp: Optional[str] = Field(None, description="ISO-8601 UTC timestamp of candidate response")
    word_count: int = Field(0, description="Word count of candidate response")
    response_time_seconds: float = Field(0.0, description="Latency before candidate started speaking")
    follow_up_eligible: bool = Field(False, description="Whether response triggers follow-up probing")
    follow_up_triggered: bool = Field(False, description="Whether follow-up prompt was actually dispatched")
    follow_up_reason: FollowUpTriggerReason = Field(FollowUpTriggerReason.NONE, description="Root cause for follow-up")
    follow_up_depth: int = Field(0, description="Sequential follow-up depth for current parent question")
    ambiguity_score: float = Field(0.0, description="Degree of vagueness or ambiguity detected (0.0=clear, 1.0=very vague)")
    confidence_score: float = Field(0.0, description="Estimated confidence/assertiveness of candidate response (0.0=hesitant, 1.0=authoritative)")
    adaptation_tier: AdaptationTier = Field(AdaptationTier.STANDARD, description="Difficulty adaptation tier assigned to this turn")
    probe_category: FollowUpProbeCategory = Field(FollowUpProbeCategory.NONE, description="Category of follow-up probe if triggered")
    extracted_themes: List[str] = Field(default_factory=list, description="Extracted behavioral keywords & themes")
    communication_score: Optional[CommunicationScoreBreakdown] = Field(None, description="Day 35 objective communication score breakdown")
    confidence_evaluation: Optional[TurnConfidenceBreakdown] = Field(None, description="Day 36 confidence & stress evaluation breakdown")
    phase_completed: bool = Field(False, description="Whether this turn marked the conclusion of a phase")


class HRInterviewConfig(BaseModel):
    """Configuration payload to initiate an adaptive HR interview session."""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    candidate_name: str = Field(..., description="Full legal name of candidate")
    job_role: str = Field(..., description="Target role title (e.g. Junior Backend Developer, Senior Sales Lead)")
    experience_years: float = Field(..., ge=0.0, description="Candidate total years of experience")
    experience_tier: ExperienceTier = Field(..., description="Fresher or Experienced classification")
    role_track: RoleTrack = Field(..., description="Technical or Non-Technical role classification")
    target_skills: List[str] = Field(default_factory=list, description="Key candidate skills or domain areas")
    enable_adaptive_probing: bool = Field(True, description="Whether to trigger follow-up probing on vague answers")

    @classmethod
    def auto_classify(
        cls,
        candidate_id: str,
        candidate_name: str,
        job_role: str,
        experience_years: float,
        target_skills: Optional[List[str]] = None,
    ) -> "HRInterviewConfig":
        """Factory method that automatically infers ExperienceTier and RoleTrack from metadata."""
        tier = ExperienceTier.FRESHER if experience_years < 2.0 else ExperienceTier.EXPERIENCED
        
        # Technical keywords list for heuristic track assignment
        tech_keywords = {
            "developer", "engineer", "software", "devops", "cloud", "data", "qa",
            "frontend", "backend", "fullstack", "architect", "python", "java", "react",
            "infrastructure", "machine learning", "ai", "security", "sysadmin"
        }
        role_lower = job_role.lower()
        skills_lower = [s.lower() for s in (target_skills or [])]
        is_tech = any(k in role_lower for k in tech_keywords) or any(k in s for s in skills_lower for k in tech_keywords)
        track = RoleTrack.TECHNICAL if is_tech else RoleTrack.NON_TECHNICAL

        return cls(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_role=job_role,
            experience_years=experience_years,
            experience_tier=tier,
            role_track=track,
            target_skills=target_skills or [],
        )


class HRInterviewSession(BaseModel):
    """Master state record tracking the entire lifecycle of an HR interview."""
    session_id: str = Field(..., description="Unique session ID (e.g. sess_hr_a1b2c3d4)")
    config: HRInterviewConfig = Field(..., description="Interview configuration parameters")
    current_phase: InterviewPhase = Field(InterviewPhase.INTRODUCTION, description="Active conversation phase")
    current_question_index: int = Field(0, description="Index of question in planned path")
    turns: List[InterviewTurnState] = Field(default_factory=list, description="Chronological turn audit trail")
    is_completed: bool = Field(False, description="Whether interview has reached CLOSING terminal state")
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = Field(None, description="ISO-8601 completion timestamp")
    total_clarifications: int = Field(0, description="Total clarification follow-ups triggered")
    total_deepenings: int = Field(0, description="Total technical deepening follow-ups triggered")
    total_examples_requested: int = Field(0, description="Total STAR example requests triggered")
    total_scenarios_triggered: int = Field(0, description="Total complex scenario challenge follow-ups triggered")
    probes_dispatched_history: List[Dict[str, Any]] = Field(default_factory=list, description="Audit log of all probes dispatched")
    average_communication_score: float = Field(0.0, ge=0.0, le=100.0, description="Session-wide mean communication score")
    overall_fluency: float = Field(0.0, ge=0.0, le=100.0, description="Mean fluency score")
    overall_grammar: float = Field(0.0, ge=0.0, le=100.0, description="Mean grammar score")
    overall_vocabulary: float = Field(0.0, ge=0.0, le=100.0, description="Mean vocabulary score")
    overall_clarity: float = Field(0.0, ge=0.0, le=100.0, description="Mean clarity score")
    overall_structure: float = Field(0.0, ge=0.0, le=100.0, description="Mean structure score")
    total_fillers_detected: int = Field(0, description="Total filler words detected across all turns")
    communication_tier: str = Field("Proficient", description="Proficiency tier (e.g. Exceptional, Proficient, Developing, Needs Training)")
    average_confidence_score: float = Field(0.0, ge=0.0, le=100.0, description="Session-wide mean confidence score")
    overall_confidence_tier: str = Field("Composed", description="Session confidence classification")
    average_stress_index: float = Field(0.0, ge=0.0, le=100.0, description="Session-wide mean stress index")
    overall_stress_level: str = Field("Low", description="Session-wide stress classification")
    total_hesitations_detected: int = Field(0, description="Total hesitation events across all turns")
    total_contradictions_detected: int = Field(0, description="Total contradiction alerts across session")
    dominant_emotional_tone: str = Field("Matter-of-Fact", description="Primary emotional tone across session")
    summary_notes: Dict[str, Any] = Field(default_factory=dict, description="Consolidated behavioral observations")
