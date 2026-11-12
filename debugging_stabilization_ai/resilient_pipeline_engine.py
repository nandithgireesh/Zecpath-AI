"""
Day 57: Resilient Pipeline Engine - Fix Data Pipeline Issues & Circuit Breaker
=============================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Remediates:
  1. Corrupted Unicode, null bytes, and schema drift in data pipelines.
  2. Circuit Breaker pattern with failure thresholds, recovery timeouts, and half-open probes.
  3. Graceful degradation fallbacks for audio/telemetry streaming failures.
  4. API payload sanitization preventing internal traceback leakage.
"""

import time
import unicodedata
import re
from typing import Dict, List, Optional, Tuple, Any, Callable

from debugging_stabilization_ai.models import (
    CircuitState, PipelineErrorCode, SeverityLevel, DebugIncidentLog
)


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit is OPEN."""
    pass


class ResilientPipelineEngine:
    """
    Guarantees data pipeline resilience, automated Unicode normalization,
    circuit-breaker fault tolerance, and deterministic fallback execution.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 2.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self.circuit_state: CircuitState = CircuitState.CLOSED
        self.incident_logs: List[DebugIncidentLog] = []

    def clean_raw_pipeline_text(self, raw_data: Any) -> str:
        """
        Normalizes corrupted Unicode, removes null bytes, and sanitizes input text.
        """
        if raw_data is None:
            return ""
        
        # Convert non-string to string
        text = str(raw_data)
        
        # Strip null bytes and non-printable control characters
        text = text.replace("\x00", "")
        text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        # NFKC Normalization (standardizes ligatures, accented variants, full-width)
        normalized = unicodedata.normalize("NFKC", text)
        return normalized.strip()

    def record_incident(
        self,
        error_code: PipelineErrorCode,
        severity: SeverityLevel,
        subsystem: str,
        message: str,
        mitigation: str,
        fallback_used: bool,
        candidate_id: Optional[str] = None
    ) -> DebugIncidentLog:
        """Logs an operational incident for auditability and diagnostic tracking."""
        incident = DebugIncidentLog(
            incident_id=f"INC-{int(time.time()*1000)}",
            error_code=error_code,
            severity=severity,
            subsystem=subsystem,
            candidate_id=candidate_id,
            raw_error_message=message,
            mitigation_applied=mitigation,
            fallback_used=fallback_used,
            resolved=True
        )
        self.incident_logs.append(incident)
        return incident

    def execute_with_circuit_breaker(
        self,
        subsystem_name: str,
        primary_callable: Callable[[], Any],
        fallback_callable: Callable[[Exception], Any]
    ) -> Tuple[Any, bool]:
        """
        Executes a primary operation protected by the Circuit Breaker pattern.
        
        Returns:
            Tuple of (result, was_fallback_triggered)
        """
        now = time.time()

        # Check if OPEN circuit should transition to HALF_OPEN
        if self.circuit_state == CircuitState.OPEN:
            if (now - self.last_failure_time) >= self.recovery_timeout_seconds:
                self.circuit_state = CircuitState.HALF_OPEN
            else:
                # Still OPEN: immediately bypass to fallback
                self.record_incident(
                    error_code=PipelineErrorCode.UPSTREAM_SERVICE_TIMEOUT,
                    severity=SeverityLevel.HIGH,
                    subsystem=subsystem_name,
                    message="Circuit is OPEN. Fast-failing to fallback.",
                    mitigation="Diverted to local deterministic fallback.",
                    fallback_used=True
                )
                return fallback_callable(CircuitBreakerOpenException("Circuit is OPEN")), True

        # Attempt execution
        try:
            result = primary_callable()
            # If HALF_OPEN trial succeeded, reset to CLOSED
            if self.circuit_state == CircuitState.HALF_OPEN:
                self.circuit_state = CircuitState.CLOSED
                self.failure_count = 0
            elif self.circuit_state == CircuitState.CLOSED:
                self.failure_count = 0
            return result, False

        except Exception as exc:
            self.failure_count += 1
            self.last_failure_time = now

            if self.failure_count >= self.failure_threshold:
                self.circuit_state = CircuitState.OPEN

            self.record_incident(
                error_code=PipelineErrorCode.TELEMETRY_STREAM_FAILURE,
                severity=SeverityLevel.MEDIUM,
                subsystem=subsystem_name,
                message=str(exc),
                mitigation="Triggered resilient fallback callable.",
                fallback_used=True
            )
            # Execute graceful fallback
            return fallback_callable(exc), True

    def sanitize_api_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Removes internal stack traces, formats error keys, and ensures
        client-safe deterministic JSON outputs.
        """
        safe_copy = {}
        for k, v in payload.items():
            # Never leak stack traces or internal memory references
            if k in ["traceback", "stack_trace", "internal_exc"]:
                continue
            if isinstance(v, str):
                safe_copy[k] = self.clean_raw_pipeline_text(v)
            elif isinstance(v, dict):
                safe_copy[k] = self.sanitize_api_response(v)
            else:
                safe_copy[k] = v
        return safe_copy
