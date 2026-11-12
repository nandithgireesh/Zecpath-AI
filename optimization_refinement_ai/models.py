"""
Day 54: Optimization & Refinement - Domain Models
=================================================
Enterprise schemas for:
- Confusion Matrix Diagnostics (TP, FP, TN, FN, Precision, Recall, F1)
- Error Analysis & False Positive/Negative Root Causes
- Refined Intent Telemetry (Pause Disambiguation & Implicit STAR Detection)
- Dynamic Thresholding & Bayesian Smoothing Telemetry
- Optimization Benchmark Reports and Cryptographic Seals
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

class DecisionClass(str, Enum):
    SELECTED = "SELECTED"
    HOLD_REVIEW = "HOLD_REVIEW"
    REJECTED = "REJECTED"


class PauseType(str, Enum):
    CONCEPTUAL_THINKING = "CONCEPTUAL_THINKING"
    NERVOUS_HESITATION = "NERVOUS_HESITATION"
    NORMAL_CADENCE = "NORMAL_CADENCE"


class ErrorClassification(str, Enum):
    TRUE_POSITIVE = "TRUE_POSITIVE"
    TRUE_NEGATIVE = "TRUE_NEGATIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    FALSE_NEGATIVE = "FALSE_NEGATIVE"


class OptimizationStage(str, Enum):
    BASELINE = "BASELINE"
    THRESHOLD_TUNED = "THRESHOLD_TUNED"
    INTENT_REFINED = "INTENT_REFINED"
    FULLY_OPTIMIZED = "FULLY_OPTIMIZED"


# ==============================================================================
# 2. CONFUSION MATRIX & ERROR ANALYSIS MODELS
# ==============================================================================

class ConfusionMatrixMetrics(BaseModel):
    """Empirical classification diagnostic metrics for decision arbitration."""
    total_samples: int = Field(..., ge=0)
    true_positives: int = Field(..., ge=0)
    true_negatives: int = Field(..., ge=0)
    false_positives: int = Field(..., ge=0)
    false_negatives: int = Field(..., ge=0)
    accuracy: float = Field(..., ge=0.0, le=100.0)
    precision: float = Field(..., ge=0.0, le=100.0)
    recall: float = Field(..., ge=0.0, le=100.0)
    f1_score: float = Field(..., ge=0.0, le=100.0)
    specificity: float = Field(..., ge=0.0, le=100.0)
    false_positive_rate: float = Field(..., ge=0.0, le=100.0)
    false_negative_rate: float = Field(..., ge=0.0, le=100.0)


class ErrorAnalysisCase(BaseModel):
    """Granular error diagnostic tracing why a candidate was misclassified."""
    candidate_id: str = Field(..., description="Unique candidate ID")
    candidate_name: str = Field(..., description="Candidate name")
    target_role: str = Field(..., description="Target role")
    ground_truth: DecisionClass = Field(..., description="Human expert committee verdict")
    predicted_baseline: DecisionClass = Field(..., description="Initial unoptimized AI verdict")
    predicted_optimized: DecisionClass = Field(..., description="Refined Day 54 AI verdict")
    error_category: ErrorClassification = Field(..., description="FP, FN, TP, or TN")
    root_cause_analysis: str = Field(..., description="Detailed diagnosis of baseline misclassification")
    optimization_remedy: str = Field(..., description="Refinement mechanism resolving the error")


# ==============================================================================
# 3. REFINED INTENT TELEMETRY
# ==============================================================================

class IntentRefinementTelemetry(BaseModel):
    """Disambiguates conceptual thinking vs. nervous crutches, and implicit STAR."""
    pause_duration_seconds: float = Field(default=0.0, ge=0.0)
    pause_classification: PauseType = Field(default=PauseType.NORMAL_CADENCE)
    implicit_star_coverage: float = Field(default=80.0, ge=0.0, le=100.0)
    evasive_deflection_probability: float = Field(default=0.05, ge=0.0, le=1.0)
    intent_confidence_score: float = Field(default=90.0, ge=0.0, le=100.0)
    penalty_adjustment_points: float = Field(default=0.0, description="Deduction refunded or added after intent check")


# ==============================================================================
# 4. THRESHOLD OPTIMIZATION & REFINED SCORING SCHEMAS
# ==============================================================================

class ThresholdOptimizationConfig(BaseModel):
    """Dynamic role-aware threshold parameters replacing brittle static cutoffs."""
    role_track: str = Field(..., description="e.g. DISTRIBUTED_SYSTEMS, CORE_ENGINEERING")
    experience_tier: str = Field(..., description="Seniority tier")
    base_selected_threshold: float = Field(default=82.0, ge=70.0, le=95.0)
    base_hold_floor: float = Field(default=65.0, ge=50.0, le=80.0)
    margin_damping_factor: float = Field(default=0.85, ge=0.5, le=1.5)
    variance_tolerance_ceiling: float = Field(default=16.0, ge=8.0, le=25.0)


class RefinedScoringOutput(BaseModel):
    """Optimized candidate decision payload incorporating Bayesian smoothing and intent."""
    candidate_id: str
    candidate_name: str
    target_role: str
    raw_composite_score: float = Field(..., ge=0.0, le=100.0)
    variance_smoothed_score: float = Field(..., ge=0.0, le=100.0)
    cross_round_coherence_index: float = Field(..., ge=0.0, le=100.0)
    dynamic_selected_threshold: float = Field(..., ge=70.0, le=95.0)
    dynamic_hold_floor: float = Field(..., ge=50.0, le=80.0)
    final_decision: DecisionClass
    decision_substatus: str
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    intent_telemetry: IntentRefinementTelemetry
    processing_latency_ms: float = 0.0
    audit_hash: str = ""

    def compute_sha256_audit_seal(self) -> str:
        payload = {
            "candidate_id": self.candidate_id,
            "target_role": self.target_role,
            "raw_score": round(self.raw_composite_score, 2),
            "smoothed_score": round(self.variance_smoothed_score, 2),
            "coherence_index": round(self.cross_round_coherence_index, 2),
            "decision": self.final_decision.value,
            "substatus": self.decision_substatus,
            "confidence": round(self.confidence_score, 2),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def finalize_and_seal(self) -> None:
        self.audit_hash = self.compute_sha256_audit_seal()


# ==============================================================================
# 5. OPTIMIZATION BENCHMARK REPORT DATA (DELIVERABLE 2)
# ==============================================================================

class OptimizationReportData(BaseModel):
    """Comprehensive empirical benchmark report data contrasting baseline vs. optimized."""
    report_id: str
    evaluation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dataset_cohort_size: int = Field(default=100)
    baseline_metrics: ConfusionMatrixMetrics
    optimized_metrics: ConfusionMatrixMetrics
    accuracy_improvement_pct: float
    fp_reduction_pct: float
    fn_reduction_pct: float
    latency_baseline_p99_ms: float
    latency_optimized_p99_ms: float
    speedup_factor: float
    error_cases: List[ErrorAnalysisCase] = Field(default_factory=list)
    audit_hash: str = ""

    def compute_sha256_audit_seal(self) -> str:
        payload = {
            "report_id": self.report_id,
            "cohort_size": self.dataset_cohort_size,
            "baseline_acc": round(self.baseline_metrics.accuracy, 2),
            "optimized_acc": round(self.optimized_metrics.accuracy, 2),
            "speedup": round(self.speedup_factor, 2),
            "error_cases_count": len(self.error_cases),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def finalize_and_seal(self) -> None:
        self.audit_hash = self.compute_sha256_audit_seal()
