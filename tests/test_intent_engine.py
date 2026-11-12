import unittest
from screening_ai.intent_models import (
    CandidateIntent,
    ProficiencyLevel,
    StructuredAnswerObject,
)
from screening_ai.intent_classifier import CandidateIntentClassifier
from screening_ai.answer_understanding import AnswerUnderstandingEngine


class TestAnswerIntentAndUnderstanding(unittest.TestCase):

    def setUp(self):
        self.classifier = CandidateIntentClassifier()
        self.engine = AnswerUnderstandingEngine()

    # -------------------------------------------------------------
    # 1. Intent Classification Tests
    # -------------------------------------------------------------
    def test_intent_providing_experience(self):
        text = "I have 4 years of experience as a machine learning engineer building computer vision systems."
        intent, conf, _ = self.classifier.classify_intent(text, question_category="Experience")
        self.assertEqual(intent, CandidateIntent.PROVIDING_EXPERIENCE)
        self.assertGreaterEqual(conf, 0.65)

    def test_intent_confirming_skill(self):
        text = "Yes, I have hands-on experience in PyTorch, Docker, and FastAPI."
        intent, conf, _ = self.classifier.classify_intent(text, question_category="Technical Skills")
        self.assertEqual(intent, CandidateIntent.CONFIRMING_SKILL)
        self.assertGreaterEqual(conf, 0.70)

    def test_intent_declining_skill(self):
        text = "I haven't worked with Kubernetes, and I have zero experience with AWS cloud."
        intent, conf, _ = self.classifier.classify_intent(text, question_category="Technical Skills")
        self.assertEqual(intent, CandidateIntent.DECLINING_SKILL)
        self.assertGreaterEqual(conf, 0.80)

    def test_intent_stating_salary(self):
        text = "My current CTC is 12 LPA and I am expecting around 16 LPA."
        intent, conf, _ = self.classifier.classify_intent(text, question_category="Salary Expectation")
        self.assertEqual(intent, CandidateIntent.STATING_SALARY)
        self.assertGreaterEqual(conf, 0.75)

    def test_intent_stating_availability(self):
        text = "My official notice period is 30 days, but I can negotiate a buyout."
        intent, conf, _ = self.classifier.classify_intent(text, question_category="Notice Period")
        self.assertEqual(intent, CandidateIntent.STATING_AVAILABILITY)
        self.assertGreaterEqual(conf, 0.75)

    def test_intent_asking_clarification(self):
        text = "Sorry, could you repeat that? What do you mean by asynchronous queues?"
        intent, conf, _ = self.classifier.classify_intent(text)
        self.assertEqual(intent, CandidateIntent.ASKING_CLARIFICATION)
        self.assertGreaterEqual(conf, 0.85)

    def test_intent_off_topic(self):
        text = "What is the weather like today? Can I talk to a real human recruiter?"
        intent, conf, _ = self.classifier.classify_intent(text, question_prompt="Tell me about your Python experience.")
        self.assertEqual(intent, CandidateIntent.OFF_TOPIC)
        self.assertGreaterEqual(conf, 0.85)

    def test_intent_vague_answer(self):
        text = "I know a little bit of everything, it depends on what the team wants."
        intent, conf, _ = self.classifier.classify_intent(text)
        self.assertEqual(intent, CandidateIntent.VAGUE_ANSWER)
        self.assertGreaterEqual(conf, 0.80)

    # -------------------------------------------------------------
    # 2. Entity Extraction: Skills & Proficiency
    # -------------------------------------------------------------
    def test_extract_skills_proficiency_and_decline(self):
        text = "I am an expert in Python and have hands-on experience in PyTorch, but I haven't worked with Kubernetes."
        skills = self.engine.extract_skills(text)
        skill_names = [s.skill for s in skills]

        self.assertIn("python", skill_names)
        self.assertIn("pytorch", skill_names)
        self.assertIn("kubernetes", skill_names)

        # Python proficiency
        py_skill = next(s for s in skills if s.skill == "python")
        self.assertTrue(py_skill.is_confirmed)
        self.assertEqual(py_skill.proficiency, ProficiencyLevel.ADVANCED)
        self.assertEqual(py_skill.sentiment, "positive")

        # PyTorch proficiency
        torch_skill = next(s for s in skills if s.skill == "pytorch")
        self.assertTrue(torch_skill.is_confirmed)
        self.assertEqual(torch_skill.proficiency, ProficiencyLevel.INTERMEDIATE)

        # Kubernetes decline
        k8s_skill = next(s for s in skills if s.skill == "kubernetes")
        self.assertFalse(k8s_skill.is_confirmed)
        self.assertEqual(k8s_skill.sentiment, "negative")

    # -------------------------------------------------------------
    # 3. Entity Extraction: Experience
    # -------------------------------------------------------------
    def test_extract_experience_details(self):
        text = "I have four years of experience as a Backend Engineer in Fintech using Python and PostgreSQL."
        exp = self.engine.extract_experience(text)
        self.assertIsNotNone(exp)
        self.assertEqual(exp.total_years, 4.0)
        self.assertEqual(exp.primary_role, "Backend Engineer")
        self.assertIn("Fintech", exp.domains)
        self.assertIn("python", exp.key_technologies)
        self.assertIn("postgresql", exp.key_technologies)

    # -------------------------------------------------------------
    # 4. Entity Extraction: Availability
    # -------------------------------------------------------------
    def test_extract_availability_immediate(self):
        text = "I am ready to join immediately, currently not employed."
        avail = self.engine.extract_availability(text)
        self.assertIsNotNone(avail)
        self.assertTrue(avail.is_immediate_joiner)
        self.assertEqual(avail.notice_period_days, 0)

    def test_extract_availability_notice_period(self):
        text = "I have a 60 days notice period, but company buyout is possible."
        avail = self.engine.extract_availability(text)
        self.assertIsNotNone(avail)
        self.assertEqual(avail.notice_period_days, 60)
        self.assertTrue(avail.can_buyout_notice)

    # -------------------------------------------------------------
    # 5. Entity Extraction: Salary
    # -------------------------------------------------------------
    def test_extract_salary_current_and_expected(self):
        text = "Currently earning 12 LPA and my expected CTC is 16.5 LPA, negotiable."
        sal = self.engine.extract_salary(text)
        self.assertIsNotNone(sal)
        self.assertEqual(sal.current_ctc_lpa, 12.0)
        self.assertEqual(sal.expected_ctc_lpa, 16.5)
        self.assertTrue(sal.is_negotiable)

    # -------------------------------------------------------------
    # 6. Quality & Vagueness Evaluation
    # -------------------------------------------------------------
    def test_quality_evaluation_off_topic(self):
        text = "Can you tell me a funny joke about cricket?"
        quality = self.engine.evaluate_quality(text, primary_intent=CandidateIntent.OFF_TOPIC)
        self.assertTrue(quality.is_off_topic)
        self.assertLess(quality.relevance_score, 0.4)
        self.assertTrue(quality.follow_up_needed)

    def test_quality_evaluation_missing_salary_slot(self):
        text = "I am looking for an attractive salary package as per industry standard."
        quality = self.engine.evaluate_quality(text, question_category="Salary Expectation", primary_intent=CandidateIntent.STATING_SALARY)
        self.assertTrue(quality.is_vague)
        self.assertIn("expected_ctc_lpa", quality.missing_slots)
        self.assertTrue(quality.follow_up_needed)

    # -------------------------------------------------------------
    # 7. End-to-End StructuredAnswerObject Compilation
    # -------------------------------------------------------------
    def test_full_answer_understanding_pipeline(self):
        text = "I have 5 years experience in Python and Docker as a Software Engineer. My current CTC is 15 LPA, expecting 20 LPA, and notice period is 30 days."
        ans = self.engine.understand_answer(
            raw_text=text,
            question_category="Experience",
            turn_id="TURN_01",
            question_id="EXP_01",
        )
        self.assertIsInstance(ans, StructuredAnswerObject)
        self.assertEqual(ans.turn_id, "TURN_01")
        self.assertEqual(ans.question_id, "EXP_01")
        self.assertIsNotNone(ans.experience)
        self.assertEqual(ans.experience.total_years, 5.0)
        self.assertIsNotNone(ans.salary)
        self.assertEqual(ans.salary.expected_ctc_lpa, 20.0)
        self.assertIsNotNone(ans.availability)
        self.assertEqual(ans.availability.notice_period_days, 30)
        self.assertFalse(ans.quality.is_off_topic)


if __name__ == "__main__":
    unittest.main()
