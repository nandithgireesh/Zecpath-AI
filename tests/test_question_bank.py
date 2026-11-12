import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screening_ai.question_bank import ScreeningQuestionBank
from screening_ai.question_models import (
    QuestionCategory,
    AnswerType,
    ImportanceLevel,
)


class TestScreeningQuestionBank(unittest.TestCase):
    """
    Day 22 - Unit tests for HR Screening Question Bank dataset and manager.
    """

    @classmethod
    def setUpClass(cls):
        cls.bank = ScreeningQuestionBank()

    def test_dataset_loaded_and_categories_covered(self):
        """Verify all 7 mandatory HR categories are covered in the question bank."""
        expected_categories = {
            "Introduction",
            "Education",
            "Experience",
            "Skills",
            "Location",
            "Salary",
            "Notice period",
        }
        summary = self.bank.get_dataset_summary()
        self.assertGreater(summary["total_questions"], 0)

        found_categories = set(summary["categories_covered"])
        self.assertTrue(
            expected_categories.issubset(found_categories),
            f"Missing categories: {expected_categories - found_categories}",
        )

    def test_question_metadata_attributes(self):
        """Verify all questions have required metadata: answer type, mandatory flag, importance."""
        for q_id, q in self.bank.questions.items():
            self.assertIsNotNone(q.id)
            self.assertIsInstance(q.category, QuestionCategory)
            self.assertIsInstance(q.expected_answer_type, AnswerType)
            self.assertIsInstance(q.scoring_importance, ImportanceLevel)
            self.assertIsInstance(q.is_mandatory, bool)
            self.assertGreater(len(q.template), 5)

    def test_filter_by_role_and_category(self):
        """Test filtering questions by specific technical role and category."""
        ml_skill_questions = self.bank.filter_questions(
            role="Machine Learning Engineer",
            category=QuestionCategory.SKILLS,
            include_general=False,
        )
        self.assertGreaterEqual(len(ml_skill_questions), 1)
        for q in ml_skill_questions:
            self.assertEqual(q.category, QuestionCategory.SKILLS)
            self.assertIn("machine learning", q.role.lower())

        mern_skill_questions = self.bank.filter_questions(
            role="MERN Stack Developer",
            category=QuestionCategory.SKILLS,
            include_general=False,
        )
        self.assertGreaterEqual(len(mern_skill_questions), 1)
        for q in mern_skill_questions:
            self.assertEqual(q.category, QuestionCategory.SKILLS)
            self.assertIn("mern", q.role.lower())

    def test_filter_by_mandatory_and_importance(self):
        """Test filtering by mandatory flag and minimum importance level."""
        mandatory_qs = self.bank.filter_questions(mandatory_only=True)
        self.assertGreater(len(mandatory_qs), 0)
        for q in mandatory_qs:
            self.assertTrue(q.is_mandatory)

        critical_qs = self.bank.filter_questions(min_importance=ImportanceLevel.CRITICAL)
        self.assertGreater(len(critical_qs), 0)
        for q in critical_qs:
            self.assertEqual(q.scoring_importance, ImportanceLevel.CRITICAL)

    def test_dynamic_template_rendering(self):
        """Test template placeholder rendering with candidate and job context."""
        context = {
            "candidate_name": "Nandith Gireesh",
            "role_name": "Senior ML Engineer",
            "job_location": "Bangalore",
        }
        rendered = self.bank.render_question("INTRO_01", context=context, language="en")
        self.assertIn("Nandith Gireesh", rendered["rendered_prompt"])
        self.assertNotIn("{candidate_name}", rendered["rendered_prompt"])
        self.assertEqual(rendered["expected_answer_type"], "text")

    def test_multilingual_question_resolution(self):
        """Test multilingual translations in Hindi, Malayalam, Tamil, and English."""
        context = {
            "candidate_name": "Nandith",
            "role_name": "Python Developer",
            "job_location": "Kochi",
        }
        # English
        en_res = self.bank.render_question("INTRO_01", context=context, language="en")
        self.assertIn("Hello Nandith", en_res["rendered_prompt"])

        # Hindi
        hi_res = self.bank.render_question("INTRO_01", context=context, language="hi")
        self.assertIn("नमस्ते Nandith", hi_res["rendered_prompt"])

        # Malayalam
        ml_res = self.bank.render_question("INTRO_01", context=context, language="ml")
        self.assertIn("നമസ്കാരം Nandith", ml_res["rendered_prompt"])

        # Tamil
        ta_res = self.bank.render_question("INTRO_01", context=context, language="ta")
        self.assertIn("வணக்கம் Nandith", ta_res["rendered_prompt"])

    def test_generate_conversational_call_script(self):
        """Test assembling a complete AI voice screening script for a candidate."""
        candidate_data = {
            "name": "Arjun Menon",
            "ats_score": 88.0,
            "skills": ["Python", "TensorFlow", "FastAPI"],
            "total_experience": "3 years",
            "location": "Bangalore",
        }
        script = self.bank.generate_call_script(
            candidate_data=candidate_data,
            role_name="Machine Learning Engineer",
            job_location="Bangalore",
            language="en",
        )
        self.assertEqual(script.candidate_name, "Arjun Menon")
        self.assertEqual(script.role_name, "Machine Learning Engineer")
        self.assertGreaterEqual(script.total_stages, 7)
        self.assertGreater(script.estimated_call_duration_minutes, 0.0)
        self.assertIn("Arjun Menon", script.script_items[0].rendered_prompt)
        self.assertIsNotNone(script.closing_statement)


if __name__ == "__main__":
    unittest.main()
