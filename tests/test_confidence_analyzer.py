"""
Day 27: Unit Tests for Confidence Analyzer
==========================================
Tests:
1. Vocal filler and hesitation detection
2. Repetitions and false starts
3. Latency delay and internal pauses
4. Words Per Minute (WPM) and pacing classification
5. Epistemic hedging and uncertainty scoring
6. Overall turn confidence calculation
"""

import unittest
from screening_ai.behavioral_models import (
    HesitationType,
    PaceRating,
    TurnConfidenceMetrics,
)
from screening_ai.confidence_analyzer import ConfidenceAnalyzer


class TestConfidenceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ConfidenceAnalyzer()

    def test_confident_articulate_answer(self):
        """Confident direct answer with no fillers or hedging should receive high score."""
        text = "I have 5 years of experience building Python microservices with FastAPI and Docker."
        metrics = self.analyzer.evaluate_turn_confidence(
            raw_text=text,
            duration_seconds=5.2,
            latency_ms=1200,
        )
        self.assertGreaterEqual(metrics.final_confidence_score, 88.0)
        self.assertEqual(metrics.confidence_tier, "HIGH")
        self.assertEqual(len(metrics.hesitation_incidents), 0)
        self.assertEqual(metrics.uncertainty.hedging_count, 0)
        self.assertEqual(metrics.pace_metrics.pace_rating, PaceRating.OPTIMAL)

    def test_vocal_fillers_detected(self):
        """Excessive vocal fillers (um, uh, like, you know) should incur penalties."""
        text = "Um, uh, well, you know, I basically, uh, worked on some databases."
        incidents, penalty = self.analyzer.analyze_hesitations(text)
        self.assertGreater(penalty, 10.0)
        self.assertGreater(len(incidents), 0)
        types = [inc.type for inc in incidents]
        self.assertIn(HesitationType.FILLER_WORD, types)

    def test_repetition_and_stutter_detected(self):
        """Word repetitions and false starts should be detected and penalized."""
        text = "I- I think the the project was deployed on AWS."
        incidents, penalty = self.analyzer.analyze_hesitations(text)
        self.assertGreater(penalty, 5.0)
        types = [inc.type for inc in incidents]
        self.assertTrue(
            HesitationType.REPETITION in types or HesitationType.FALSE_START in types
        )

    def test_response_latency_penalty(self):
        """Long hesitation latency before answering (>3000ms) should incur a penalty."""
        text = "Yes, I am comfortable with Docker."
        incidents, penalty = self.analyzer.analyze_hesitations(text, latency_ms=5000)
        self.assertGreater(penalty, 0.0)
        self.assertTrue(any(inc.type == HesitationType.LATENCY_DELAY for inc in incidents))

    def test_pacing_wpm_optimal(self):
        """Conversational pace around 130-150 WPM should be rated OPTIMAL."""
        # 14 words in 6 seconds = 140 WPM
        text = "We utilized PostgreSQL for relational storage and Redis for caching session tokens."
        pace = self.analyzer.calculate_pacing(text, duration_seconds=6.0)
        self.assertAlmostEqual(pace.wpm, 120.0, delta=10.0)
        self.assertEqual(pace.pace_rating, PaceRating.OPTIMAL)
        self.assertEqual(pace.pacing_score, 100.0)

    def test_pacing_wpm_very_slow(self):
        """Very slow speech (<100 WPM) should be rated VERY_SLOW and penalized."""
        # 6 words in 6 seconds = 60 WPM
        text = "I worked on machine learning."
        pace = self.analyzer.calculate_pacing(text, duration_seconds=6.0)
        self.assertLess(pace.wpm, 100.0)
        self.assertEqual(pace.pace_rating, PaceRating.VERY_SLOW)
        self.assertLess(pace.pacing_score, 80.0)

    def test_pacing_wpm_rushed(self):
        """Very fast speech (>185 WPM) should be rated RUSHED."""
        # 35 words in 10 seconds = 210 WPM
        words = "word " * 35
        pace = self.analyzer.calculate_pacing(words, duration_seconds=10.0)
        self.assertGreater(pace.wpm, 185.0)
        self.assertEqual(pace.pace_rating, PaceRating.RUSHED)

    def test_uncertainty_and_hedging(self):
        """Uncertain hedging language should trigger uncertainty score and discount."""
        text = "I think maybe we could possibly use Kafka, but I'm not sure if that's best."
        uncertainty = self.analyzer.detect_uncertainty(text)
        self.assertGreaterEqual(uncertainty.hedging_count, 3)
        self.assertGreaterEqual(uncertainty.uncertainty_score, 70.0)
        self.assertGreaterEqual(uncertainty.confidence_discount, 20.0)
        self.assertTrue(any("kafka" in s.lower() for s in uncertainty.flagged_statements))


if __name__ == "__main__":
    unittest.main()
