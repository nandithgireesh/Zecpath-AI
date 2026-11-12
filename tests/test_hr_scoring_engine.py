"""
Tests for Day 37: HR Interview Scoring Engine, Weight Configuration, and Report Formatter
========================================================================================
"""

import unittest
import json
from datetime import datetime, timezone

from interview_ai.hr_models import (
    HRInterviewConfig,
    HRInterviewSession,
    InterviewTurnState,
    InterviewPhase,
    HRCategory,
    ExperienceTier,
    RoleTrack,
    CommunicationScoreBreakdown,
)
from interview_ai.confidence_models import (
    TurnConfidenceBreakdown,
    HesitationType,
    SentimentTone,
    StressLevel,
    ConfidenceTier,
)
from interview_ai.hr_scoring_models import (
    ScoringParameter,
    HiringRecommendation,
    RoleTrackPreset,
    WeightProfile,
    CandidateHRScoreReport,
)
from interview_ai.weight_config import (
    WeightConfigurationSystem,
    WeightConfigurationError,
)
from interview_ai.hr_scoring_engine import (
    AnswerRelevanceAnalyzer,
    LengthNormalizationEngine,
    HRInterviewScoringEngine,
)
from interview_ai.hr_score_report import HRScoreReportFormatter
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


class TestHRInterviewScoringEngine(unittest.TestCase):
    """Unit test suite verifying all Day 37 core deliverables."""

    def setUp(self):
        self.relevance_analyzer = AnswerRelevanceAnalyzer()
        self.normalizer = LengthNormalizationEngine()
        self.weight_system = WeightConfigurationSystem()
        self.scoring_engine = HRInterviewScoringEngine(weight_system=self.weight_system)

    def test_answer_relevance_high_relevance(self):
        """Validates that a detailed answer with domain keywords, prompt overlap, and metrics scores high."""
        prompt = "Describe a high-throughput architecture bottleneck you resolved under heavy load."
        response = (
            "During a promotional flash sale, our database connection pool was exhausted at 45,000 QPS. "
            "I investigated slow queries, added Redis read replicas to offload read traffic, and optimized indexes. "
            "This dropped latency by 65% from 420ms down to 18ms and restored full throughput availability."
        )
        eval_result = self.relevance_analyzer.evaluate_turn_relevance(
            turn_index=0,
            prompt=prompt,
            response=response,
            category=HRCategory.CAREER_JOURNEY.value
        )
        self.assertGreaterEqual(eval_result.raw_relevance_score, 80.0)
        self.assertGreaterEqual(eval_result.intent_match_score, 75.0)
        self.assertGreater(len(eval_result.detected_intent_themes), 2)
        self.assertEqual(len(eval_result.missing_aspects), 0)

    def test_answer_relevance_evasion_and_short(self):
        """Asserts that evasive responses or monosyllabic answers receive heavy deductions."""
        prompt = "How do you handle disagreements with engineering peers on technical choices?"
        evasive_response = "I don't know, skip this. None of your business."
        eval_result = self.relevance_analyzer.evaluate_turn_relevance(
            turn_index=0,
            prompt=prompt,
            response=evasive_response,
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT.value
        )
        self.assertLessEqual(eval_result.raw_relevance_score, 35.0)
        self.assertTrue(any("evasive" in m.lower() for m in eval_result.missing_aspects))

    def test_weight_configuration_default_profiles(self):
        """Verifies that default enterprise role profiles sum to exactly 1.0 and match design specs."""
        profiles = self.weight_system.DEFAULT_PROFILES
        self.assertIn("technical_roles", profiles)
        self.assertIn("leadership_roles", profiles)
        self.assertIn("client_facing_roles", profiles)
        self.assertIn("campus_fresher_roles", profiles)
        self.assertIn("standard_balanced", profiles)

        for key, p in profiles.items():
            self.assertTrue(p.validate_weights(), f"Profile {key} weights do not sum to 1.0")
            weights = p.as_dict()
            self.assertAlmostEqual(sum(weights.values()), 1.0, places=4)

        # Technical track gives highest weight to relevance
        tech = profiles["technical_roles"]
        self.assertEqual(tech.answer_relevance, 0.35)
        self.assertEqual(tech.communication, 0.25)

        # Client-facing track gives highest weight to communication
        client = profiles["client_facing_roles"]
        self.assertEqual(client.communication, 0.35)

    def test_weight_configuration_custom_registration(self):
        """Tests dynamic registration and constraint enforcement of custom weight profiles."""
        custom = self.weight_system.register_custom_profile(
            profile_key="qa_automation",
            profile_name="QA Automation Engineer",
            answer_relevance=0.40,
            communication=0.20,
            confidence=0.20,
            consistency=0.20,
            description="High relevance on testing frameworks and test coverage."
        )
        self.assertEqual(custom.profile_name, "QA Automation Engineer")
        fetched = self.weight_system.get_profile("qa_automation")
        self.assertEqual(fetched.answer_relevance, 0.40)

        # Invalid weights (sum != 1.0) must raise WeightConfigurationError
        with self.assertRaises(WeightConfigurationError):
            self.weight_system.register_custom_profile(
                profile_key="invalid_weights",
                profile_name="Broken Weights",
                answer_relevance=0.50,
                communication=0.50,
                confidence=0.50,
                consistency=0.50  # sum = 2.0
            )

    def test_length_normalization_bayesian_and_recency(self):
        """Tests that length normalization dampens small-sample outliers and handles variable turn lengths."""
        # 1-turn extreme outlier (100) vs 5-turn consistent performance
        score_1turn = [100.0]
        norm_1turn, meta_1 = self.normalizer.normalize_turn_scores(score_1turn, is_completed=False)
        # Bayesian prior (70.0, m=2) and completeness factor should pull 100.0 down significantly
        self.assertLess(norm_1turn, 85.0)

        # 5-turn consistent session
        scores_5turn = [88.0, 90.0, 92.0, 94.0, 96.0]
        norm_5turn, meta_5 = self.normalizer.normalize_turn_scores(scores_5turn, is_completed=True)
        # Warmup / recency should reward the upward trajectory (raw avg is 92.0)
        self.assertGreaterEqual(norm_5turn, 85.0)
        self.assertEqual(meta_5.total_turns_evaluated, 5)

    def test_explainable_scoring_contributions(self):
        """Verifies that parameter point contributions sum to composite score and percentages sum to ~100%."""
        config = HRInterviewConfig(
            candidate_id="cand_test_01",
            candidate_name="Meera Nair",
            job_role="Senior Cloud Architect",
            experience_years=8.0,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL
        )
        session = HRInterviewSession(
            session_id="sess_test_101",
            config=config,
            is_completed=True
        )

        # Provision 3 complete turns
        session.turns = [
            InterviewTurnState(
                turn_index=1,
                phase=InterviewPhase.INTRODUCTION,
                category=HRCategory.SELF_INTRODUCTION,
                question_id="INT_01",
                ai_prompt="Please introduce yourself and your cloud architecture experience.",
                candidate_response="I have 8 years of experience architecting resilient multi-region cloud infrastructures on AWS and Kubernetes. I designed systems supporting 2M daily users.",
                word_count=23,
                communication_score=CommunicationScoreBreakdown(overall_score=92.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=1,
                    confidence_score=94.0,
                    hesitation_score=95.0,
                    sentiment_score=90.0,
                    consistency_score=100.0,
                    stress_index=15.0
                )
            ),
            InterviewTurnState(
                turn_index=2,
                phase=InterviewPhase.CORE_HR,
                category=HRCategory.CAREER_JOURNEY,
                question_id="TECH_02",
                ai_prompt="Describe how you handled a critical cloud infrastructure outage.",
                candidate_response="When an availability zone suffered a network partition, our automated failover shifted traffic within 12 seconds. I coordinated post-mortem analysis with stakeholders.",
                word_count=23,
                communication_score=CommunicationScoreBreakdown(overall_score=90.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=2,
                    confidence_score=91.0,
                    hesitation_score=90.0,
                    sentiment_score=88.0,
                    consistency_score=100.0,
                    stress_index=20.0
                )
            ),
            InterviewTurnState(
                turn_index=3,
                phase=InterviewPhase.ROLE_BASED_EVALUATION,
                category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
                question_id="STAR_03",
                ai_prompt="Tell us about a technical disagreement you resolved within your engineering team.",
                candidate_response="Our team was split between Terraform and Pulumi. I organized a prototype benchmark measuring state file drift and CI/CD ergonomics. We aligned unanimously on Terraform.",
                word_count=26,
                communication_score=CommunicationScoreBreakdown(overall_score=94.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=3,
                    confidence_score=96.0,
                    hesitation_score=98.0,
                    sentiment_score=92.0,
                    consistency_score=100.0,
                    stress_index=10.0
                )
            )
        ]

        report = self.scoring_engine.evaluate_session(session)

        # Sum of weighted contributions should match composite score
        total_pts = sum(p.weighted_contribution for p in report.parameter_breakdown.values())
        self.assertAlmostEqual(total_pts, report.composite_score, delta=0.5)

        # Percentage contributions should sum to ~100%
        total_pct = sum(p.percentage_of_total for p in report.parameter_breakdown.values())
        self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

        # Candidate with strong scores should get HIRE or STRONG_HIRE
        self.assertIn(report.recommendation, [HiringRecommendation.STRONG_HIRE, HiringRecommendation.HIRE])

    def test_hiring_recommendations_thresholds(self):
        """Validates hiring recommendation tier thresholds."""
        engine = self.scoring_engine
        config = HRInterviewConfig(
            candidate_id="cand_test_02",
            candidate_name="Weak Candidate",
            job_role="Junior Developer",
            experience_years=1.0,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL
        )
        session = HRInterviewSession(
            session_id="sess_test_102",
            config=config,
            is_completed=True
        )
        # Turn with monosyllabic / evasive responses
        session.turns = [
            InterviewTurnState(
                turn_index=1,
                phase=InterviewPhase.CORE_HR,
                category=HRCategory.CAREER_JOURNEY,
                question_id="T_01",
                ai_prompt="Explain REST vs GraphQL.",
                candidate_response="I don't know.",
                word_count=3,
                communication_score=CommunicationScoreBreakdown(overall_score=25.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=1,
                    confidence_score=30.0,
                    hesitation_score=20.0,
                    sentiment_score=35.0,
                    consistency_score=50.0,
                    stress_index=80.0
                )
            )
        ]
        report = engine.evaluate_session(session)
        self.assertLess(report.composite_score, 50.0)
        self.assertEqual(report.recommendation, HiringRecommendation.NO_HIRE)

    def test_ats_json_report_serialization(self):
        """Verifies that CandidateHRScoreReport serializes to valid ATS JSON schema."""
        config = HRInterviewConfig(
            candidate_id="cand_test_03",
            candidate_name="Arjun Varma",
            job_role="Senior Backend Architect",
            experience_years=7.0,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL
        )
        session = HRInterviewSession(
            session_id="sess_test_103",
            config=config,
            is_completed=True
        )
        session.turns = [
            InterviewTurnState(
                turn_index=1,
                phase=InterviewPhase.INTRODUCTION,
                category=HRCategory.SELF_INTRODUCTION,
                question_id="I_01",
                ai_prompt="Please introduce your engineering career.",
                candidate_response="I have 7 years of experience architecting distributed transaction systems and microservices at scale.",
                word_count=14,
                communication_score=CommunicationScoreBreakdown(overall_score=90.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=1,
                    confidence_score=92.0,
                    hesitation_score=95.0,
                    sentiment_score=88.0,
                    consistency_score=100.0,
                    stress_index=15.0
                )
            )
        ]
        report = self.scoring_engine.evaluate_session(session)
        json_output = HRScoreReportFormatter.to_ats_json(report)
        parsed = json.loads(json_output)

        self.assertIn("candidate_id", parsed)
        self.assertIn("composite_score", parsed)
        self.assertIn("recommendation", parsed)
        self.assertIn("parameter_breakdown", parsed)
        self.assertIn("length_normalization", parsed)
        self.assertIn("turn_score_trajectory", parsed)
        self.assertIn("key_strengths", parsed)

    def test_markdown_report_formatting(self):
        """Verifies that HRScoreReportFormatter produces formatted markdown containing all required tables."""
        config = HRInterviewConfig(
            candidate_id="cand_test_04",
            candidate_name="Priya Sharma",
            job_role="Staff Systems Engineer",
            experience_years=9.0,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL
        )
        session = HRInterviewSession(
            session_id="sess_test_104",
            config=config,
            is_completed=True
        )
        session.turns = [
            InterviewTurnState(
                turn_index=1,
                phase=InterviewPhase.INTRODUCTION,
                category=HRCategory.SELF_INTRODUCTION,
                question_id="I_01",
                ai_prompt="Introduce yourself.",
                candidate_response="I lead infrastructure engineering at fintech firm scaling to 50,000 QPS with sub-20ms p99 latency.",
                word_count=16,
                communication_score=CommunicationScoreBreakdown(overall_score=95.0),
                confidence_evaluation=TurnConfidenceBreakdown(
                    turn_index=3,
                    confidence_score=96.0,
                    hesitation_score=98.0,
                    sentiment_score=94.0,
                    consistency_score=100.0,
                    stress_index=10.0
                )
            )
        ]
        report = self.scoring_engine.evaluate_session(session)
        md = HRScoreReportFormatter.to_markdown_summary(report)

        self.assertIn("# Zecpath-AI Candidate HR Interview Score Report", md)
        self.assertIn("Four Core Scoring Parameters Breakdown", md)
        self.assertIn("Sub-Dimensional Skill Ratings", md)
        self.assertIn("Turn-by-Turn Score Trajectory", md)
        self.assertIn("Recruiter Actionable Feedback", md)

    def test_flow_engine_dossier_integration(self):
        """Asserts that HRInterviewFlowEngine.export_session_dossier() embeds the Day 37 hr_score_report."""
        engine = HRInterviewFlowEngine()
        config = HRInterviewConfig.auto_classify(
            candidate_id="cand_test_05",
            candidate_name="Rohit Verma",
            job_role="DevOps Specialist",
            experience_years=4.5
        )
        session = engine.start_session(config)
        prompt1 = session.turns[0].ai_prompt
        
        # Turn 1
        resp1 = "I have 4.5 years of experience automating CI/CD pipelines and managing Kubernetes clusters on Google Cloud."
        prompt2 = engine.process_turn(session.session_id, resp1, response_time_seconds=1.4)
        
        # Export dossier
        dossier = engine.export_session_dossier(session.session_id)
        self.assertIn("hr_score_report", dossier)
        report_data = dossier["hr_score_report"]
        self.assertIn("composite_score", report_data)
        self.assertIn("parameter_breakdown", report_data)
        self.assertIn("recommendation", report_data)


if __name__ == "__main__":
    unittest.main()
