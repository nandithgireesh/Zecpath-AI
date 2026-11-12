import unittest
from screening_ai.scoring_models import (
    ScoringDimension,
    RecommendationTier,
    ScoreGrade,
    QuestionScoreBreakdown,
    FinalScreeningScoreObject,
)
from screening_ai.scoring_engine import ScreeningScoringEngine
from screening_ai.intent_models import StructuredAnswerObject, CandidateIntent


class TestScreeningScoringEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ScreeningScoringEngine()

    # -------------------------------------------------------------
    # 1. Clarity Scoring Tests
    # -------------------------------------------------------------
    def test_clarity_scoring_articulate(self):
        """Articulate, direct answer should achieve high clarity score."""
        res = self.engine.score_question_answer(
            raw_text="I have 5 years of experience building Python and FastAPI microservices.",
            question_category="Experience",
        )
        self.assertGreaterEqual(res.clarity_score, 90.0)
        self.assertIn("Articulate and direct communication", res.strengths)

    def test_clarity_scoring_vague(self):
        """Vague, non-committal answer should be penalized on clarity."""
        res = self.engine.score_question_answer(
            raw_text="Well, it depends on many things, a little bit of everything as per company norms.",
            question_category="Experience",
        )
        self.assertLessEqual(res.clarity_score, 70.0)
        self.assertTrue(any("Vague" in p for p in res.penalties))

    # -------------------------------------------------------------
    # 2. Relevance Scoring Tests
    # -------------------------------------------------------------
    def test_relevance_scoring_on_topic(self):
        """On-topic answer should score high on relevance."""
        res = self.engine.score_question_answer(
            raw_text="I work with Python, PostgreSQL, and Docker daily.",
            question_category="Technical Skills",
        )
        self.assertGreaterEqual(res.relevance_score, 90.0)

    def test_relevance_scoring_off_topic(self):
        """Off-topic answer (weather, joke, etc.) should be severely penalized."""
        res = self.engine.score_question_answer(
            raw_text="The weather in Bangalore is really pleasant and sunny today.",
            question_category="Technical Skills",
        )
        self.assertLessEqual(res.relevance_score, 30.0)
        self.assertTrue(any("off-topic" in w.lower() for w in res.weaknesses))

    # -------------------------------------------------------------
    # 3. Completeness Scoring Tests
    # -------------------------------------------------------------
    def test_completeness_scoring_full_salary(self):
        """Providing concrete expected CTC should yield high completeness."""
        res = self.engine.score_question_answer(
            raw_text="My current CTC is 14 LPA and I am looking for 18.5 LPA negotiable.",
            question_category="Salary Expectation",
        )
        self.assertGreaterEqual(res.completeness_score, 90.0)
        self.assertTrue(any("18.5 LPA" in s for s in res.strengths))

    def test_completeness_scoring_missing_salary_number(self):
        """Vague salary answer without numerical LPA should be penalized on completeness."""
        res = self.engine.score_question_answer(
            raw_text="I expect a competitive package according to standard company budget.",
            question_category="Salary Expectation",
        )
        self.assertLessEqual(res.completeness_score, 70.0)
        self.assertTrue(any("expected_ctc_lpa" in p for p in res.penalties))

    def test_completeness_scoring_technical_skills(self):
        """Specifying confirmed technical skills achieves high completeness."""
        res = self.engine.score_question_answer(
            raw_text="I am an expert in Python, FastAPI, and PostgreSQL.",
            question_category="Technical Skills",
        )
        self.assertGreaterEqual(res.completeness_score, 90.0)
        self.assertTrue(any("Confirmed technical skills" in s for s in res.strengths))

    def test_completeness_scoring_notice_period(self):
        """Specifying exact notice days achieves high completeness."""
        res = self.engine.score_question_answer(
            raw_text="My official notice period is 30 days and I can buy out.",
            question_category="Notice Period",
        )
        self.assertGreaterEqual(res.completeness_score, 90.0)
        self.assertTrue(any("30 days" in s for s in res.strengths))

    # -------------------------------------------------------------
    # 4. Consistency Scoring Tests
    # -------------------------------------------------------------
    def test_cross_turn_consistency_flawless(self):
        """Consistent answers across turns should receive a perfect consistency score."""
        ans1 = self.engine.answer_engine.understand_answer(
            raw_text="I have 5 years of experience in Python and FastAPI backend development.",
            question_category="Experience",
        )
        ans2 = self.engine.answer_engine.understand_answer(
            raw_text="I also work with PostgreSQL and Docker.",
            question_category="Technical Skills",
        )
        ans3 = self.engine.answer_engine.understand_answer(
            raw_text="My notice period is 30 days and expected CTC is 20 LPA.",
            question_category="Salary Expectation",
        )

        consistency, contradictions, audit = self.engine.audit_session_consistency([ans1, ans2, ans3])
        self.assertEqual(consistency, 100.0)
        self.assertEqual(len(contradictions), 0)
        self.assertTrue(audit["is_flawless"])

    def test_cross_turn_consistency_skill_flip_flop(self):
        """Confirming a skill in Turn 1 but declining it in Turn 2 triggers a contradiction."""
        ans1 = self.engine.answer_engine.understand_answer(
            raw_text="I have extensive experience working with Kubernetes and Docker.",
            question_category="Technical Skills",
        )
        ans2 = self.engine.answer_engine.understand_answer(
            raw_text="I have never worked with Kubernetes or cloud infrastructure.",
            question_category="Technical Skills",
        )

        consistency, contradictions, audit = self.engine.audit_session_consistency([ans1, ans2])
        self.assertLess(consistency, 100.0)
        self.assertGreaterEqual(len(contradictions), 1)
        self.assertTrue(any("kubernetes" in c.lower() for c in contradictions))

    def test_cross_turn_consistency_experience_drift(self):
        """Claiming 6 years in turn 1 and 2 years in turn 2 triggers tenure drift."""
        ans1 = self.engine.answer_engine.understand_answer(
            raw_text="I have over 6 years of experience in software engineering.",
            question_category="Experience",
        )
        ans2 = self.engine.answer_engine.understand_answer(
            raw_text="I have 2 years of experience building machine learning pipelines.",
            question_category="Experience",
        )

        consistency, contradictions, audit = self.engine.audit_session_consistency([ans1, ans2])
        self.assertLess(consistency, 100.0)
        self.assertTrue(any("Tenure Inconsistency" in c for c in contradictions))

    # -------------------------------------------------------------
    # 5. Score Grade & Recommendation Tier Derivation
    # -------------------------------------------------------------
    def test_score_grade_derivation(self):
        """Verifies grade thresholds."""
        self.assertEqual(self.engine._derive_score_grade(92.0), ScoreGrade.EXCELLENT)
        self.assertEqual(self.engine._derive_score_grade(75.0), ScoreGrade.STRONG)
        self.assertEqual(self.engine._derive_score_grade(62.0), ScoreGrade.MODERATE)
        self.assertEqual(self.engine._derive_score_grade(45.0), ScoreGrade.POOR)
        self.assertEqual(self.engine._derive_score_grade(25.0), ScoreGrade.UNSATISFACTORY)

    def test_recommendation_tier_derivation(self):
        """Verifies recommendation tier decision boundaries."""
        # High score without contradictions -> STRONGLY_RECOMMENDED
        tier1 = self.engine._derive_recommendation_tier(88.0, 95.0, [])
        self.assertEqual(tier1, RecommendationTier.STRONGLY_RECOMMENDED)

        # High score but with contradictions -> RECOMMENDED
        tier2 = self.engine._derive_recommendation_tier(88.0, 75.0, ["Contradiction"])
        self.assertEqual(tier2, RecommendationTier.RECOMMENDED)

        # Moderate score -> RECOMMENDED_WITH_RESERVATIONS
        tier3 = self.engine._derive_recommendation_tier(60.0, 70.0, [])
        self.assertEqual(tier3, RecommendationTier.RECOMMENDED_WITH_RESERVATIONS)

        # Low score -> NOT_RECOMMENDED
        tier4 = self.engine._derive_recommendation_tier(42.0, 60.0, [])
        self.assertEqual(tier4, RecommendationTier.NOT_RECOMMENDED)

    # -------------------------------------------------------------
    # 6. Session Aggregation & Explainable Reporting
    # -------------------------------------------------------------
    def test_session_aggregation_and_explainability(self):
        """Tests complete end-to-end multi-turn session evaluation."""
        turn1_raw = "I have 4.5 years of experience building Python and FastAPI microservices."
        turn2_raw = "I specialize in PostgreSQL, Redis, and Docker, but I haven't worked with Kubernetes."
        turn3_raw = "My current CTC is 12 LPA, expecting 16 LPA negotiable. Notice period is 15 days."

        ans1 = self.engine.answer_engine.understand_answer(turn1_raw, question_category="Experience")
        ans2 = self.engine.answer_engine.understand_answer(turn2_raw, question_category="Technical Skills")
        ans3 = self.engine.answer_engine.understand_answer(turn3_raw, question_category="Salary Expectation")

        q1 = self.engine.score_question_answer(turn1_raw, question_category="Experience", structured_answer=ans1)
        q2 = self.engine.score_question_answer(turn2_raw, question_category="Technical Skills", structured_answer=ans2)
        q3 = self.engine.score_question_answer(turn3_raw, question_category="Salary Expectation", structured_answer=ans3)

        final_obj = self.engine.aggregate_screening_session(
            questions_breakdowns=[q1, q2, q3],
            structured_answers=[ans1, ans2, ans3],
            candidate_id="CAND_TEST_99",
            call_id="CALL_TEST_99",
            job_id="JOB_TEST_99",
        )

        self.assertIsInstance(final_obj, FinalScreeningScoreObject)
        self.assertGreater(final_obj.overall_score, 70.0)
        self.assertIn(final_obj.recommendation_tier, [RecommendationTier.STRONGLY_RECOMMENDED, RecommendationTier.RECOMMENDED])
        self.assertIn("Technical Skills", final_obj.category_breakdowns)
        self.assertIn("Experience", final_obj.category_breakdowns)
        self.assertIn("Salary Expectation", final_obj.category_breakdowns)

        # Verify explainability report
        report = final_obj.explainability
        self.assertTrue(len(report.executive_summary) > 20)
        self.assertTrue(len(report.key_strengths) > 0)
        self.assertTrue(len(report.recommended_interview_probes) > 0)


if __name__ == "__main__":
    unittest.main()
