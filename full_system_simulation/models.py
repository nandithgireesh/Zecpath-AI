"""
Day 56: Full System Simulation - Data Models & Schemas
=====================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Covers the complete 6-stage end-to-end hiring journey,
AI vs. Human comparative judgment, and inconsistency diagnosis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime
import uuid


class HiringStage(str, Enum):
    RESUME_UPLOAD = "RESUME_UPLOAD"
    ATS_SCORING = "ATS_SCORING"
    SCREENING = "SCREENING"
    HR_INTERVIEW = "HR_INTERVIEW"
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"
    FINAL_DECISION = "FINAL_DECISION"


class StageStatus(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BYPASSED = "BYPASSED"


class DecisionVerdict(str, Enum):
    STRONG_HIRE = "STRONG_HIRE"
    HIRE = "HIRE"
    LEAN_HIRE = "LEAN_HIRE"
    HOLD_REVIEW = "HOLD_REVIEW"
    LEAN_REJECT = "LEAN_REJECT"
    REJECT = "REJECT"


class InconsistencyType(str, Enum):
    RESUME_INFLATION = "RESUME_INFLATION"             # High ATS (90+), Poor Code (<50)
    FLUENCY_DISGUISE = "FLUENCY_DISGUISE"             # High Vocal Confidence, Low Tech Depth
    ACCENT_BIAS_DRIFT = "ACCENT_BIAS_DRIFT"           # AI False Negative due to Speech Telemetry
    PEDIGREE_HALO_BIAS = "PEDIGREE_HALO_BIAS"         # Human False Positive due to Elite College
    FATIGUE_DRIFT = "FATIGUE_DRIFT"                   # Human Harsher in Afternoon Sessions
    NICHE_SKILL_MISMATCH = "NICHE_SKILL_MISMATCH"     # ATS penalizes unlisted synonym


@dataclass
class ResumeArtifact:
    """Stage 1: Resume Upload artifact."""
    candidate_id: str
    full_name: str
    target_role: str
    raw_text: str
    experience_years: float
    education_level: str
    institution: str
    primary_skills: List[str]
    upload_timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


@dataclass
class ATSScoreResult:
    """Stage 2: ATS Scoring result."""
    candidate_id: str
    keyword_match_score: float      # 0.0 - 100.0
    experience_relevance_score: float # 0.0 - 100.0
    format_hygiene_score: float     # 0.0 - 100.0
    composite_ats_score: float      # Weighted composite (0 - 100)
    passed: bool
    status: StageStatus = StageStatus.PASSED
    extracted_keywords: List[str] = field(default_factory=list)
    missing_critical_skills: List[str] = field(default_factory=list)


@dataclass
class ScreeningResult:
    """Stage 3: Initial Screening evaluation."""
    candidate_id: str
    work_authorization_valid: bool
    salary_alignment_valid: bool
    notice_period_days: int
    prerequisite_met: bool
    screening_score: float          # 0.0 - 100.0
    status: StageStatus = StageStatus.PASSED
    flags: List[str] = field(default_factory=list)


@dataclass
class HRInterviewResult:
    """Stage 4: HR Interview multi-modal evaluation."""
    candidate_id: str
    behavioral_score: float         # 0.0 - 100.0
    communication_clarity_score: float # 0.0 - 100.0
    confidence_index: float         # 0.0 - 100.0
    sentiment_stability_score: float # 0.0 - 100.0
    speech_pause_telemetry: float   # WPM / Pause duration index
    composite_hr_score: float       # 0.0 - 100.0
    status: StageStatus = StageStatus.PASSED
    red_flags: List[str] = field(default_factory=list)


@dataclass
class TechnicalInterviewResult:
    """Stage 5: Technical Interview & Machine Evaluation."""
    candidate_id: str
    coding_correctness_score: float # 0.0 - 100.0
    algorithmic_efficiency_score: float # 0.0 - 100.0
    system_design_score: float      # 0.0 - 100.0
    problem_solving_score: float    # 0.0 - 100.0
    composite_technical_score: float # 0.0 - 100.0
    test_cases_passed: int
    total_test_cases: int
    status: StageStatus = StageStatus.PASSED
    execution_time_ms: float = 120.5


@dataclass
class FinalDecisionResult:
    """Stage 6: Final Decision Arbitration."""
    candidate_id: str
    raw_composite_score: float
    variance_smoothed_score: float
    confidence_interval: float
    ai_verdict: DecisionVerdict
    human_verdict: DecisionVerdict
    alignment: bool
    dossier_id: str
    status: StageStatus = StageStatus.PASSED
    divergence_reasons: List[str] = field(default_factory=list)


@dataclass
class ComparativeEvaluation:
    """AI vs. Human Judgment Comparative Record."""
    candidate_id: str
    candidate_name: str
    ai_score: float
    human_score: float
    score_delta: float
    ai_verdict: DecisionVerdict
    human_verdict: DecisionVerdict
    verdict_concordance: bool
    classification_quadrant: str    # "TRUE_POSITIVE", "TRUE_NEGATIVE", "FALSE_POSITIVE", "FALSE_NEGATIVE"
    human_bias_marker: Optional[str] = None
    ai_bias_marker: Optional[str] = None


@dataclass
class InconsistencyRecord:
    """Identified Inconsistency Record between journey stages or AI/Human."""
    inconsistency_id: str
    candidate_id: str
    candidate_name: str
    inconsistency_type: InconsistencyType
    severity: str                   # "CRITICAL", "MODERATE", "LOW"
    detected_stage: HiringStage
    ai_observation: str
    human_observation: str
    root_cause: str
    recommended_remediation: str


@dataclass
class CompleteJourneyDossier:
    """Comprehensive dossier tracking a candidate through all 6 stages."""
    journey_id: str
    candidate_id: str
    candidate_name: str
    target_role: str
    start_time: str
    completion_time: str
    stage_progression: Dict[HiringStage, StageStatus] = field(default_factory=dict)
    resume: Optional[ResumeArtifact] = None
    ats_result: Optional[ATSScoreResult] = None
    screening_result: Optional[ScreeningResult] = None
    hr_result: Optional[HRInterviewResult] = None
    technical_result: Optional[TechnicalInterviewResult] = None
    final_decision: Optional[FinalDecisionResult] = None
    comparative_record: Optional[ComparativeEvaluation] = None
    inconsistencies: List[InconsistencyRecord] = field(default_factory=list)
    journey_passed: bool = False
    total_latency_ms: float = 0.0
