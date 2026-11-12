"""
Unit Tests for Day 31: Missing Answer & Non-Response Handler
"""

import unittest
from screening_ai.failure_models import MissingAnswerType
from screening_ai.missing_answer_handler import MissingAnswerHandler


class TestMissingAnswerHandler(unittest.TestCase):

    def test_complete_silence_detection(self):
        """Empty string should trigger COMPLETE_SILENCE and Tier 1 recovery."""
        res = MissingAnswerHandler.assess_response(
            text="",
            duration_ms=5000,
            consecutive_missing_count=0,
            topic="microservices architecture",
        )
        self.assertTrue(res.is_silence)
        self.assertEqual(res.category, MissingAnswerType.COMPLETE_SILENCE)
        self.assertEqual(res.recovery_tier, 1)
        self.assertIn("microservices architecture", res.recovery_prompt)

    def test_silence_escalation_tier2(self):
        """Second consecutive silence should trigger Tier 2 alternative phrasing."""
        res = MissingAnswerHandler.assess_response(
            text="   ",
            duration_ms=6000,
            consecutive_missing_count=1,
            topic="database transactions",
        )
        self.assertTrue(res.is_silence)
        self.assertEqual(res.recovery_tier, 2)
        self.assertIn("another angle", res.recovery_prompt)

    def test_empty_filler_line_check(self):
        """Utterances like 'uh... hello? can you hear me?' should be classified as EMPTY_FILLER."""
        res = MissingAnswerHandler.assess_response(
            text="uh... hello? can you hear me?",
            duration_ms=2500,
            consecutive_missing_count=0,
            topic="cloud deployments",
        )
        self.assertTrue(res.is_empty_filler)
        self.assertFalse(res.is_silence)
        self.assertEqual(res.category, MissingAnswerType.EMPTY_FILLER)
        self.assertIn("hear you", res.recovery_prompt.lower())

    def test_explicit_pass_triggers_tier3_bridge(self):
        """Utterance 'I don't know, pass' should trigger EXPLICIT_PASS with polite bridge."""
        res = MissingAnswerHandler.assess_response(
            text="I don't know, can we pass this question?",
            duration_ms=1800,
            next_topic="API rate limiting",
        )
        self.assertTrue(res.is_explicit_pass)
        self.assertEqual(res.category, MissingAnswerType.EXPLICIT_PASS)
        self.assertEqual(res.recovery_tier, 3)
        self.assertIn("API rate limiting", res.recovery_prompt)

    def test_evasive_deflection_relevance_reframe(self):
        """Evasive deflection should trigger Tier 2 relevance explanation."""
        res = MissingAnswerHandler.assess_response(
            text="Why do you need to know? Let's talk about cricket instead.",
            duration_ms=3000,
            topic="system design",
        )
        self.assertTrue(res.is_evasive)
        self.assertEqual(res.category, MissingAnswerType.EVASIVE_DEFLECTION)
        self.assertIn("technical background", res.recovery_prompt)

    def test_informative_answer_not_missing(self):
        """Genuine technical response should not be flagged as missing."""
        res = MissingAnswerHandler.assess_response(
            text="We implemented Celery tasks with Redis message broker to handle background email delivery.",
            duration_ms=4500,
        )
        self.assertFalse(res.is_silence)
        self.assertFalse(res.is_empty_filler)
        self.assertFalse(res.is_explicit_pass)
        self.assertFalse(res.is_evasive)
        self.assertIsNone(res.recovery_prompt)


if __name__ == "__main__":
    unittest.main()
