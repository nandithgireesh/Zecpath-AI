"""
Day 27: Unit Tests for Behavioral Indicators Engine
===================================================
Tests:
1. Calculation of Communication Strength Indicators (Fluency, Assertiveness, Engagement, Pacing, Articulation)
2. Single-turn behavioral analysis
3. Multi-turn interview session behavioral report generation
4. Green flags, red flags, and recruiter interviewer probes
"""

import unittest
from screening_ai.behavioral_models import (
    SentimentPolarity,
    PaceRating,
    CommunicationGrade,
    BehavioralIndicatorsReport,
)
from screening_ai.behavioral_engine import BehavioralIndicatorsEngine


class TestBehavioralIndicatorsEngine(unittest.TestCase):

    def setUp(self):
        self.engine = BehavioralIndicatorsEngine()

    def test_communication_indicators_high_quality(self):
        """Articulate, fluent, and confident turn should yield EXCELLENT grade."""
        analysis = self.engine.analyze_turn(
            turn_id="TURN_01",
            raw_text="I have 6 years of experience architecting distributed cloud systems with Python and Kubernetes.",
            duration_seconds=4.2,
            latency_ms=1000,
        )
        ci = analysis.communication_indicators
        self.assertGreaterEqual(ci.fluency_score, 90.0)
        self.assertGreaterEqual(ci.assertiveness_score, 90.0)
        self.assertGreaterEqual(ci.overall_strength_score, 85.0)
        self.assertEqual(ci.grade, CommunicationGrade.EXCELLENT)

    def test_communication_indicators_hedging_and_fillers(self):
        """Turn with fillers and hedging should show reduced fluency and assertiveness."""
        analysis = self.engine.analyze_turn(
            turn_id="TURN_02",
            raw_text="Um, uh, well, I think maybe we could sort of use PostgreSQL, but I'm not sure.",
            duration_seconds=5.0,
            latency_ms=2500,
        )
        ci = analysis.communication_indicators
        self.assertLess(ci.fluency_score, 80.0)
        self.assertLess(ci.assertiveness_score, 60.0)
        self.assertIn(ci.grade, [CommunicationGrade.ACCEPTABLE, CommunicationGrade.NEEDS_IMPROVEMENT])

    def test_multi_turn_session_report_generation(self):
        """Multi-turn session report should aggregate metrics and produce recruiter insights."""
        turns = [
            {
                "turn_id": "T01",
                "raw_text": "I am delighted to interview today. I have 5 years in Python and FastAPI.",
                "duration_seconds": 6.0,
                "latency_ms": 1100,
            },
            {
                "turn_id": "T02",
                "raw_text": "I built high-throughput message pipelines using RabbitMQ and Redis cache.",
                "duration_seconds": 4.5,
                "latency_ms": 1400,
            },
            {
                "turn_id": "T03",
                "raw_text": "My current CTC is 18 LPA and my expected CTC is 24 LPA with a 30-day notice period.",
                "duration_seconds": 7.5,
                "latency_ms": 1200,
            },
        ]
        report = self.engine.analyze_session(
            candidate_id="CAND_NANDITH_01",
            session_id="SESS_DAY27_01",
            turns=turns,
        )
        self.assertIsInstance(report, BehavioralIndicatorsReport)
        self.assertEqual(report.total_turns_analyzed, 3)
        self.assertGreaterEqual(report.overall_confidence_score, 85.0)
        self.assertEqual(report.overall_pace_rating, PaceRating.OPTIMAL)
        self.assertGreater(len(report.behavioral_green_flags), 0)
        self.assertEqual(len(report.behavioral_red_flags), 0)
        self.assertIn("NANDITH", report.recruiter_executive_summary)

    def test_session_report_with_defensive_and_hedging_red_flags(self):
        """Session with defensive or heavily uncertain turns should flag warnings and probes."""
        turns = [
            {
                "turn_id": "T01",
                "raw_text": "I think maybe I used Docker once or twice, but I'm not really sure.",
                "duration_seconds": 4.0,
            },
            {
                "turn_id": "T02",
                "raw_text": "Why do you need to know my previous salary? That's none of your business.",
                "duration_seconds": 3.0,
            },
        ]
        report = self.engine.analyze_session(
            candidate_id="CAND_RISKY_02",
            session_id="SESS_DAY27_02",
            turns=turns,
        )
        self.assertEqual(report.overall_sentiment, SentimentPolarity.DEFENSIVE)
        self.assertGreater(len(report.behavioral_red_flags), 0)
        self.assertGreater(len(report.recommended_interviewer_probes), 0)
        self.assertTrue(any("defensive" in f.lower() for f in report.behavioral_red_flags))


if __name__ == "__main__":
    unittest.main()
