import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main_day20 import app


class TestScreeningQuestionBankAPI(unittest.TestCase):
    """
    Day 22 - API endpoint integration tests for Question Bank and Call Scripts.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_screening_questions_endpoint(self):
        """Test GET /screening/questions with and without query filters."""
        # 1. All questions
        response = self.client.get("/screening/questions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_found", data)
        self.assertGreater(data["total_found"], 0)

        # 2. Filter by category
        res_cat = self.client.get("/screening/questions?category=Salary")
        self.assertEqual(res_cat.status_code, 200)
        cat_data = res_cat.json()
        for q in cat_data["questions"]:
            self.assertEqual(q["category"], "Salary")

        # 3. Filter by mandatory
        res_mand = self.client.get("/screening/questions?mandatory_only=true")
        self.assertEqual(res_mand.status_code, 200)
        mand_data = res_mand.json()
        for q in mand_data["questions"]:
            self.assertTrue(q["is_mandatory"])

    def test_get_screening_categories_endpoint(self):
        """Test GET /screening/categories returns full category taxonomy."""
        response = self.client.get("/screening/categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertIn("Introduction", data["categories"])
        self.assertIn("Notice period", data["categories"])
        self.assertEqual(data["total_categories"], 7)

    def test_render_screening_question_endpoint(self):
        """Test POST /screening/questions/render with dynamic context."""
        payload = {
            "question_id": "LOC_02",
            "context": {
                "job_location": "Hyderabad",
                "role_name": "DevOps Engineer",
            },
            "language": "en",
        }
        response = self.client.post("/screening/questions/render", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["question_id"], "LOC_02")
        self.assertIn("Hyderabad", data["rendered_prompt"])
        self.assertEqual(data["expected_answer_type"], "choice")

    def test_generate_screening_call_script_endpoint(self):
        """Test POST /screening/script/generate creates full structured script."""
        payload = {
            "candidate_data": {
                "name": "Priya Sharma",
                "ats_score": 91.5,
                "skills": ["React", "Node.js", "MongoDB"],
                "total_experience": "4 years",
                "location": "Kochi",
            },
            "role_name": "MERN Stack Developer",
            "job_location": "Bangalore",
            "language": "en",
            "bot_name": "Zecpath AI Recruiter",
        }
        response = self.client.post("/screening/script/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["candidate_name"], "Priya Sharma")
        self.assertEqual(data["role_name"], "MERN Stack Developer")
        self.assertGreaterEqual(data["total_stages"], 7)
        self.assertIn("script_items", data)
        self.assertGreater(len(data["script_items"]), 0)


if __name__ == "__main__":
    unittest.main()
