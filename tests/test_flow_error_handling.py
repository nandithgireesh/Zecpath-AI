"""
Unit Tests: Day 29 Error-Handling Flow Design
=============================================
Tests multi-stage silence nudges, confusion intent detection,
repeated answer detection, and retry circuit breaker policies.
"""

import unittest
from screening_ai.flow_models import (
    NudgeLevel,
    RetryPolicyAction,
    SilenceEvent,
    ConfusionEvent,
    RepetitionEvent,
)
from screening_ai.error_handling_flow import ErrorHandlingFlowManager
from screening_ai.fallback_bank import (
    get_fallback_for_question,
    get_simplified_question,
    get_paraphrase,
    get_scenario,
    get_silence_nudge,
)


class TestErrorHandlingFlow(unittest.TestCase):
    """Test suite for ErrorHandlingFlowManager and FallbackBank."""

    def setUp(self):
        self.manager = ErrorHandlingFlowManager()

    # -------------------------------------------------------------------------
    # 1. Silence Latency Nudge Tests
    # -------------------------------------------------------------------------
    def test_silence_gentle_check(self):
        """Verify 5-9 second silence produces a gentle check-in nudge."""
        event = self.manager.evaluate_silence(duration_ms=6500, consecutive_silence_count=1)
        self.assertEqual(event.nudge_level, NudgeLevel.GENTLE_CHECK)
        self.assertFalse(event.is_timeout)
        self.assertTrue(len(event.nudge_prompt) > 10)
        self.assertIn("Are you still with me", event.nudge_prompt)

    def test_silence_assist_rephrase(self):
        """Verify 10-19 second silence produces an assist/rephrase nudge."""
        event = self.manager.evaluate_silence(duration_ms=14000, consecutive_silence_count=2)
        self.assertEqual(event.nudge_level, NudgeLevel.ASSIST_REPHRASE)
        self.assertFalse(event.is_timeout)
        self.assertTrue("repeat" in event.nudge_prompt.lower() or "rephrase" in event.nudge_prompt.lower())

    def test_silence_timeout_transition(self):
        """Verify >= 20 second silence triggers a timeout advance."""
        event = self.manager.evaluate_silence(duration_ms=25000, consecutive_silence_count=3)
        self.assertEqual(event.nudge_level, NudgeLevel.TIMEOUT_TRANSITION)
        self.assertTrue(event.is_timeout)
        self.assertTrue("move on" in event.nudge_prompt.lower() or "next" in event.nudge_prompt.lower())

    # -------------------------------------------------------------------------
    # 2. Confusion Detection Tests
    # -------------------------------------------------------------------------
    def test_confusion_explicit_cues(self):
        """Verify common confusion phrases trigger ConfusionEvent."""
        test_phrases = [
            "I don't understand what you mean",
            "Can you please clarify that question?",
            "Could you rephrase that in simpler terms?",
            "Sorry, what are you asking?",
            "what was the question again?",
        ]
        for phrase in test_phrases:
            event = self.manager.detect_confusion(phrase, question_id="sys_design_scalability")
            self.assertIsNotNone(event, f"Failed to detect confusion for phrase: '{phrase}'")
            self.assertIsInstance(event, ConfusionEvent)
            self.assertTrue(len(event.suggested_clarification) > 15)
            # Should have pulled simplified question
            self.assertIsNotNone(event.fallback_question_used)

    def test_confusion_short_expressions(self):
        """Verify short single-word confusion triggers."""
        event = self.manager.detect_confusion("what?")
        self.assertIsNotNone(event)
        self.assertEqual(event.trigger_phrase, "what?")

    def test_no_confusion_on_valid_answers(self):
        """Verify valid technical answers do not trigger confusion."""
        valid_answers = [
            "In my previous project, we deployed Redis clusters and Kafka for message queuing.",
            "I have 5 years of experience building Python microservices using FastAPI and Docker.",
            "We optimized database queries by adding composite B-tree indexes on foreign keys."
        ]
        for answer in valid_answers:
            event = self.manager.detect_confusion(answer)
            self.assertIsNone(event, f"False positive confusion on valid answer: '{answer}'")

    # -------------------------------------------------------------------------
    # 3. Repeated Answer Detection Tests
    # -------------------------------------------------------------------------
    def test_repetition_explicit_markers(self):
        """Verify phrases like 'as I said before' trigger RepetitionEvent."""
        candidate_text = "As I mentioned earlier, we used Redis and Celery for background processing."
        previous_turns = ["We used Celery for background jobs."]
        event = self.manager.detect_repetition(candidate_text, previous_turns)
        self.assertIsNotNone(event)
        self.assertEqual(event.similarity_score, 1.0)
        self.assertTrue("reiterating" in event.pivot_prompt.lower() or "earlier" in event.pivot_prompt.lower())

    def test_repetition_high_jaccard_overlap(self):
        """Verify verbatim or near-identical text triggers RepetitionEvent."""
        prev = "We implemented horizontal pod autoscaling with Prometheus metrics in Kubernetes."
        curr = "We implemented horizontal pod autoscaling with Prometheus metrics in Kubernetes cluster."
        event = self.manager.detect_repetition(curr, [prev])
        self.assertIsNotNone(event)
        self.assertGreaterEqual(event.similarity_score, 0.60)

    def test_no_repetition_on_novel_answers(self):
        """Verify completely distinct answers do not trigger repetition."""
        prev = "For our frontend we built interactive dashboards with React, TypeScript, and Redux."
        curr = "Regarding database performance, we partitioned large audit tables by month and added indexes."
        event = self.manager.detect_repetition(curr, [prev])
        self.assertIsNone(event)

    # -------------------------------------------------------------------------
    # 4. Polite Failure & Retry Circuit Breaker Tests
    # -------------------------------------------------------------------------
    def test_retry_policy_progression(self):
        """Verify circuit breaker transitions from retry -> fallback -> skip."""
        qid = "sys_design_scalability"

        # Turn 0: normal attempt
        act0, _ = self.manager.evaluate_retry_policy(qid, current_retries=0, consecutive_failures=0)
        self.assertEqual(act0, RetryPolicyAction.RETRY_PRIMARY)

        # Turn 1: offer simplified fallback
        act1, prompt1 = self.manager.evaluate_retry_policy(qid, current_retries=1, consecutive_failures=0)
        self.assertEqual(act1, RetryPolicyAction.TRY_FALLBACK)
        self.assertTrue("simpler" in prompt1.lower() or "website" in prompt1.lower())

        # Turn 2: max retries reached -> skip question
        act2, prompt2 = self.manager.evaluate_retry_policy(qid, current_retries=2, consecutive_failures=0)
        self.assertEqual(act2, RetryPolicyAction.SKIP_QUESTION)
        self.assertTrue("moving forward" in prompt2.lower() or "fine" in prompt2.lower())

    def test_retry_policy_abort_on_consecutive_failures(self):
        """Verify 3 consecutive failures abort the call gracefully."""
        act, prompt = self.manager.evaluate_retry_policy(
            question_id="sys_design_scalability",
            current_retries=0,
            consecutive_failures=3
        )
        self.assertEqual(act, RetryPolicyAction.ABORT_CALL)
        self.assertTrue("reschedule" in prompt.lower())

    # -------------------------------------------------------------------------
    # 5. Fallback Bank Tests
    # -------------------------------------------------------------------------
    def test_fallback_bank_structure(self):
        """Verify fallback bank returns simplified, paraphrase, and scenario questions."""
        q = get_fallback_for_question("database_optimization")
        self.assertIsNotNone(q)
        self.assertEqual(q.category, "Databases")
        self.assertTrue(len(q.simplified_text) > 10)
        self.assertTrue(len(q.paraphrase_text) > 10)
        self.assertTrue(len(q.applied_scenario) > 10)
        self.assertTrue(len(q.hint_keywords) >= 3)


if __name__ == "__main__":
    unittest.main()
