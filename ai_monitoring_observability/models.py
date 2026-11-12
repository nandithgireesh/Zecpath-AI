"""
Day 61: AI Monitoring & Observability Models
Platform: Zecpath Automated Hiring Platform
"""

import time
import uuid
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(str, Enum):
    API_REQUEST = "API_REQUEST"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    ERROR_EXCEPTION = "ERROR_EXCEPTION"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    AUDIT_TRAIL = "AUDIT_TRAIL"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    P1_EMERGENCY = "P1_EMERGENCY"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SILENCED = "SILENCED"
    RESOLVED = "RESOLVED"


@dataclass
class APILogEntry:
    trace_id: str
    timestamp: float = field(default_factory=time.time)
    method: str = "POST"
    endpoint: str = "/api/v1/interview/turn"
    status_code: int = 200
    latency_ms: float = 1.25
    client_ip: str = "127.0.0.1"
    candidate_id: Optional[str] = None
    payload_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": LogType.API_REQUEST.value,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "method": self.method,
            "endpoint": self.endpoint,
            "status_code": self.status_code,
            "latency_ms": round(self.latency_ms, 3),
            "client_ip": self.client_ip,
            "candidate_id": self.candidate_id,
            "payload_hash": self.payload_hash,
        }


@dataclass
class ModelOutputLogEntry:
    trace_id: str
    timestamp: float = field(default_factory=time.time)
    candidate_id: str = "CAND-001"
    subsystem: str = "tech_scoring"
    input_text_hash: str = ""
    output_tokens: int = 42
    confidence_score: float = 0.94
    predicted_grade: str = "STRONG_HIRE"
    inference_latency_ms: float = 0.08
    explainability_factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": LogType.MODEL_INFERENCE.value,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "candidate_id": self.candidate_id,
            "subsystem": self.subsystem,
            "input_text_hash": self.input_text_hash,
            "output_tokens": self.output_tokens,
            "confidence_score": round(self.confidence_score, 4),
            "predicted_grade": self.predicted_grade,
            "inference_latency_ms": round(self.inference_latency_ms, 3),
            "explainability_factors": self.explainability_factors,
        }


@dataclass
class ErrorLogEntry:
    trace_id: str
    timestamp: float = field(default_factory=time.time)
    error_type: str = "InferenceTimeoutError"
    message: str = "Execution exceeded safety bound"
    stack_trace: str = ""
    subsystem: str = "scoring_engine"
    severity: LogLevel = LogLevel.ERROR
    recoverable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": LogType.ERROR_EXCEPTION.value,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "message": self.message,
            "subsystem": self.subsystem,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "stack_trace": self.stack_trace,
        }


@dataclass
class MetricSnapshot:
    timestamp: float = field(default_factory=time.time)
    sample_window_sec: float = 60.0
    total_requests: int = 0
    throughput_rps: float = 0.0
    p50_latency_ms: float = 0.0
    p90_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    model_accuracy_pct: float = 98.5
    active_interviews: int = 0


@dataclass
class AlertRule:
    rule_id: str
    name: str
    metric_name: str  # "p99_latency_ms", "error_rate_pct", "model_accuracy_pct"
    comparison_operator: str  # ">", ">=", "<", "<="
    threshold_value: float
    severity: AlertSeverity = AlertSeverity.WARNING
    window_sec: float = 60.0
    cooldown_sec: float = 120.0
    last_triggered_at: float = 0.0


@dataclass
class AlertIncident:
    incident_id: str = field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    rule_id: str = ""
    rule_name: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    metric_value: float = 0.0
    threshold_value: float = 0.0
    triggered_at: float = field(default_factory=time.time)
    status: AlertStatus = AlertStatus.ACTIVE
    resolved_at: Optional[float] = None


@dataclass
class DecisionAuditRecord:
    audit_id: str = field(default_factory=lambda: f"AUDIT-{uuid.uuid4().hex[:12].upper()}")
    candidate_id: str = "CAND-001"
    target_role: str = "Senior Backend Architect"
    timestamp: float = field(default_factory=time.time)
    final_verdict: str = "STRONG_HIRE"
    overall_score: float = 91.5
    round_scores: Dict[str, float] = field(default_factory=dict)
    adverse_impact_ratio: float = 0.94  # EEOC 4/5ths Rule Verification
    eu_ai_act_risk_class: str = "Annex III High-Risk Employment AI"
    previous_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
    current_hash: str = ""

    def calculate_hash(self) -> str:
        payload = {
            "audit_id": self.audit_id,
            "candidate_id": self.candidate_id,
            "target_role": self.target_role,
            "timestamp": self.timestamp,
            "final_verdict": self.final_verdict,
            "overall_score": self.overall_score,
            "round_scores": self.round_scores,
            "adverse_impact_ratio": self.adverse_impact_ratio,
            "previous_hash": self.previous_hash,
        }
        raw_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


@dataclass
class DashboardMetrics:
    total_candidates_processed: int = 0
    active_interviews: int = 0
    completed_interviews: int = 0
    interview_success_rate_pct: float = 0.0
    offer_recommendation_rate_pct: float = 0.0
    average_interview_duration_min: float = 0.0
    system_throughput_rps: float = 0.0
    p95_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    system_health: str = "OPTIMAL"
    last_updated: float = field(default_factory=time.time)

