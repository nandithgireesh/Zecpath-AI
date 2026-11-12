"""
Unit Tests for Day 36: Confidence & Stress Indicators Subsystem
===============================================================
Validates:
1. Hesitation pattern detection (long pauses, repeated words/stutters, uncertainty phrases)
2. Professional sentiment scoring & emotional composure
3. Contradiction pattern detection (within-turn and cross-turn)
4. Quantitative stress indicator measurement & StressLevel
5. Composite behavioral confidence scoring & tiering
6. End-to-end integration with HRInterviewFlowEngine & ATS dossier export
"""

import unittest
from interview_ai.confidence_models import (
    HesitationType,
    SentimentPolarity,
    SentimentTone,
    ContradictionSeverity,
    StressLevel,
    ConfidenceTier,
)
from interview_ai.confidence_analyzer import (
    HesitationPatternDetector,
    ContradictionDetector,
    StressIndicatorScorer,
    ConfidenceAnalyzer,
)
from interview_ai.sentiment_scoring_engine import InterviewSentimentScorer
from interview_ai.hr_models import HRInterviewConfig, RoleTrack
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


class TestInterviewConfidenceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ConfidenceAnalyzer()
        self.hesitation_detector = HesitationPatternDetector()
        self.sentiment_scorer = InterviewSentimentScorer()
        self.contradiction_detector = ContradictionDetector()
        self.stress_scorer = StressIndicatorScorer()

    # =========================================================================
    # 1. Hesitation Pattern Tests
    # =========================================================================

    def test_long_pause_detection(self):
        """Excessive initial latency and transcript pause markers should be penalized."""
        # A. Initial latency of 4.5s (threshold is 2.8s)
        signals, score = self.hesitation_detector.analyze_hesitations(
            text="I implemented the microservices architecture using FastAPI.",
            response_time_seconds=4.5,
        )
        self.assertTrue(any(s.type == HesitationType.LONG_PAUSE for s in signals))
        self.assertLess(score, 100.0)

        # B. Internal pause marker in transcript "[pause 3.5s]"
        signals_int, score_int = self.hesitation_detector.analyze_hesitations(
            text="We started with monolith [pause 3.5s] and then migrated to Kubernetes.",
            response_time_seconds=1.5,
        )
        self.assertTrue(any(s.type == HesitationType.LONG_PAUSE for s in signals_int))
        self.assertLess(score_int, 95.0)

    def test_repeated_words_and_stutters(self):
        """Repeated words ('I I', 'the the') and false starts should be detected."""
        text = "I I think the the system crashed, so we we re- deployed the cluster."
        signals, score = self.hesitation_detector.analyze_hesitations(text, response_time_seconds=1.0)
        types = [s.type for s in signals]
        self.assertIn(HesitationType.REPEATED_WORD, types)
        self.assertIn(HesitationType.FALSE_START, types)
        self.assertLessEqual(score, 88.0)

    def test_uncertainty_phrases_hedging(self):
        """Epistemic hedging phrases should be flagged as UNCERTAINTY_PHRASE."""
        text = "I think maybe the database locked up, but I'm not really sure, could be wrong."
        signals, score = self.hesitation_detector.analyze_hesitations(text, response_time_seconds=1.2)
        unc_signals = [s for s in signals if s.type == HesitationType.UNCERTAINTY_PHRASE]
        self.assertGreaterEqual(len(unc_signals), 2)
        self.assertLess(score, 85.0)

    # =========================================================================
    # 2. Sentiment Scoring Engine Tests (Deliverable 2)
    # =========================================================================

    def test_constructive_optimism_sentiment(self):
        """Enthusiastic candidate taking full ownership should receive high composure and positive tone."""
        text = (
            "I was really excited to take full ownership of the payment pipeline redesign. "
            "Our team collaborated closely, solved the throughput bottlenecks, and successfully delivered "
            "a 40% latency optimization that we are extremely proud of."
        )
        result = self.sentiment_scorer.analyze_sentiment(text)
        self.assertEqual(result.polarity, SentimentPolarity.POSITIVE)
        self.assertGreaterEqual(result.composure_score, 85.0)
        self.assertIn(result.emotional_tone, {SentimentTone.ENTHUSIASTIC, SentimentTone.COMPOSED_OPTIMISTIC})
        self.assertGreater(len(result.positive_cues), 0)

    def test_defensive_and_hostile_sentiment(self):
        """Defensive evasion and hostile remarks should be detected as DEFENSIVE_GUARDED."""
        text = "Why are you asking me that? That's none of your business and I already told you in my resume."
        result = self.sentiment_scorer.analyze_sentiment(text)
        self.assertEqual(result.emotional_tone, SentimentTone.DEFENSIVE_GUARDED)
        self.assertLess(result.composure_score, 60.0)
        self.assertGreater(len(result.defensive_cues), 0)

    # =========================================================================
    # 3. Contradiction Pattern Tests
    # =========================================================================

    def test_within_turn_contradiction(self):
        """Self-negation within a single turn should be flagged as an inconsistency."""
        text = "I built the entire distributed caching layer by myself alone. Actually, no wait, the team leads handled all the core architecture."
        incidents, consistency_score = self.contradiction_detector.analyze_contradictions(
            session_id="test_sess_01",
            turn_index=1,
            text=text,
        )
        self.assertGreater(len(incidents), 0)
        self.assertLess(consistency_score, 85.0)

    def test_cross_turn_contradiction(self):
        """Conflicting factual statements across turns (years of experience) should be flagged."""
        detector = ContradictionDetector()
        session_id = "test_sess_cross"

        # Turn 1: Claims 6 years of experience
        inc1, score1 = detector.analyze_contradictions(
            session_id=session_id,
            turn_index=1,
            text="I have 6 years of experience architecting large scale backend systems."
        )
        self.assertEqual(len(inc1), 0)
        self.assertEqual(score1, 100.0)

        # Turn 3: Contradicts and claims 1 year of experience
        inc2, score2 = detector.analyze_contradictions(
            session_id=session_id,
            turn_index=3,
            text="Since I only have 1 year of experience in the industry, I shadowed senior engineers."
        )
        self.assertGreater(len(inc2), 0)
        self.assertIn("EXPERIENCE_TIMELINE_CLASH", [i.contradiction_type for i in inc2])
        self.assertLessEqual(score2, 70.0)

    # =========================================================================
    # 4. Stress Indicators & Stress Level Tests
    # =========================================================================

    def test_stress_indicators_low_vs_high(self):
        """Composed answer should yield LOW stress, whereas stutter/hesitation cluster yields HIGH stress."""
        # Low Stress
        low_res = self.analyzer.evaluate_turn(
            turn_index=1,
            text="We implemented continuous deployment using GitHub Actions and automated regression tests.",
            response_time_seconds=1.2,
        )
        self.assertEqual(low_res.stress.stress_level, StressLevel.LOW)
        self.assertLess(low_res.stress.stress_index, 25.0)

        # High Stress (Heavy stutters, long delay, multiple uncertainty hedges)
        high_res = self.analyzer.evaluate_turn(
            turn_index=2,
            text="I I... [pause 3s] I think maybe the the cluster was failing... sorry I'm really nervous, could be wrong.",
            response_time_seconds=4.8,
        )
        self.assertIn(high_res.stress.stress_level, {StressLevel.HIGH, StressLevel.CRITICAL})
        self.assertGreaterEqual(high_res.stress.stress_index, 50.0)

    # =========================================================================
    # 5. Composite Behavioral Confidence Score Tests (Deliverable 1)
    # =========================================================================

    def test_authoritative_candidate_confidence(self):
        """Flawless, articulate, and confident response achieves AUTHORITATIVE tier (>85.0)."""
        text = (
            "I served as the Lead Architect for our high-throughput streaming engine. "
            "When traffic spiked by 300%, I identified connection pool saturation, introduced Redis caching, "
            "and reduced 99th percentile response latency from 1.2 seconds to 85 milliseconds."
        )
        result = self.analyzer.evaluate_turn(
            turn_index=1,
            text=text,
            response_time_seconds=1.1,
        )
        self.assertGreaterEqual(result.confidence_score, 88.0)
        self.assertEqual(result.confidence_tier, ConfidenceTier.AUTHORITATIVE)
        self.assertGreater(len(result.key_strengths), 0)
        self.assertEqual(len(result.risk_flags), 0)

    def test_fragile_high_stress_candidate_confidence(self):
        """Flustered response with stutters and defensive comments lands in HESITANT or HIGH_STRESS tier."""
        text = "Why are you asking that? I I don't know, maybe we used Docker... not really sure, could be wrong."
        result = self.analyzer.evaluate_turn(
            turn_index=1,
            text=text,
            response_time_seconds=4.5,
        )
        self.assertLessEqual(result.confidence_score, 70.0)
        self.assertIn(result.confidence_tier, {ConfidenceTier.HESITANT, ConfidenceTier.HIGH_STRESS})
        self.assertGreater(len(result.risk_flags), 0)

    # =========================================================================
    # 6. End-to-End HR Flow Engine Integration & ATS Dossier Telemetry
    # =========================================================================

    def test_hr_flow_engine_confidence_integration(self):
        """Verifies that HRInterviewFlowEngine captures confidence in turns and exports ATS dossier."""
        engine = HRInterviewFlowEngine()
        config = HRInterviewConfig.auto_classify(
            candidate_id="CAND-DAY36-TEST",
            candidate_name="Kavita Rao",
            job_role="Senior DevOps Architect",
            experience_years=6.0,
            target_skills=["Kubernetes", "Terraform", "Go"],
        )

        session = engine.start_session(config)
        self.assertEqual(len(session.turns), 1)

        # Turn 1: Confident, articulate response
        resp1 = (
            "Hello! I have 6 years of experience leading cloud infrastructure transformations. "
            "I spearheaded our migration to AWS EKS, improving deployment frequency by 4x."
        )
        engine.process_turn(session.session_id, resp1, response_time_seconds=1.2)
        turn1 = session.turns[0]
        self.assertIsNotNone(turn1.confidence_evaluation)
        self.assertGreaterEqual(turn1.confidence_evaluation.confidence_score, 85.0)
        self.assertEqual(turn1.confidence_evaluation.confidence_tier, ConfidenceTier.AUTHORITATIVE)

        # Turn 2: Natural second turn
        resp2 = (
            "When troubleshooting high memory usage on nodes, I analyze cgroup metrics and kube-state-metrics. "
            "We optimized pod requests and limits, which resolved OOMKilled events permanently."
        )
        engine.process_turn(session.session_id, resp2, response_time_seconds=1.4)
        turn2 = session.turns[1]
        self.assertIsNotNone(turn2.confidence_evaluation)

        # Verify Session-wide Aggregations
        self.assertGreaterEqual(session.average_confidence_score, 80.0)
        self.assertIn(session.overall_confidence_tier, ["Authoritative", "Composed"])
        self.assertEqual(session.overall_stress_level.upper(), "LOW")

        # Export ATS Dossier
        dossier = engine.export_session_dossier(session.session_id)
        self.assertIn("behavioral_confidence_summary", dossier)
        b_summary = dossier["behavioral_confidence_summary"]
        self.assertGreaterEqual(b_summary["average_score"], 80.0)
        self.assertIn("confidence_tier", b_summary)
        self.assertIn("average_stress_index", b_summary)
        self.assertEqual(b_summary["overall_stress_level"].upper(), "LOW")
        self.assertIn("dominant_emotional_tone", b_summary)


if __name__ == "__main__":
    unittest.main()
