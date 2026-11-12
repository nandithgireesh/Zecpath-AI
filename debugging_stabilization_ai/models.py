"""
Day 57: Debugging & Stabilization - Data Models & Schemas
=========================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Covers error classification, circuit breaker states, stabilization patches,
debug incident records, edge case results, and system reliability metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime
import uuid


class PipelineErrorCode(str, Enum):
    SCORING_OUTLIER_ANOMALY = "SCORING_OUTLIER_ANOMALY"
    SCORING_DIVIDE_BY_ZERO = "SCORING_DIVIDE_BY_ZERO"
    CONVERSATION_LOOP_STALL = "CONVERSATION_LOOP_STALL"
    CONVERSATION_SILENCE_TIMEOUT = "CONVERSATION_SILENCE_TIMEOUT"
    CONVERSATION_TOPIC_DRIFT = "CONVERSATION_TOPIC_DRIFT"
    DATA_CORRUPTED_UNICODE = "DATA_CORRUPTED_UNICODE"
    DATA_SCHEMA_VALIDATION_ERROR = "DATA_SCHEMA_VALIDATION_ERROR"
    UPSTREAM_SERVICE_TIMEOUT = "UPSTREAM_SERVICE_TIMEOUT"
    TELEMETRY_STREAM_FAILURE = "TELEMETRY_STREAM_FAILURE"


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class CircuitState(str, Enum):
    CLOSED = "CLOSED"         # Normal operation, traffic flows
    OPEN = "OPEN"             # Tripped due to failures, traffic diverted to fallback
    HALF_OPEN = "HALF_OPEN"   # Testing recovery with trial traffic


@dataclass
class StabilizationPatch:
    """Documenting a formal engineering bugfix/stabilization patch."""
    patch_id: str
    target_subsystem: str      # "SCORING_ENGINE", "CONVERSATION_FLOW", "DATA_PIPELINE", "API_GATEWAY"
    issue_description: str
    root_cause: str
    remediation_strategy: str
    verification_status: str   # "VERIFIED", "DEPLOYED", "TESTED"
    introduced_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


@dataclass
class DebugIncidentLog:
    """Tamper-evident incident log entry for operational failures."""
    incident_id: str
    error_code: PipelineErrorCode
    severity: SeverityLevel
    subsystem: str
    candidate_id: Optional[str]
    raw_error_message: str
    mitigation_applied: str
    fallback_used: bool
    resolved: bool
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


@dataclass
class EdgeCaseValidationResult:
    """Record verifying platform robustness against an extreme edge case."""
    test_case_id: str
    edge_case_name: str
    input_payload_summary: str
    expected_behavior: str
    actual_behavior: str
    unhandled_exception: bool
    graceful_fallback_triggered: bool
    passed: bool
    execution_time_ms: float


@dataclass
class SystemStabilityMetrics:
    """Aggregated reliability, MTBF, error rate, and SLA telemetry."""
    total_transactions_tested: int
    unhandled_crashes: int
    handled_fallbacks: int
    error_rate_percentage: float
    circuit_breaker_trips: int
    p99_latency_ms: float
    mtbf_hours: float          # Mean Time Between Failures
    mttr_seconds: float        # Mean Time To Recover
    availability_sla_percentage: float
