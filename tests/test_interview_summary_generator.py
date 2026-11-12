"""
Unit Tests for Day 39: AI Interview Summary Generator
=====================================================
Validates:
1. Cross-turn contradiction detection (Solo vs Team claim)
2. Verbal-affect discordance detection (Extreme certainty vs high stress)
3. Competency-performance gap detection (Senior claim vs logical fallacy)
4. Factual experience mismatch detection (Resume vs spoken years)
5. Cultural fit scoring across 5 dimensions (Ownership, Teamwork, Customer, Adaptability, Ethics)
6. Cultural fit penalty under blame deflection
7. Overall HR performance synthesis and calibrated role leveling
8. Critical inconsistency score deduction
9. Extraction of strengths and developmental weaknesses
10. Natural language recruiter dossier generation
11. Enterprise ATS JSON schema serialization and compliance
12. Markdown recruiter debrief document formatting
"""

import unittest
from datetime import datetime

from interview_ai.summary_models import (
    CandidateInterviewSummary,
    InconsistencyType,
    InconsistencySeverity,
    CulturalFitDimension,
)
from interview_ai.inconsistency_detector import InconsistencyDetector
from interview_ai.interview_summary_generator import InterviewSummaryGenerator
from interview_ai.hr_scoring_models import (
    CandidateHRScoreReport,
    HiringRecommendation,
    ParameterContribution,
    ScoringParameter,
    LengthNormalizationMetadata,
)


class TestInterviewSummaryGenerator(unittest.TestCase):
    """Test suite for Day 39 interview summary generator and inconsistency detection."""

    def setUp(self):
        self.detector = InconsistencyDetector()
        self.generator = InterviewSummaryGenerator()

        # Mock standard score report
        self.mock_score_report = CandidateHRScoreReport(
            candidate_id="CAND-TEST-01",
            candidate_name="Alice Smith",
            job_role="Senior Distributed Systems Engineer",
            experience_years=7.0,
            session_id="SESS-2026-TEST",
            evaluation_date=datetime.now().isoformat(),
            weight_profile_used="technical_roles",
            composite_score=86.5,
            recommendation=HiringRecommendation.STRONG_HIRE,
            executive_summary="Candidate demonstrates high technical competence.",
            parameter_breakdown={
                "answer_relevance": ParameterContribution(
                    parameter=ScoringParameter.ANSWER_RELEVANCE,
                    display_name="Answer Relevance",
                    raw_score=88.0,
                    normalized_score=88.0,
                    weight=0.30,
                    weighted_contribution=26.4,
                    percentage_of_total=30.0,
                    diagnostic_summary="Direct and relevant answers.",
                ),
                "communication_score": ParameterContribution(
                    parameter=ScoringParameter.COMMUNICATION,
                    display_name="Communication Score",
                    raw_score=85.0,
                    normalized_score=85.0,
                    weight=0.25,
                    weighted_contribution=21.25,
                    percentage_of_total=25.0,
                    diagnostic_summary="Fluent and articulate.",
                ),
                "confidence_score": ParameterContribution(
                    parameter=ScoringParameter.CONFIDENCE,
                    display_name="Confidence Score",
                    raw_score=84.0,
                    normalized_score=84.0,
                    weight=0.25,
                    weighted_contribution=21.0,
                    percentage_of_total=25.0,
                    diagnostic_summary="High composure.",
                ),
                "consistency": ParameterContribution(
                    parameter=ScoringParameter.CONSISTENCY,
                    display_name="Consistency",
                    raw_score=90.0,
                    normalized_score=90.0,
                    weight=0.20,
                    weighted_contribution=18.0,
                    percentage_of_total=20.0,
                    diagnostic_summary="Consistent responses.",
                ),
            },
            length_normalization=LengthNormalizationMetadata(
                total_turns_evaluated=5,
                expected_standard_turns=5,
                raw_average_score=86.5,
                normalized_score=86.5,
                prior_mean=70.0,
                prior_weight_m=2.0,
                recency_weighted_average=86.5,
                session_completeness_factor=1.0,
                normalization_adjustment=0.0,
            ),
            communication_subdimensions={"fluency": 85.0, "clarity": 88.0, "filler_control": 92.0},
            behavioral_subdimensions={"hesitation_control": 88.0, "stress_resilience": 85.0},
            turn_score_trajectory=[],
            key_strengths=["Exceptional technical depth."],
            risk_flags=[],
            recommended_next_steps=["Proceed to executive debrief."],
        )

    def test_inconsistency_solo_vs_team_contradiction(self):
        """Validates detection of solo architectural claims contradicted by team dependence."""
        transcript = [
            {"turn_index": 1, "response": "I single-handedly designed the distributed cache architecture from scratch."},
            {"turn_index": 3, "response": "My tech lead made all decisions on database schema, I only wrote tests."},
        ]
        flags = self.detector.detect_inconsistencies(transcript_turns=transcript)
        self.assertTrue(any(f.inconsistency_type == InconsistencyType.CROSS_TURN_CONTRADICTION for f in flags))
        crit_flag = next(f for f in flags if f.inconsistency_type == InconsistencyType.CROSS_TURN_CONTRADICTION)
        self.assertTrue(any(w in crit_flag.claimed_statement.lower() for w in ["solo", "single-handedly"]))

    def test_inconsistency_verbal_affect_discordance(self):
        """Validates detection of extreme verbal certainty while physiological stress spikes."""
        transcript = [
            {"turn_index": 2, "response": "I completely and absolutely understand Paxos consensus inside out, it's 100% trivial."}
        ]
        stress_signals = [
            {"turn_index": 2, "stress_index": 78.5, "hesitation_latency": 3.8, "filler_percentage": 9.2}
        ]
        flags = self.detector.detect_inconsistencies(
            transcript_turns=transcript,
            stress_signals=stress_signals,
        )
        self.assertTrue(any(f.inconsistency_type == InconsistencyType.VERBAL_AFFECT_DISCORDANCE for f in flags))
        discord_flag = next(f for f in flags if f.inconsistency_type == InconsistencyType.VERBAL_AFFECT_DISCORDANCE)
        self.assertEqual(discord_flag.severity, InconsistencySeverity.MODERATE)

    def test_inconsistency_senior_fallacy_gap(self):
        """Validates competency gap when a senior applicant demonstrates fallacious reasoning."""
        metadata = {"job_role": "Lead Systems Architect", "experience_years": 8.0}
        fallacies = [
            {"fallacy_type": "FALSE_DILEMMA", "explanation": "Framed migration as an all-or-nothing binary."}
        ]
        flags = self.detector.detect_inconsistencies(
            transcript_turns=[],
            candidate_metadata=metadata,
            fallacy_flags=fallacies,
        )
        self.assertTrue(any(f.inconsistency_type == InconsistencyType.COMPETENCY_PERFORMANCE_GAP for f in flags))

    def test_inconsistency_factual_experience_mismatch(self):
        """Validates factual gap between resume years and spoken tenure."""
        metadata = {"experience_years": 8.0}
        transcript = [
            {"turn_index": 1, "response": "I have been working for 3 years in industry since graduation."}
        ]
        flags = self.detector.detect_inconsistencies(
            transcript_turns=transcript,
            candidate_metadata=metadata,
        )
        self.assertTrue(any(f.inconsistency_type == InconsistencyType.FACTUAL_EXPERIENCE_MISMATCH for f in flags))

    def test_cultural_fit_exemplary_ownership(self):
        """Validates exemplary ownership score when candidate demonstrates blameless post-mortem."""
        transcript = [
            {"turn_index": 1, "response": "I took ownership of the incident and ran a blameless post-mortem to isolate the root cause."}
        ]
        cultural_fit = self.generator._evaluate_cultural_fit(
            transcript_turns=transcript,
            aptitude_evaluation=None,
            fallacies=[],
        )
        ownership = next(c for c in cultural_fit if c.dimension == CulturalFitDimension.OWNERSHIP_AND_ACCOUNTABILITY)
        self.assertEqual(ownership.alignment_level, "EXEMPLARY")
        self.assertGreaterEqual(ownership.score, 88.0)

    def test_cultural_fit_blame_deflection_penalty(self):
        """Validates heavy penalty on ownership when blame deflection fallacy is present."""
        cultural_fit = self.generator._evaluate_cultural_fit(
            transcript_turns=[],
            aptitude_evaluation=None,
            fallacies=[{"fallacy_type": "BLAME_DEFLECTION", "explanation": "Blamed management"}],
        )
        ownership = next(c for c in cultural_fit if c.dimension == CulturalFitDimension.OWNERSHIP_AND_ACCOUNTABILITY)
        self.assertEqual(ownership.alignment_level, "WEAK")
        self.assertLessEqual(ownership.score, 40.0)

    def test_overall_performance_synthesis_strong_hire(self):
        """Validates Strong Hire recommendation for high performing candidate with zero contradictions."""
        summary = self.generator.generate_summary(
            candidate_metadata={
                "candidate_id": "CAND-01",
                "candidate_name": "David Miller",
                "job_role": "Staff Platform Architect",
                "experience_years": 8.0,
            },
            transcript_turns=[
                {"turn_index": 1, "response": "I took ownership and led our cross-functional team with blameless post-mortems."}
            ],
            score_report=self.mock_score_report,
            aptitude_evaluation={
                "composite_aptitude_score": 88.0,
                "scores": {"logical_reasoning": 90.0, "problem_solving_clarity": 88.0},
                "framework_adherence_percent": 100.0,
            },
            communication_telemetry={"clarity": 88.0, "filler_percentage": 1.5},
            stress_signals=[{"stress_index": 22.0}],
            fallacy_flags=[],
        )
        self.assertEqual(summary.overall_performance.recommendation, HiringRecommendation.STRONG_HIRE)
        self.assertGreaterEqual(summary.overall_performance.composite_score, 85.0)

    def test_overall_performance_inconsistency_penalty(self):
        """Validates score penalty and rejection/degradation when critical inconsistencies exist."""
        summary = self.generator.generate_summary(
            candidate_metadata={
                "candidate_id": "CAND-02",
                "candidate_name": "Bob Contradictor",
                "job_role": "Senior Engineer",
                "experience_years": 6.0,
            },
            transcript_turns=[
                {"turn_index": 1, "response": "I single-handedly wrote the entire platform alone."},
                {"turn_index": 2, "response": "My tech lead made all decisions, I only followed orders."},
            ],
            score_report=self.mock_score_report,
            aptitude_evaluation={"composite_aptitude_score": 70.0},
            fallacy_flags=[{"fallacy_type": "BLAME_DEFLECTION", "explanation": "Blamed the QA team."}],
        )
        # Should be penalized due to critical inconsistency and blame deflection
        self.assertIn(
            summary.overall_performance.recommendation,
            [HiringRecommendation.LEAN_HIRE, HiringRecommendation.LEAN_NO_HIRE, HiringRecommendation.NO_HIRE],
        )
        self.assertGreaterEqual(len(summary.inconsistencies), 1)

    def test_strengths_weaknesses_extraction(self):
        """Validates proper extraction of strengths and developmental areas."""
        strengths, weaknesses = self.generator._extract_strengths_and_weaknesses(
            score_report=self.mock_score_report,
            aptitude_evaluation={
                "scores": {"logical_reasoning": 85.0, "problem_solving_clarity": 85.0},
                "framework_adherence_percent": 95.0,
            },
            communication_telemetry={"clarity": 85.0, "filler_percentage": 6.2},
            stress_signals=[{"stress_index": 28.0}],
            inconsistencies=[],
        )
        self.assertTrue(any("Logical Deduction" in s for s in strengths))
        self.assertTrue(any("Filler Word" in w for w in weaknesses))

    def test_natural_language_dossier_generation(self):
        """Validates generation of natural-language briefing sections."""
        summary = self.generator.generate_summary(
            candidate_metadata={
                "candidate_id": "CAND-03",
                "candidate_name": "Carol Danvers",
                "job_role": "Backend Lead",
                "experience_years": 5.0,
            },
            transcript_turns=[
                {"turn_index": 1, "response": "We optimized the database throughput using connection pools and Kafka."}
            ],
            score_report=self.mock_score_report,
        )
        nlg = summary.natural_language_report
        self.assertTrue(len(nlg.executive_overview) > 50)
        self.assertTrue(len(nlg.communication_persona) > 50)
        self.assertTrue(len(nlg.behavioral_and_cultural_fit) > 50)
        self.assertTrue(len(nlg.cognitive_and_technical_maturity) > 50)
        self.assertTrue(len(nlg.hiring_manager_action_plan) > 30)
        self.assertGreaterEqual(len(nlg.targeted_interview_probes), 1)

    def test_ats_json_serialization(self):
        """Validates that summary serializes into valid ATS-compliant JSON."""
        summary = self.generator.generate_summary(
            candidate_metadata={"candidate_id": "CAND-04", "candidate_name": "Dan Evans", "job_role": "SRE", "experience_years": 4.0},
            transcript_turns=[],
            score_report=self.mock_score_report,
        )
        json_str = self.generator.to_ats_json(summary)
        self.assertIn('"summary_id"', json_str)
        self.assertIn('"overall_performance"', json_str)
        self.assertIn('"candidate_strengths"', json_str)
        self.assertIn('"cultural_fit_indicators"', json_str)

    def test_recruiter_markdown_formatting(self):
        """Validates formatting of recruiter markdown dossier."""
        summary = self.generator.generate_summary(
            candidate_metadata={"candidate_id": "CAND-05", "candidate_name": "Eva Green", "job_role": "ML Engineer", "experience_years": 3.0},
            transcript_turns=[],
            score_report=self.mock_score_report,
        )
        md = self.generator.to_recruiter_markdown(summary)
        self.assertIn("# Zecpath-AI Executive Interview Summary Dossier", md)
        self.assertIn("## 1. Executive Hiring Verdict & Performance Synthesis", md)
        self.assertIn("## 3. Cultural Fit & Organizational Alignment", md)
        self.assertIn("## 5. Recruiter Natural-Language Narrative Dossier", md)


if __name__ == "__main__":
    unittest.main()
