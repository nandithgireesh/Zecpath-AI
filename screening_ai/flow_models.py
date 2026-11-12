"""
Day 29: AI Conversation Flow Models
===================================
Defines Enums and Pydantic schemas for the AI Call Flow Decision Tree,
Conversation State Machine, Disruption Handling, and Session Contexts.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CallPhase(str, Enum):
    """Phases of an end-to-end recruitment screening call."""
    GREETING_CONSENT = "GREETING_CONSENT"
    PROFILE_CONFIRMATION = "PROFILE_CONFIRMATION"
    CORE_TECHNICAL = "CORE_TECHNICAL"
    OPERATIONAL_CONSTRAINTS = "OPERATIONAL_CONSTRAINTS"
    CANDIDATE_QNA = "CANDIDATE_QNA"
    CLOSING_WRAPUP = "CLOSING_WRAPUP"


class ConversationState(str, Enum):
    """Formal states of the AI screening conversation state machine."""
    INITIALIZING = "INITIALIZING"
    GREETING = "GREETING"
    AWAITING_INPUT = "AWAITING_INPUT"
    PROCESSING_INPUT = "PROCESSING_INPUT"
    FOLLOW_UP_PROBING = "FOLLOW_UP_PROBING"
    REPHRASING_FALLBACK = "REPHRASING_FALLBACK"
    HANDLING_SILENCE = "HANDLING_SILENCE"
    HANDLING_CONFUSION = "HANDLING_CONFUSION"
    HANDLING_REPETITION = "HANDLING_REPETITION"
    TRANSITIONING_NEXT = "TRANSITIONING_NEXT"
    WRAPUP = "WRAPUP"
    COMPLETED = "COMPLETED"
    CALL_TERMINATED = "CALL_TERMINATED"


class DisruptionType(str, Enum):
    """Types of conversational interruptions or behavioral edge-cases."""
    NONE = "NONE"
    SILENCE_TIMEOUT = "SILENCE_TIMEOUT"
    CANDIDATE_CONFUSION = "CANDIDATE_CONFUSION"
    REPEATED_ANSWER = "REPEATED_ANSWER"
    AUDIO_INCOMPREHENSIBLE = "AUDIO_INCOMPREHENSIBLE"
    OFF_TOPIC = "OFF_TOPIC"
    TECHNICAL_GLITCH = "TECHNICAL_GLITCH"


class ActionType(str, Enum):
    """Actions the AI conversational agent can execute."""
    SPEAK_PRIMARY = "SPEAK_PRIMARY"
    SPEAK_PROBE = "SPEAK_PROBE"
    SPEAK_FALLBACK = "SPEAK_FALLBACK"
    NUDGE_SILENCE = "NUDGE_SILENCE"
    CLARIFY_CONFUSION = "CLARIFY_CONFUSION"
    ACKNOWLEDGE_REPETITION = "ACKNOWLEDGE_REPETITION"
    ANSWER_CANDIDATE_QUERY = "ANSWER_CANDIDATE_QUERY"
    SKIP_AND_TRANSITION = "SKIP_AND_TRANSITION"
    WRAPUP_CALL = "WRAPUP_CALL"
    TERMINATE_CALL = "TERMINATE_CALL"


class NudgeLevel(str, Enum):
    """Progressive severity tiers for silence nudging."""
    GENTLE_CHECK = "GENTLE_CHECK"         # 5 - 9 seconds
    ASSIST_REPHRASE = "ASSIST_REPHRASE"   # 10 - 19 seconds
    TIMEOUT_TRANSITION = "TIMEOUT_TRANSITION"  # >= 20 seconds


class RetryPolicyAction(str, Enum):
    """Circuit breaker action when candidate struggles repeatedly."""
    RETRY_PRIMARY = "RETRY_PRIMARY"
    TRY_FALLBACK = "TRY_FALLBACK"
    SKIP_QUESTION = "SKIP_QUESTION"
    ABORT_CALL = "ABORT_CALL"


class FallbackQuestion(BaseModel):
    """Structured question record with multiple fallback formulations."""
    primary_id: str = Field(..., description="Unique question identifier")
    category: str = Field(..., description="Competency or topic category")
    primary_text: str = Field(..., description="Standard high-level technical question")
    simplified_text: str = Field(..., description="Simpler, low-jargon alternative question")
    paraphrase_text: str = Field(..., description="Direct rephrasing for audio clarity requests")
    applied_scenario: str = Field(..., description="Concrete applied project scenario question")
    hint_keywords: List[str] = Field(default_factory=list, description="Key concepts or hints")


class SilenceEvent(BaseModel):
    """Details of a detected conversational pause or silence."""
    silence_duration_ms: int = Field(..., description="Silence duration in milliseconds")
    nudge_level: NudgeLevel = Field(..., description="Severity tier of silence nudge")
    consecutive_silence_count: int = Field(default=1, description="Number of consecutive silences")
    is_timeout: bool = Field(default=False, description="Whether silence exceeds max limit")
    nudge_prompt: str = Field(..., description="Natural language spoken prompt to re-engage candidate")


class ConfusionEvent(BaseModel):
    """Details when a candidate expresses confusion or asks for clarification."""
    trigger_phrase: str = Field(..., description="Exact cue uttered by candidate indicating confusion")
    confusion_level: str = Field(default="MODERATE", description="Severity of confusion (MILD, MODERATE, SEVERE)")
    suggested_clarification: str = Field(..., description="Empathic acknowledgment and rephrased question")
    fallback_question_used: Optional[str] = None


class RepetitionEvent(BaseModel):
    """Details when a candidate repeats a previously stated answer or loops."""
    previous_turn_index: int = Field(..., description="Index of turn that this response repeats")
    similarity_score: float = Field(..., description="Cosine / Jaccard similarity score (0.0 - 1.0)")
    repeated_snippet: str = Field(..., description="Key overlapping phrases detected")
    pivot_prompt: str = Field(..., description="Polite pivot prompt advancing to progressive probe")


class FollowUpTriggerRule(BaseModel):
    """Rule determining when an adaptive technical follow-up probe is fired."""
    trigger_id: str
    condition_name: str
    description: str
    probe_template: str


class CallFlowAction(BaseModel):
    """Structured action instruction emitted by the AI Call Flow Decision Tree."""
    action_id: str = Field(..., description="Unique action identifier")
    action_type: ActionType = Field(..., description="Type of action to execute")
    text_to_speak: str = Field(..., description="Natural language text synthesized via TTS to candidate")
    next_state: ConversationState = Field(..., description="Target state after action completes")
    current_phase: CallPhase = Field(..., description="Active screening phase")
    question_id: Optional[str] = Field(None, description="Active question ID, if applicable")
    should_listen: bool = Field(default=True, description="Whether agent should open microphone for candidate")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Operational flags, audio hints, latency metrics")


class ConversationTurn(BaseModel):
    """A single conversational dialogue turn."""
    turn_id: int
    speaker: str = Field(..., description="'AI' or 'CANDIDATE'")
    text: str
    state_before: ConversationState
    state_after: ConversationState
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    disruption_type: DisruptionType = DisruptionType.NONE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CallSessionState(BaseModel):
    """Full operational state of an active screening conversation."""
    session_id: str
    candidate_id: str
    candidate_name: str
    role_name: str
    current_phase: CallPhase = CallPhase.GREETING_CONSENT
    current_state: ConversationState = ConversationState.INITIALIZING
    current_question_index: int = 0
    question_ids: List[str] = Field(default_factory=list)
    question_retries: Dict[str, int] = Field(default_factory=dict)
    consecutive_failures: int = 0
    total_silence_count: int = 0
    total_confusion_count: int = 0
    total_repetition_count: int = 0
    turn_history: List[ConversationTurn] = Field(default_factory=list)
    is_active: bool = True
    is_completed: bool = False
    termination_reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CallSessionSummary(BaseModel):
    """Recruiter-ready summary of conversation execution and flow quality."""
    session_id: str
    candidate_name: str
    role_name: str
    total_turns: int
    completion_status: str
    total_disruptions_handled: int
    silence_events_count: int
    confusion_events_count: int
    repetition_events_count: int
    phases_completed: List[CallPhase]
    final_state: ConversationState
    termination_reason: Optional[str] = None
