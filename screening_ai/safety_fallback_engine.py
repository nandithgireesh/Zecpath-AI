"""
Day 31: Safety Fallback & Graceful Degradation Engine
=====================================================
Coordinates fail-safe interview execution and human escalation:
- Tracks session failure counters and enforces circuit breakers.
- Implements progressive Graceful Degradation:
    NORMAL -> SIMPLIFIED_QUESTIONING -> STRUCTURED_VERIFICATION -> EMERGENCY_HUMAN_HANDOFF
- Generates immutable SafetyHandoffPacket audit payloads for ATS synchronization.
- Guarantees polite, non-blocking call termination, preventing deadlocks and infinite loops.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from screening_ai.failure_models import (
    SafetyDegradationTier,
    FailureSeverity,
    SafetyHandoffPacket,
    RetryDecision,
    ClarificationAction,
)


class SafetyFallbackEngine:
    """
    Manages failure tracking, degradation modes, circuit breakers,
    and emergency human escalation packaging.
    """

    MAX_RETRIES_PER_QUESTION = 2
    MAX_CONSECUTIVE_FAILURES = 3
    MAX_TOTAL_SESSION_FAILURES = 5

    def __init__(self, session_id: str, candidate_id: str):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.current_tier = SafetyDegradationTier.NORMAL_FLOW
        self.consecutive_failures = 0
        self.total_failures = 0
        self.unresolved_failures: List[str] = []
        self.question_retries: Dict[str, int] = {}
        self.transcript_history: List[Dict[str, Any]] = []

    def record_turn(self, role: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Appends a turn to the audit history."""
        self.transcript_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "message": message,
            "metadata": metadata or {},
        })

    def record_success(self, question_id: str):
        """Resets consecutive failure counter upon a successful turn."""
        self.consecutive_failures = 0
        if question_id in self.question_retries:
            del self.question_retries[question_id]
        if self.current_tier == SafetyDegradationTier.SIMPLIFIED_QUESTIONING:
            # Self-heal back to normal flow after success
            self.current_tier = SafetyDegradationTier.NORMAL_FLOW

    def record_failure(
        self,
        question_id: str,
        failure_type: str,
        severity: FailureSeverity = FailureSeverity.MEDIUM,
    ) -> Tuple[SafetyDegradationTier, Optional[RetryDecision], Optional[SafetyHandoffPacket]]:
        """
        Records a conversational or acoustic failure, evaluates circuit breakers,
        and determines next action (Retry, Structured Degradation, or Human Escalation).
        """
        self.consecutive_failures += 1
        self.total_failures += 1
        self.unresolved_failures.append(f"{question_id}:{failure_type}")

        current_retries = self.question_retries.get(question_id, 0) + 1
        self.question_retries[question_id] = current_retries

        # 1. Critical Circuit Breaker: Trigger Emergency Human Handoff
        if (
            self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES
            or self.total_failures >= self.MAX_TOTAL_SESSION_FAILURES
            or severity == FailureSeverity.CRITICAL
        ):
            self.current_tier = SafetyDegradationTier.EMERGENCY_HUMAN_HANDOFF
            handoff = self.build_handoff_packet(
                reason=f"Exceeded failure threshold ({self.consecutive_failures} consecutive failures: {failure_type})"
            )
            decision = RetryDecision(
                action=ClarificationAction.HUMAN_ESCALATION,
                attempt_number=current_retries,
                max_attempts=self.MAX_RETRIES_PER_QUESTION,
                retry_budget_remaining=0,
                prompt_message=(
                    "It appears we are experiencing persistent technical difficulties on this line. "
                    "To ensure your assessment is completely fair, I have forwarded your profile "
                    "directly to our recruitment team for a personal follow-up. Thank you for your time!"
                ),
                escalation_required=True,
                severity=FailureSeverity.CRITICAL,
            )
            return self.current_tier, decision, handoff

        # 2. Per-Question Retry Budget Check
        if current_retries <= self.MAX_RETRIES_PER_QUESTION:
            # Attempt retry with degradation
            if current_retries == 1:
                self.current_tier = SafetyDegradationTier.SIMPLIFIED_QUESTIONING
                action = ClarificationAction.SIMPLIFIED_ALTERNATE
                prompt = "Let me simplify the question: could you share one specific example of how you implemented this in production?"
            else:
                self.current_tier = SafetyDegradationTier.STRUCTURED_VERIFICATION
                action = ClarificationAction.SEMANTIC_DISAMBIGUATION
                prompt = "To make it easier, have you worked with this technology in a production environment: yes or no?"

            decision = RetryDecision(
                action=action,
                attempt_number=current_retries,
                max_attempts=self.MAX_RETRIES_PER_QUESTION,
                retry_budget_remaining=self.MAX_RETRIES_PER_QUESTION - current_retries,
                prompt_message=prompt,
                escalation_required=False,
                severity=severity,
            )
            return self.current_tier, decision, None

        # 3. Retries Exhausted for Question: Polite Skip Bridge
        decision = RetryDecision(
            action=ClarificationAction.POLITE_SKIP,
            attempt_number=current_retries,
            max_attempts=self.MAX_RETRIES_PER_QUESTION,
            retry_budget_remaining=0,
            prompt_message="No problem at all. Let's move on to the next topic to make sure we cover everything today.",
            escalation_required=False,
            severity=FailureSeverity.LOW,
        )
        return self.current_tier, decision, None

    def build_handoff_packet(self, reason: str, partial_score: Optional[float] = None) -> SafetyHandoffPacket:
        """Constructs an immutable escalation payload for human recruiter review."""
        return SafetyHandoffPacket(
            session_id=self.session_id,
            candidate_id=self.candidate_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degradation_tier=self.current_tier,
            reason=reason,
            unresolved_failures=list(self.unresolved_failures),
            turns_completed=len(self.transcript_history),
            partial_score=partial_score,
            audio_summary={
                "consecutive_failures": self.consecutive_failures,
                "total_failures": self.total_failures,
            },
            transcript_snapshot=list(self.transcript_history),
        )
