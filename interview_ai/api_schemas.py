"""
Zecpath-AI: Interview AI API Schemas & Data Formats
===================================================
Production Pydantic models defining strict API contracts for the HR Interview AI:
- Request / Response validation schemas
- OpenAPI 3.1.0 metadata and payload examples
- Enumerations for session state, decisions, and follow-up routing
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class ConsentStatus(str, Enum):
    EXPLICIT_OPT_IN = "EXPLICIT_OPT_IN"
    CONDITIONAL = "CONDITIONAL"
    OPTED_OUT = "OPTED_OUT"
    REVOKED = "REVOKED"


class FollowUpAction(str, Enum):
    PROBE_DEEPER = "PROBE_DEEPER"
    ADVANCE_TOPIC = "ADVANCE_TOPIC"
    RECOVER_DEADLOCK = "RECOVER_DEADLOCK"
    CONCLUDE_SESSION = "CONCLUDE_SESSION"


class HiringDecision(str, Enum):
    STRONG_HIRE = "STRONG_HIRE"
    LEAN_HIRE = "LEAN_HIRE"
    BORDERLINE = "BORDERLINE"
    NO_HIRE = "NO_HIRE"


class SeniorityLevel(str, Enum):
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    STAFF_PRINCIPAL = "STAFF_PRINCIPAL"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class InterviewSessionInitRequest(BaseModel):
    candidate_id: str = Field(..., description="Unique pseudonymous candidate identifier", example="CAND-43-ADITI")
    role_id: str = Field(..., description="Target job profile identifier", example="DATA_INFRA_ENG")
    target_seniority: SeniorityLevel = Field(default=SeniorityLevel.SENIOR, description="Target job seniority tier")
    explicit_opt_in: bool = Field(..., description="Statutory consent opt-in acknowledgement (NYC LL144 & BIPA)")
    locale: str = Field(default="en-US", description="Language and dialect locale code", example="en-US")


class CandidateTurnRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session UUID", example="sess-8f92a10b-43c1")
    turn_index: int = Field(..., ge=1, le=20, description="Sequential turn index", example=1)
    raw_transcript: str = Field(..., description="Speech-to-text transcript utterance with optional disfluencies",
                                 example="My name is Aditi Rao. As a woman in tech, they told me Stanford grads get priority.")
    speech_latency_seconds: float = Field(..., ge=0.0, le=60.0, description="Speech onset delay in seconds", example=3.8)
    audio_duration_seconds: float = Field(default=12.5, ge=0.0, description="Total speech duration in seconds")


class ScoringEvaluationRequest(BaseModel):
    session_id: str = Field(..., description="Concluded interview session UUID", example="sess-8f92a10b-43c1")
    include_explainability: bool = Field(default=True, description="Whether to include EU AI Act Art. 13/14 transparency dossier")
    apply_deliberation_discount: bool = Field(default=True, description="Whether to apply Cognitive Deliberation Ratio filtering")


class GDPRRetentionPurgeRequest(BaseModel):
    candidate_id: str = Field(..., description="Candidate identifier requesting Right-to-Erasure", example="CAND-43-ADITI")
    statutory_authority: str = Field(default="GDPR Article 17", description="Legal basis for permanent record destruction")
    requestor_token: str = Field(..., description="Cryptographic bearer authorization token")


# ---------------------------------------------------------------------------
# Sub-Schemas & Telemetry
# ---------------------------------------------------------------------------

class RedactionTelemetry(BaseModel):
    total_redactions: int = Field(..., description="Count of demographic tokens masked")
    name_tokens_redacted: int = Field(0, description="Candidate name entities scrubbed")
    gender_pronouns_neutralized: int = Field(0, description="Gender markers neutralized")
    age_grad_proxies_redacted: int = Field(0, description="Age or graduation dates masked")
    institution_proxies_normalized: int = Field(0, description="Prestige institutions normalized")
    geo_dialects_normalized: int = Field(0, description="Regional syntax idioms normalized")


class CompetencyFactorScore(BaseModel):
    factor_name: str = Field(..., description="Competency dimension name")
    weight: float = Field(..., description="Mathematical weight percentage (0.0 - 1.0)")
    raw_score: float = Field(..., description="Raw competency score (0.0 - 100.0)")
    weighted_contribution: float = Field(..., description="Contribution to composite score")


class ItemizedDeduction(BaseModel):
    category: str = Field(..., description="Penalty category (linguistic, behavioral, fallacy)")
    points_deducted: float = Field(..., description="Absolute points deducted")
    rationale: str = Field(..., description="Audit-ready plain English rationale")
    is_bounded: bool = Field(default=True, description="Whether deduction respects anti-double-dipping ceiling")


class ExplainabilityDossier(BaseModel):
    transparency_framework: str = Field("EU AI Act Articles 13 & 14", description="Compliance standard")
    deliberation_credit_applied: bool = Field(..., description="True if hesitation discount was granted")
    credit_points_restored: float = Field(0.0, description="Points restored via Cognitive Deliberation Ratio")
    counterfactual_guidance: str = Field(..., description="Plain-English coaching to achieve next hiring tier")
    human_oversight_notice: str = Field("Final hiring decision remains subject to certified human reviewer.", description="Human oversight statement")


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class InterviewSessionInitResponse(BaseModel):
    session_id: str = Field(..., description="Generated session UUID")
    candidate_pseudonym: str = Field(..., description="Cryptographic pseudonym (e.g. PSEUDO-5C49A2314C)")
    consent_status: ConsentStatus = Field(..., description="Registered statutory consent state")
    consent_receipt_sha256: str = Field(..., description="Immutable SHA-256 consent receipt hash")
    initial_question: str = Field(..., description="First interview question calibrated to role")
    ttl_expiry_utc: str = Field(..., description="Session storage expiration timestamp")


class CandidateTurnResponse(BaseModel):
    session_id: str = Field(..., description="Session UUID")
    turn_index: int = Field(..., description="Current turn index")
    cleaned_transcript: str = Field(..., description="ASR-cleaned transcript without non-words")
    scrubbed_transcript: str = Field(..., description="Demographic-scrubbed transcript for blind scoring")
    redaction_telemetry: RedactionTelemetry = Field(..., description="Summary of demographic tokens scrubbed")
    cognitive_deliberation_ratio: float = Field(..., description="Words per second formulation velocity")
    followup_action: FollowUpAction = Field(..., description="Deterministic state coordinator decision")
    followup_question: Optional[str] = Field(None, description="Entity-grounded follow-up question")
    is_concluded: bool = Field(default=False, description="True if maximum topic depth or turns reached")


class ScoringEvaluationResponse(BaseModel):
    session_id: str = Field(..., description="Session UUID")
    candidate_pseudonym: str = Field(..., description="Pseudonymized candidate ID")
    composite_score: float = Field(..., description="Final calibrated score (0.0 - 100.0)")
    decision: HiringDecision = Field(..., description="Statutory hiring recommendation")
    leveling_recommendation: SeniorityLevel = Field(..., description="Role leveling assignment")
    overqualification_index: float = Field(..., description="Calculated Overqualification Leveling Index")
    factors: List[CompetencyFactorScore] = Field(..., description="4-factor competency breakdown")
    deductions: List[ItemizedDeduction] = Field(..., description="Itemized penalty deductions")
    total_deduction_points: float = Field(..., description="Net bounded deduction sum (max -12.0)")
    explainability: Optional[ExplainabilityDossier] = Field(None, description="EU AI Act compliance dossier")


class GDPRRetentionPurgeResponse(BaseModel):
    candidate_id: str = Field(..., description="Target candidate identifier")
    purged_assets_count: int = Field(..., description="Number of storage assets shredded")
    deletion_certificate_id: str = Field(..., description="Cryptographic certificate ID (DEL-CERT-XXXX)")
    sha256_verification_hash: str = Field(..., description="Verifiable proof of destruction hash")
    timestamp_utc: str = Field(..., description="Deletion execution UTC timestamp")
    status: str = Field("PERMANENTLY_ERASED", description="Purge completion status")


class HealthCheckResponse(BaseModel):
    status: str = Field("HEALTHY", description="Overall platform status")
    version: str = Field("v1.4.3", description="API semantic version")
    subsystems: Dict[str, str] = Field(..., description="Health status of all component subsystems")
    avg_latency_ms: float = Field(..., description="99th percentile end-to-end turn latency")
    statutory_mode: str = Field("NYC_LL144_AND_EU_AI_ACT", description="Active compliance governance mode")


class APIErrorResponse(BaseModel):
    error_code: str = Field(..., description="Standardized error code (e.g. ERR_ZEC_4001)", example="ERR_ZEC_4001")
    message: str = Field(..., description="Human-readable description of error constraint")
    correlation_id: str = Field(..., description="Tracing UUID for distributed telemetry")
    timestamp_utc: str = Field(..., description="UTC timestamp of error occurrence")
    troubleshooting_runbook: str = Field(..., description="Direct reference to developer remediation runbook")
