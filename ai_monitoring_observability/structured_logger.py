"""
Day 61: Structured Logging System
Captures API Logs, Model Outputs, and Error/Exception Events with GDPR Privacy Masking
Platform: Zecpath Automated Hiring Platform
"""

import time
import json
import uuid
import hashlib
import traceback
from typing import List, Dict, Any, Optional
from ai_monitoring_observability.models import (
    LogLevel,
    LogType,
    APILogEntry,
    ModelOutputLogEntry,
    ErrorLogEntry,
)


class StructuredAILogger:
    """
    Centralized Observability Logging Engine.
    Emits structured, machine-parseable JSON logs across:
      1. API Ingress & Turn Transactions
      2. AI Model Inferences & Explainability Outputs
      3. Errors, Failures, and Circuit Breaker Events
    Enforces privacy scrubbing on sensitive demographic attributes.
    """

    def __init__(self, buffer_capacity: int = 10000):
        self.buffer_capacity = buffer_capacity
        self.api_logs: List[APILogEntry] = []
        self.model_logs: List[ModelOutputLogEntry] = []
        self.error_logs: List[ErrorLogEntry] = []
        self.raw_event_stream: List[Dict[str, Any]] = []

    def _hash_payload(self, payload: Any) -> str:
        if not payload:
            return ""
        s = json.dumps(payload, sort_keys=True) if isinstance(payload, (dict, list)) else str(payload)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    def log_api_request(
        self,
        endpoint: str,
        method: str = "POST",
        status_code: int = 200,
        latency_ms: float = 1.0,
        client_ip: str = "127.0.0.1",
        candidate_id: Optional[str] = None,
        payload: Optional[Any] = None,
        trace_id: Optional[str] = None,
    ) -> APILogEntry:
        """
        Logs API call with latency and execution telemetry.
        """
        tid = trace_id or f"TR-{uuid.uuid4().hex[:10].upper()}"
        entry = APILogEntry(
            trace_id=tid,
            timestamp=time.time(),
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            latency_ms=latency_ms,
            client_ip=client_ip,
            candidate_id=candidate_id,
            payload_hash=self._hash_payload(payload),
        )
        self.api_logs.append(entry)
        self.raw_event_stream.append(entry.to_dict())

        # Bound buffer
        if len(self.api_logs) > self.buffer_capacity:
            self.api_logs.pop(0)
        return entry

    def log_model_output(
        self,
        candidate_id: str,
        subsystem: str,
        input_text: str,
        output_tokens: int,
        confidence_score: float,
        predicted_grade: str,
        inference_latency_ms: float,
        explainability_factors: Optional[Dict[str, float]] = None,
        trace_id: Optional[str] = None,
    ) -> ModelOutputLogEntry:
        """
        Logs AI model evaluation output with confidence and explainability attributions.
        """
        tid = trace_id or f"TR-{uuid.uuid4().hex[:10].upper()}"
        entry = ModelOutputLogEntry(
            trace_id=tid,
            timestamp=time.time(),
            candidate_id=candidate_id,
            subsystem=subsystem,
            input_text_hash=self._hash_payload(input_text),
            output_tokens=output_tokens,
            confidence_score=confidence_score,
            predicted_grade=predicted_grade,
            inference_latency_ms=inference_latency_ms,
            explainability_factors=explainability_factors or {},
        )
        self.model_logs.append(entry)
        self.raw_event_stream.append(entry.to_dict())

        if len(self.model_logs) > self.buffer_capacity:
            self.model_logs.pop(0)
        return entry

    def log_error(
        self,
        error_type: str,
        message: str,
        subsystem: str = "general",
        severity: LogLevel = LogLevel.ERROR,
        recoverable: bool = True,
        exc: Optional[Exception] = None,
        trace_id: Optional[str] = None,
    ) -> ErrorLogEntry:
        """
        Logs error event with exception stack traces.
        """
        tid = trace_id or f"TR-{uuid.uuid4().hex[:10].upper()}"
        st = traceback.format_exc() if exc else ""
        entry = ErrorLogEntry(
            trace_id=tid,
            timestamp=time.time(),
            error_type=error_type,
            message=message,
            stack_trace=st,
            subsystem=subsystem,
            severity=severity,
            recoverable=recoverable,
        )
        self.error_logs.append(entry)
        self.raw_event_stream.append(entry.to_dict())

        if len(self.error_logs) > self.buffer_capacity:
            self.error_logs.pop(0)
        return entry

    def get_recent_api_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self.api_logs[-limit:]]

    def get_recent_model_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self.model_logs[-limit:]]

    def get_recent_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self.error_logs[-limit:]]

    def get_logs_by_candidate(self, candidate_id: str) -> List[Dict[str, Any]]:
        res = []
        for l in self.api_logs:
            if l.candidate_id == candidate_id:
                res.append(l.to_dict())
        for m in self.model_logs:
            if m.candidate_id == candidate_id:
                res.append(m.to_dict())
        return sorted(res, key=lambda x: x["timestamp"])

    def get_summary_statistics(self) -> Dict[str, Any]:
        total_api = len(self.api_logs)
        total_model = len(self.model_logs)
        total_errors = len(self.error_logs)

        error_rate = round((total_errors / max(1, total_api)) * 100.0, 2)
        avg_api_latency = (
            round(sum(l.latency_ms for l in self.api_logs) / max(1, total_api), 2)
            if total_api > 0
            else 0.0
        )
        avg_confidence = (
            round(sum(m.confidence_score for m in self.model_logs) / max(1, total_model), 3)
            if total_model > 0
            else 0.0
        )

        return {
            "total_api_calls": total_api,
            "total_model_inferences": total_model,
            "total_errors_logged": total_errors,
            "error_rate_pct": error_rate,
            "average_api_latency_ms": avg_api_latency,
            "average_model_confidence": avg_confidence,
        }

