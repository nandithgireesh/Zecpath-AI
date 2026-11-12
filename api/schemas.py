from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    skills: List[str] = Field(default_factory=list)
    experience: str = ""
    education: str = ""
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    role: str = "Unknown Role"
    skills: List[str] = Field(default_factory=list)
    experience: str = ""
    education: str = ""
    projects: List[str] = Field(default_factory=list)


class ATSScoreRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescription


class Candidate(BaseModel):
    resume_id: str
    resume: ResumeData


class RankingRequest(BaseModel):
    candidates: List[Candidate]
    job_description: JobDescription


class ATSScoreResponse(BaseModel):
    ats_score: float
    level: str
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float


class RankedCandidate(BaseModel):
    rank: int
    resume_id: str
    ats_score: float
    level: str
    status: str


class RankingResponse(BaseModel):
    role: str
    candidates: List[RankedCandidate]


class ShortlistResponse(BaseModel):
    role: str
    shortlisted: List[RankedCandidate]
    review: List[RankedCandidate]
    rejected: List[RankedCandidate]


class ATSJobRequest(BaseModel):
    resume_id: str
    job_description: Dict[str, Any]


# =========================================================
# Day 21 - Screening AI Eligibility Schemas
# =========================================================

class EligibilityRuleSchema(BaseModel):
    role_name: str = "General Role"
    min_ats_score: float = 70.0
    review_ats_score: float = 55.0
    mandatory_skills: List[str] = Field(default_factory=list)
    min_experience_years: float = 0.0
    max_experience_years: Optional[float] = None
    allowed_locations: List[str] = Field(default_factory=list)
    max_notice_period_days: Optional[int] = None
    allow_remote: bool = True
    required_education_keywords: List[str] = Field(default_factory=list)


class CandidateEligibilityRequest(BaseModel):
    candidate_id: Optional[str] = None
    resume_id: Optional[str] = None
    name: Optional[str] = None
    ats_score: float
    skills: List[str] = Field(default_factory=list)
    total_experience: Optional[Any] = 0.0
    location: Optional[str] = ""
    notice_period_days: Optional[int] = None
    rules: Optional[EligibilityRuleSchema] = None
    role_name: Optional[str] = None


class BatchEligibilityRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    rules: Optional[EligibilityRuleSchema] = None
    role_name: Optional[str] = None


# =========================================================
# Day 22 - Screening Question Bank & Call Script Schemas
# =========================================================

class QuestionRenderRequest(BaseModel):
    question_id: str
    context: Dict[str, Any] = Field(default_factory=dict)
    language: str = "en"


class CallScriptRequest(BaseModel):
    candidate_data: Dict[str, Any]
    role_name: str = "Machine Learning Engineer"
    job_location: str = "Bangalore"
    language: str = "en"
    bot_name: str = "Zecpath AI Recruiter"


# =========================================================
# Day 23 - Voice Transcript Data Architecture Schemas
# =========================================================

class TranscriptNormalizeRequest(BaseModel):
    raw_text: str
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


class TranscriptNormalizeResponse(BaseModel):
    raw_text: str
    cleaned_text: str
    removed_fillers: List[str] = Field(default_factory=list)
    normalized_entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    confidence_level: str
    is_low_confidence: bool


class TranscriptIngestResponse(BaseModel):
    session_id: str
    call_id: str
    candidate_id: str
    job_id: str
    status: str
    total_turns: int
    total_question_interactions: int
    file_storage_path: str
    db_persisted: bool
    normalized_data: Dict[str, Any] = Field(default_factory=dict)


class MetadataStandardsResponse(BaseModel):
    standard_name: str
    version: str
    metadata_fields: Dict[str, Any]
    normalization_rules: List[str]
    confidence_thresholds: Dict[str, Any]
    database_tables: List[str]


# =========================================================
# Day 24 - Speech-to-Text Integration & Cleaning Schemas
# =========================================================

class STTCleanRequest(BaseModel):
    raw_text: str
    question_category: Optional[str] = None
    question_text: Optional[str] = None
    silence_duration_seconds: float = 0.0


class STTCleanResponse(BaseModel):
    original_text: str
    cleaned_text: str
    removed_fillers: List[str] = Field(default_factory=list)
    punctuation_corrected: bool = False
    proper_case_applied: bool = False
    edge_case_analysis: Dict[str, Any] = Field(default_factory=dict)


class STTTranscribeRequest(BaseModel):
    text_payload: Optional[str] = None
    audio_file_path: Optional[str] = None
    accent: str = "INDIAN_ENGLISH"
    noise_condition: str = "CLEAN_STUDIO"
    silence_duration_seconds: float = 0.0
    question_category: Optional[str] = None


class STTTranscribeResponse(BaseModel):
    raw_transcript: str
    cleaned_transcript: str
    confidence: float
    word_confidences: List[Dict[str, Any]] = Field(default_factory=list)
    detected_accent: str
    audio_metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float
    edge_case: str
    recovery_prompt: Optional[str] = None


class STTBenchmarkReportResponse(BaseModel):
    total_tests: int
    overall_wer: float
    overall_cer: float
    mean_confidence: float
    mean_latency_ms: float
    accent_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    noise_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    generated_at: str
    status: str


# =========================================================
# Day 25 - Answer Intent & Understanding Schemas
# =========================================================

class IntentClassifyRequest(BaseModel):
    text: str
    question_category: Optional[str] = None
    question_prompt: Optional[str] = None


class IntentClassifyResponse(BaseModel):
    text: str
    primary_intent: str
    confidence: float
    secondary_intents: List[str] = Field(default_factory=list)


class AnswerUnderstandRequest(BaseModel):
    raw_text: str
    question_category: Optional[str] = None
    question_prompt: Optional[str] = None
    turn_id: Optional[str] = None
    question_id: Optional[str] = None


class AnswerUnderstandResponse(BaseModel):
    turn_id: Optional[str] = None
    question_id: Optional[str] = None
    question_category: Optional[str] = None
    raw_text: str
    cleaned_text: str
    primary_intent: str
    intent_confidence: float
    secondary_intents: List[str] = Field(default_factory=list)
    extracted_skills: List[Dict[str, Any]] = Field(default_factory=list)
    experience: Optional[Dict[str, Any]] = None
    availability: Optional[Dict[str, Any]] = None
    salary: Optional[Dict[str, Any]] = None
    quality: Dict[str, Any] = Field(default_factory=dict)
    follow_up_recommendation: Optional[str] = None


class DialogueBatchUnderstandRequest(BaseModel):
    turns: List[AnswerUnderstandRequest]


class DialogueBatchUnderstandResponse(BaseModel):
    total_turns_analyzed: int
    dominant_intents: List[str] = Field(default_factory=list)
    aggregated_skills: List[str] = Field(default_factory=list)
    overall_clarity_score: float
    structured_answers: List[Dict[str, Any]] = Field(default_factory=list)


# =========================================================
# Day 26 - Screening Scoring Engine Schemas
# =========================================================

class ScoreQuestionRequest(BaseModel):
    raw_text: str
    question_category: Optional[str] = None
    question_text: Optional[str] = None
    question_id: Optional[str] = None


class ScoreQuestionResponse(BaseModel):
    question_id: Optional[str] = None
    question_category: Optional[str] = None
    raw_answer: str
    cleaned_answer: str
    clarity_score: float
    relevance_score: float
    completeness_score: float
    consistency_score: float
    weighted_question_score: float
    grade: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    penalties: List[str] = Field(default_factory=list)
    explanation: str
    dimension_scores: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ScoreSessionRequest(BaseModel):
    candidate_id: Optional[str] = None
    call_id: Optional[str] = None
    job_id: Optional[str] = None
    turns: List[ScoreQuestionRequest]


class ScoreSessionResponse(BaseModel):
    candidate_id: Optional[str] = None
    call_id: Optional[str] = None
    job_id: Optional[str] = None
    overall_score: float
    normalized_score: float
    recommendation_tier: str
    grade: str
    dimension_averages: Dict[str, float] = Field(default_factory=dict)
    category_breakdowns: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    per_question_breakdowns: List[ScoreQuestionResponse] = Field(default_factory=list)
    explainability: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: str


class ScoringWeightsConfigResponse(BaseModel):
    dimension_weights: Dict[str, float]
    category_weights: Dict[str, float]
    grade_thresholds: Dict[str, str]
    recommendation_thresholds: Dict[str, str]


# =========================================================
# Day 27 - Confidence & Sentiment Signal Analysis Schemas
# =========================================================

class BehavioralTurnRequest(BaseModel):
    turn_id: Optional[str] = "TURN_01"
    raw_text: str
    duration_seconds: Optional[float] = None
    latency_ms: Optional[int] = None
    stt_acoustic_confidence: Optional[float] = None
    word_confidences: Optional[List[Dict[str, Any]]] = None


class BehavioralTurnResponse(BaseModel):
    turn_id: str
    raw_text: str
    confidence_score: float
    confidence_tier: str
    pace_wpm: float
    pace_rating: str
    hesitation_penalties: float
    hesitation_incidents: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainty_score: float
    hedging_phrases: List[str] = Field(default_factory=list)
    sentiment_polarity: str
    compound_sentiment: float
    engagement_level: str
    emotional_tone: str
    communication_indicators: Dict[str, Any] = Field(default_factory=dict)
    observations: List[str] = Field(default_factory=list)


class BehavioralSessionRequest(BaseModel):
    candidate_id: Optional[str] = "CANDIDATE_01"
    session_id: Optional[str] = "CALL_SESSION_01"
    turns: List[BehavioralTurnRequest]


class BehavioralSessionResponse(BaseModel):
    candidate_id: str
    session_id: str
    total_turns_analyzed: int
    overall_confidence_score: float
    overall_sentiment: str
    average_compound_sentiment: float
    average_wpm: float
    overall_pace_rating: str
    communication_indicators: Dict[str, Any] = Field(default_factory=dict)
    behavioral_green_flags: List[str] = Field(default_factory=list)
    behavioral_red_flags: List[str] = Field(default_factory=list)
    recruiter_executive_summary: str
    recommended_interviewer_probes: List[str] = Field(default_factory=list)
    turn_breakdowns: List[BehavioralTurnResponse] = Field(default_factory=list)


class BehavioralBenchmarksResponse(BaseModel):
    pace_benchmarks: Dict[str, str]
    confidence_tiers: Dict[str, str]
    sentiment_categories: Dict[str, str]
    communication_indicators: Dict[str, str]


# =========================================================
# Day 28 - AI Screening Report Generator Schemas
# =========================================================

class GenerateReportRequest(BaseModel):
    candidate_id: str = "CAND-01"
    candidate_name: str = "Jane Doe"
    job_id: str = "JOB-01"
    role_name: str = "Software Engineer"
    candidate_data: Dict[str, Any] = Field(default_factory=dict)
    question_evaluations: List[Dict[str, Any]] = Field(default_factory=list)
    role_mandatory_skills: List[str] = Field(default_factory=list)
    role_bonus_skills: List[str] = Field(default_factory=list)
    budget_max_lpa: Optional[float] = None
    budget_min_lpa: Optional[float] = None
    max_acceptable_notice_days: Optional[int] = None
    behavioral_summary: Optional[Dict[str, Any]] = None
    recommended_interviewer_probes: Optional[List[str]] = None


class GenerateReportResponse(BaseModel):
    report_id: str
    candidate_name: str
    role_name: str
    recommendation: str
    recommendation_badge: str
    overall_score: float
    overall_grade: str
    executive_summary: str
    report: Dict[str, Any]
    markdown_export: str
    html_export: str


class ExportReportRequest(BaseModel):
    report: Dict[str, Any]
    export_format: str = "MARKDOWN"  # "MARKDOWN", "HTML", "JSON"


class ExportReportResponse(BaseModel):
    report_id: str
    export_format: str
    content: str


class SampleReportsResponse(BaseModel):
    total_samples: int
    samples: Dict[str, Any]


# =========================================================
# Day 29 - AI Conversation Flow Schemas
# =========================================================

class FlowStartRequest(BaseModel):
    candidate_id: str = "cand_test_01"
    candidate_name: str = "Priya Nair"
    role_name: str = "Lead Platform & DevOps Engineer"
    question_ids: Optional[List[str]] = None


class FlowStartResponse(BaseModel):
    session_id: str
    candidate_name: str
    current_state: str
    current_phase: str
    action: Dict[str, Any]


class FlowStepRequest(BaseModel):
    session_id: str
    candidate_utterance: Optional[str] = None
    silence_ms: int = 0


class FlowStepResponse(BaseModel):
    session_id: str
    current_state: str
    current_phase: str
    current_question_index: int
    action: Dict[str, Any]
    is_completed: bool


class FlowEventRequest(BaseModel):
    session_id: str
    disruption_type: str  # "SILENCE_TIMEOUT", "CANDIDATE_CONFUSION", "REPEATED_ANSWER", "TECHNICAL_GLITCH"
    payload: Dict[str, Any] = Field(default_factory=dict)


class FlowEventResponse(BaseModel):
    session_id: str
    disruption_type: str
    action: Dict[str, Any]
    current_state: str


class FlowStateResponse(BaseModel):
    session_id: str
    session: Dict[str, Any]
    summary: Dict[str, Any]


# =========================================================
# Day 30 - System Testing & Optimization Schemas
# =========================================================

class SimulateCallRequest(BaseModel):
    candidate_id: str = "cand_expert_terse"
    use_optimized_thresholds: bool = True


class SimulateCallResponse(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    target_role: str
    archetype: str
    total_turns: int
    ai_overall_score: float
    ai_technical_score: float
    ai_communication_score: float
    ai_recommendation: str
    human_recommendation: str
    recommendation_matches: bool
    is_false_rejection: bool
    is_false_acceptance: bool
    summary_notes: str


class BenchmarkEvaluateRequest(BaseModel):
    use_optimized_thresholds: bool = True


class BenchmarkEvaluateResponse(BaseModel):
    report_id: str
    generated_at: str
    baseline_metrics: Dict[str, Any]
    optimized_metrics: Dict[str, Any]
    false_rejection_reduction_pct: float
    resolved_candidates: List[str]
    benchmark_profiles_evaluated: int
    key_takeaways: List[str]


class TuneThresholdsRequest(BaseModel):
    overall_hire_cutoff: float = 70.0
    strong_hire_cutoff: float = 84.0
    technical_hire_cutoff: float = 68.0
    communication_hire_cutoff: float = 60.0
    enable_tech_compensation: bool = True
    brevity_protection: bool = True
    hesitation_penalty_dampener: bool = True


class TuneThresholdsResponse(BaseModel):
    status: str
    applied_thresholds: Dict[str, Any]
    resulting_f1_score: float
    resulting_frr: float


class OptimizationMetricsResponse(BaseModel):
    total_profiles: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_rejection_rate: float
    false_acceptance_rate: float
    cohens_kappa: float


# =========================================================
# Day 31 - Edge Case & Failure Handling Schemas
# =========================================================

class AudioAnalysisRequest(BaseModel):
    snr_db: float = 26.0
    peak_amplitude_dbfs: float = -12.0
    packet_loss_rate: float = 0.0
    clipping_events: int = 0
    codec_bitrate_kbps: float = 64.0
    noise_hints: Dict[str, Any] = Field(default_factory=dict)


class AudioAnalysisResponse(BaseModel):
    snr_db: float
    estimated_noise_type: str
    estimated_audio_degradation: str
    acoustic_confidence_discount: float
    needs_acoustic_retry: bool
    recommended_action: Optional[str] = None
    retry_prompt: Optional[str] = None


class LanguageNormalizeRequest(BaseModel):
    text: str


class LanguageNormalizeResponse(BaseModel):
    original_text: str
    detected_category: str
    detected_languages: List[str]
    normalized_text: str
    extracted_entities: Dict[str, Any]
    confidence: float


class EvaluateTurnEdgeCaseRequest(BaseModel):
    session_id: str = "session_day31_001"
    candidate_id: str = "cand_day31_edge"
    turn_id: int = 1
    utterance: str
    question_id: str = "q_tech_stack"
    topic: str = "backend technologies"
    next_topic: str = "database architectures"
    snr_db: float = 26.0
    peak_amplitude_dbfs: float = -12.0
    packet_loss_rate: float = 0.0
    clipping_events: int = 0
    noise_hints: Dict[str, Any] = Field(default_factory=dict)


class EvaluateTurnEdgeCaseResponse(BaseModel):
    session_id: str
    turn_id: int
    original_text: str
    normalized_text: str
    audio_telemetry: Dict[str, Any]
    code_switch_category: str
    extracted_entities: Dict[str, Any]
    is_safe_to_advance: bool
    safety_tier: str
    system_response: str
    audit_flags: List[str]


class EdgeCaseBenchmarkRunResponse(BaseModel):
    total_scenarios: int
    scenarios_evaluated: int
    audio_recoveries_handled: int
    code_switches_normalized: int
    missing_answers_recovered: int
    noise_adaptations_handled: int
    overall_resilience_rate: float
    scenario_results: List[Dict[str, Any]]


# =========================================================
# Day 32 - Production Screening System Finalization Schemas
# =========================================================

class ProductionStartSessionRequest(BaseModel):
    candidate_id: str = "cand_prod_001"
    candidate_name: str = "Vikram Aditya"
    job_role: str = "Senior Backend Architect"
    target_experience_years: float = 5.0
    max_budget_lpa: float = 35.0
    max_notice_days: int = 60
    required_skills: List[str] = Field(
        default_factory=lambda: ["Python", "FastAPI", "PostgreSQL", "Docker", "Microservices"]
    )
    apply_threshold_optimization: bool = True
    enable_acoustic_fairness_buffer: bool = True
    enable_hinglish_normalization: bool = True


class ProductionStartSessionResponse(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    job_role: str
    status: str
    current_state: str
    initial_ai_prompt: str
    created_at: str


class ProductionTurnRequest(BaseModel):
    session_id: str
    turn_index: int = 1
    candidate_speech: str
    snr_db: float = 24.0
    amplitude_dbfs: float = -16.0
    packet_loss_rate: float = 0.0
    clipping_events: int = 0
    response_time_seconds: float = 2.0


class ProductionTurnResponse(BaseModel):
    session_id: str
    turn_index: int
    current_state: str
    ai_spoken_prompt: str
    detected_intent: Optional[str] = None
    normalized_speech: Optional[str] = None
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    acoustic_discount: float = 0.0
    safety_tier: str = "NORMAL_FLOW"
    is_terminal: bool = False


class ProductionFinalizeRequest(BaseModel):
    session_id: str


class ProductionFinalizeResponse(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    job_role: str
    completed_at: str
    eligibility_verified: bool
    final_score: float
    decision: str
    score_breakdown: Dict[str, float]
    technologies_verified: List[str]
    brevity_protection_applied: bool
    false_rejection_risk: str = "0.0%"


class ProductionHealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_status: str
    subsystems: List[Dict[str, Any]]
    active_sessions_count: int


class ProductionManifestResponse(BaseModel):
    track_title: str
    completion_date: str
    author: str
    organization: str
    repository: str
    total_curriculum_days: int
    modules_inventory: List[Dict[str, Any]]
    metrics_summary: Dict[str, Any]
    api_endpoints_count: int
    test_suites_count: int






