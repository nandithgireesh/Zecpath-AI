"""
Unit Tests for Day 30 Improved Intent Classifier
================================================
"""

import unittest
from screening_ai.improved_intent import OptimizedIntentClassifier
from screening_ai.intent_models import CandidateIntent


class TestImprovedIntentClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = OptimizedIntentClassifier()

    def test_terse_technical_rescue(self):
        text = "Celery workers backed by Redis broker."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
            question_prompt="How do you handle background processing?",
        )
        self.assertEqual(intent, CandidateIntent.CONFIRMING_SKILL)
        self.assertGreaterEqual(conf, 0.85)

    def test_terse_raft_consensus_rescue(self):
        text = "Raft consensus with idempotent sagas."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
        )
        self.assertEqual(intent, CandidateIntent.CONFIRMING_SKILL)

    def test_salary_range_detection(self):
        text = "My current is 18 LPA, expecting between 22 to 25 LPA negotiable."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Salary Expectation",
        )
        self.assertEqual(intent, CandidateIntent.STATING_SALARY)
        self.assertGreaterEqual(conf, 0.85)

    def test_notice_with_buyout(self):
        text = "Serving notice period, 20 days left, buyout possible."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Notice Period",
        )
        self.assertEqual(intent, CandidateIntent.STATING_AVAILABILITY)

    def test_clarify_statement_disambiguation(self):
        text = "Let me clarify, we used Docker containers with Kubernetes on AWS."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
        )
        self.assertNotEqual(intent, CandidateIntent.ASKING_CLARIFICATION)
        self.assertEqual(intent, CandidateIntent.CONFIRMING_SKILL)

    def test_genuine_clarification(self):
        text = "Could you repeat that? What do you mean by high-throughput?"
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
        )
        self.assertEqual(intent, CandidateIntent.ASKING_CLARIFICATION)

    def test_composite_utterance_secondary(self):
        text = "I have 5 years with Python and Django, and my expected CTC is 24 LPA."
        intent, conf, secondary = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
        )
        self.assertIn(intent, [CandidateIntent.CONFIRMING_SKILL, CandidateIntent.PROVIDING_EXPERIENCE, CandidateIntent.STATING_SALARY])
        self.assertTrue(CandidateIntent.STATING_SALARY in secondary or intent == CandidateIntent.STATING_SALARY)


    def test_vague_unrescued(self):
        text = "A little bit of everything, whatever the team decides."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
        )
        self.assertEqual(intent, CandidateIntent.VAGUE_ANSWER)

    def test_off_topic_detection(self):
        text = "Tell me about the stock market or cricket match today."
        intent, conf, _ = self.classifier.classify_intent(
            text=text,
            question_category="Technical Skills",
            question_prompt="Describe your Postgres indexing strategy.",
        )
        self.assertEqual(intent, CandidateIntent.OFF_TOPIC)


if __name__ == "__main__":
    unittest.main()
