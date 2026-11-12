"""
Unit Tests for Day 31: Safety Fallback Engine & Graceful Degradation
"""

import unittest
from screening_ai.failure_models import (
    SafetyDegradationTier,
    FailureSeverity,
    ClarificationAction,
)
from screening_ai.safety_fallback_engine import SafetyFallbackEngine


class TestSafetyFallbackEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SafetyFallbackEngine(
            session_id="test_sess_001",
            candidate_id="cand_test_001",
        )

    def test_initial_state(self):
        """Initial state should be NORMAL_FLOW with zero failures."""
        self.assertEqual(self.engine.current_tier, SafetyDegradationTier.NORMAL_FLOW)
        self.assertEqual(self.engine.consecutive_failures, 0)
        self.assertEqual(self.engine.total_failures, 0)

    def test_single_failure_retry_budget(self):
        """First failure on question should degrade to SIMPLIFIED_QUESTIONING and decrement retry budget."""
        tier, decision, handoff = self.engine.record_failure(
            question_id="q1",
            failure_type="SILENCE",
        )
        self.assertEqual(tier, SafetyDegradationTier.SIMPLIFIED_QUESTIONING)
        self.assertIsNotNone(decision)
        self.assertIsNone(handoff)
        self.assertEqual(decision.attempt_number, 1)
        self.assertEqual(decision.retry_budget_remaining, 1)
        self.assertFalse(decision.escalation_required)

    def test_second_failure_structured_verification(self):
        """Second failure on same question degrades to STRUCTURED_VERIFICATION."""
        self.engine.record_failure("q1", "SILENCE")
        tier, decision, handoff = self.engine.record_failure("q1", "SILENCE")
        self.assertEqual(tier, SafetyDegradationTier.STRUCTURED_VERIFICATION)
        self.assertEqual(decision.attempt_number, 2)
        self.assertEqual(decision.retry_budget_remaining, 0)
        self.assertIn("yes or no", decision.prompt_message.lower())

    def test_third_failure_polite_skip(self):
        """Third failure on same question triggers POLITE_SKIP to move conversation forward."""
        self.engine.record_failure("q1", "SILENCE")
        self.engine.record_failure("q1", "SILENCE")
        # Reset consecutive counter simulate intermediate pass so circuit breaker doesn't trip first
        self.engine.consecutive_failures = 1
        tier, decision, handoff = self.engine.record_failure("q1", "SILENCE")
        self.assertEqual(decision.action, ClarificationAction.POLITE_SKIP)
        self.assertIn("move on", decision.prompt_message.lower())

    def test_circuit_breaker_emergency_handoff(self):
        """3 consecutive failures triggers circuit breaker and builds SafetyHandoffPacket."""
        self.engine.record_failure("q1", "SILENCE")
        self.engine.record_failure("q2", "PACKET_LOSS")
        tier, decision, handoff = self.engine.record_failure("q3", "EVASION")

        self.assertEqual(tier, SafetyDegradationTier.EMERGENCY_HUMAN_HANDOFF)
        self.assertTrue(decision.escalation_required)
        self.assertEqual(decision.action, ClarificationAction.HUMAN_ESCALATION)
        self.assertIsNotNone(handoff)
        self.assertEqual(handoff.candidate_id, "cand_test_001")
        self.assertIn("consecutive", handoff.reason)

    def test_success_resets_consecutive_counter(self):
        """Success resets consecutive failure counter to zero."""
        self.engine.record_failure("q1", "SILENCE")
        self.assertEqual(self.engine.consecutive_failures, 1)
        self.engine.record_success("q1")
        self.assertEqual(self.engine.consecutive_failures, 0)
        self.assertEqual(self.engine.current_tier, SafetyDegradationTier.NORMAL_FLOW)


if __name__ == "__main__":
    unittest.main()
