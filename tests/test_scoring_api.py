import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestScoringAPI(unittest.TestCase):
    """
    Day 26 Integration Tests for Screening Scoring Engine Endpoints:
    - POST /screening/scoring/evaluate-question
    - POST /screening/scoring/evaluate-session
    - GET /screening/scoring/weights
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. POST /screening/scoring/evaluate-question
    # -------------------------------------------------------------
    def test_evaluate_question_high_quality_answer(self):
        payload = {
            "raw_text": "I have 5 years of experience architecting Python microservices using FastAPI, Docker, and PostgreSQL.",
            "question_category": "Technical Skills",
            "question_text": "Can you describe your technical experience with backend frameworks?",
            "question_id": "TECH_01",
        }
        response = self.client.post("/screening/scoring/evaluate-question", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["question_id"], "TECH_01")
        self.assertEqual(data["question_category"], "Technical Skills")
        self.assertGreaterEqual(data["weighted_question_score"], 80.0)
        self.assertIn(data["grade"], ["EXCELLENT", "STRONG"])
        self.assertIn("CLARITY", data["dimension_scores"])
        self.assertIn("RELEVANCE", data["dimension_scores"])
        self.assertIn("COMPLETENESS", data["dimension_scores"])
        self.assertIn("CONSISTENCY", data["dimension_scores"])
        self.assertTrue(len(data["strengths"]) > 0)
        self.assertTrue(len(data["explanation"]) > 10)

    def test_evaluate_question_vague_answer(self):
        payload = {
            "raw_text": "Well, it depends on many things, whatever is standard according to company norms.",
            "question_category": "Salary Expectation",
            "question_text": "What are your salary expectations?",
            "question_id": "SAL_01",
        }
        response = self.client.post("/screening/scoring/evaluate-question", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertLessEqual(data["clarity_score"], 70.0)
        self.assertLessEqual(data["completeness_score"], 70.0)
        self.assertLess(data["weighted_question_score"], 85.0)
        self.assertIn(data["grade"], ["STRONG", "MODERATE", "POOR", "UNSATISFACTORY"])
        self.assertTrue(len(data["weaknesses"]) > 0)

    def test_evaluate_question_off_topic_answer(self):
        payload = {
            "raw_text": "The weather today in Bangalore is really pleasant and sunny.",
            "question_category": "Experience",
            "question_id": "EXP_01",
        }
        response = self.client.post("/screening/scoring/evaluate-question", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertLessEqual(data["relevance_score"], 35.0)

    # -------------------------------------------------------------
    # 2. POST /screening/scoring/evaluate-session
    # -------------------------------------------------------------
    def test_evaluate_session_endpoint(self):
        payload = {
            "candidate_id": "CAND_API_26",
            "call_id": "CALL_API_26",
            "job_id": "JOB_AI_DEV",
            "turns": [
                {
                    "raw_text": "I have 4.5 years of experience building Python and FastAPI microservices.",
                    "question_category": "Experience",
                    "question_id": "Q1",
                },
                {
                    "raw_text": "I also specialize in PostgreSQL and Docker, but I have no experience in Kubernetes.",
                    "question_category": "Technical Skills",
                    "question_id": "Q2",
                },
                {
                    "raw_text": "My current CTC is 12 LPA, expecting 16.5 LPA. Notice period is 30 days.",
                    "question_category": "Salary Expectation",
                    "question_id": "Q3",
                },
            ],
        }
        response = self.client.post("/screening/scoring/evaluate-session", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["candidate_id"], "CAND_API_26")
        self.assertEqual(data["call_id"], "CALL_API_26")
        self.assertEqual(data["job_id"], "JOB_AI_DEV")
        self.assertGreaterEqual(data["overall_score"], 65.0)
        self.assertIn(data["recommendation_tier"], ["STRONGLY_RECOMMENDED", "RECOMMENDED"])
        self.assertEqual(len(data["per_question_breakdowns"]), 3)

        # Check category breakdowns
        self.assertIn("Experience", data["category_breakdowns"])
        self.assertIn("Technical Skills", data["category_breakdowns"])
        self.assertIn("Salary Expectation", data["category_breakdowns"])

        # Check explainability
        explainability = data["explainability"]
        self.assertIn("executive_summary", explainability)
        self.assertIn("key_strengths", explainability)
        self.assertIn("risk_factors", explainability)
        self.assertIn("recommended_interview_probes", explainability)

    # -------------------------------------------------------------
    # 3. GET /screening/scoring/weights
    # -------------------------------------------------------------
    def test_get_scoring_weights(self):
        response = self.client.get("/screening/scoring/weights")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("dimension_weights", data)
        self.assertIn("category_weights", data)
        self.assertIn("grade_thresholds", data)
        self.assertIn("recommendation_thresholds", data)

        self.assertIn("CLARITY", data["dimension_weights"])
        self.assertIn("RELEVANCE", data["dimension_weights"])
        self.assertIn("COMPLETENESS", data["dimension_weights"])
        self.assertIn("CONSISTENCY", data["dimension_weights"])


if __name__ == "__main__":
    unittest.main()
