"""
Day 27: Unit Tests for Sentiment Scorer
=======================================
Tests:
1. Positive and enthusiastic sentiment detection
2. Neutral professional matter-of-fact tone
3. Negative and dissatisfied tone
4. Defensive and hostile demeanor markers
5. Candidate engagement level classification
"""

import unittest
from screening_ai.behavioral_models import (
    SentimentPolarity,
    EngagementLevel,
)
from screening_ai.sentiment_scorer import SentimentScorer


class TestSentimentScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = SentimentScorer()

    def test_enthusiastic_positive_sentiment(self):
        """Enthusiastic answers with positive keywords should classify as VERY_POSITIVE."""
        text = "I am really excited about this opportunity. I loved collaborating with the engineering team and we achieved fantastic results."
        res = self.scorer.analyze_sentiment(text)
        self.assertIn(res.polarity, [SentimentPolarity.VERY_POSITIVE, SentimentPolarity.POSITIVE])
        self.assertGreater(res.compound_score, 0.2)
        self.assertEqual(res.engagement_level, EngagementLevel.HIGHLY_ENGAGED)
        self.assertTrue(len(res.positive_keywords) >= 2)

    def test_neutral_professional_sentiment(self):
        """Standard matter-of-fact career answers should classify as NEUTRAL."""
        text = "I spent three years developing backend APIs in Python and managing PostgreSQL tables."
        res = self.scorer.analyze_sentiment(text)
        self.assertEqual(res.polarity, SentimentPolarity.NEUTRAL)
        self.assertAlmostEqual(res.compound_score, 0.0, delta=0.2)
        self.assertEqual(res.engagement_level, EngagementLevel.COOPERATIVE)

    def test_negative_dissatisfied_sentiment(self):
        """Frustrated, critical answers should classify as NEGATIVE."""
        text = "The previous company was a terrible mess. I hated the toxic work environment and pointless meetings."
        res = self.scorer.analyze_sentiment(text)
        self.assertEqual(res.polarity, SentimentPolarity.NEGATIVE)
        self.assertLess(res.compound_score, -0.2)
        self.assertIn("toxic", res.negative_keywords)

    def test_defensive_hostile_response(self):
        """Responses with defensive patterns must trigger DEFENSIVE polarity."""
        text = "Why are you asking me that? That is none of your business and I refuse to answer."
        res = self.scorer.analyze_sentiment(text)
        self.assertEqual(res.polarity, SentimentPolarity.DEFENSIVE)
        self.assertEqual(res.engagement_level, EngagementLevel.DEFENSIVE)
        self.assertGreater(len(res.defensive_keywords), 0)
        self.assertIn("none of your business", res.defensive_keywords)

    def test_reluctant_passive_response(self):
        """Reluctant or minimal responses should be classified accordingly."""
        text = "I guess if I really have to answer, fine."
        res = self.scorer.analyze_sentiment(text)
        self.assertEqual(res.engagement_level, EngagementLevel.RELUCTANT)


if __name__ == "__main__":
    unittest.main()
