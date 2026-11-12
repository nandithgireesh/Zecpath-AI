import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestIntentAPI(unittest.TestCase):
    """
    Day 25 Integration Tests for Intent Classification & Answer Understanding Endpoints:
    - POST /screening/intent/classify
    - POST /screening/answer/understand
    - POST /screening/answer/batch-understand
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. POST /screening/intent/classify
    # -------------------------------------------------------------
    def test_classify_intent_endpoint_experience(self):
        payload = {
            "text": "I have 4 years of experience as a machine learning engineer building NLP models.",
            "question_category": "Experience"
        }
        response = self.client.post("/screening/intent/classify", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["primary_intent"], "PROVIDING_EXPERIENCE")
        self.assertGreaterEqual(data["confidence"], 0.65)

    def test_classify_intent_endpoint_clarification(self):
        payload = {
            "text": "Could you please repeat the question? I didn't hear you clearly."
        }
        response = self.client.post("/screening/intent/classify", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["primary_intent"], "ASKING_CLARIFICATION")
        self.assertGreaterEqual(data["confidence"], 0.85)

    # -------------------------------------------------------------
    # 2. POST /screening/answer/understand
    # -------------------------------------------------------------
    def test_understand_answer_endpoint_full_profile(self):
        payload = {
            "raw_text": "I have 3.5 years of experience in Python and FastAPI. Currently drawing 10 LPA and expecting 14 LPA, notice period is 30 days.",
            "question_category": "Experience",
            "turn_id": "T_101",
            "question_id": "EXP_01"
        }
        response = self.client.post("/screening/answer/understand", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["turn_id"], "T_101")
        self.assertEqual(data["question_id"], "EXP_01")
        self.assertIn("Python", data["cleaned_text"])
        self.assertIsNotNone(data["experience"])
        self.assertEqual(data["experience"]["total_years"], 3.5)
        self.assertIsNotNone(data["salary"])
        self.assertEqual(data["salary"]["expected_ctc_lpa"], 14.0)
        self.assertIsNotNone(data["availability"])
        self.assertEqual(data["availability"]["notice_period_days"], 30)
        self.assertFalse(data["quality"]["is_off_topic"])

    def test_understand_answer_endpoint_vague_salary_follow_up(self):
        payload = {
            "raw_text": "I expect standard industry compensation.",
            "question_category": "Salary Expectation"
        }
        response = self.client.post("/screening/answer/understand", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["quality"]["is_vague"])
        self.assertIn("expected_ctc_lpa", data["quality"]["missing_slots"])
        self.assertIsNotNone(data["follow_up_recommendation"])
        self.assertIn("LPA", data["follow_up_recommendation"])

    # -------------------------------------------------------------
    # 3. POST /screening/answer/batch-understand
    # -------------------------------------------------------------
    def test_batch_understand_dialogue_endpoint(self):
        payload = {
            "turns": [
                {
                    "raw_text": "I have 4 years experience in Python and PyTorch.",
                    "question_category": "Experience",
                    "turn_id": "TURN_1"
                },
                {
                    "raw_text": "I haven't used Kubernetes before.",
                    "question_category": "Technical Skills",
                    "turn_id": "TURN_2"
                },
                {
                    "raw_text": "My expected salary is 18 LPA.",
                    "question_category": "Salary Expectation",
                    "turn_id": "TURN_3"
                }
            ]
        }
        response = self.client.post("/screening/answer/batch-understand", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["total_turns_analyzed"], 3)
        self.assertIn("python", data["aggregated_skills"])
        self.assertIn("pytorch", data["aggregated_skills"])
        # Kubernetes was declined, so shouldn't be in confirmed aggregated_skills
        self.assertNotIn("kubernetes", data["aggregated_skills"])
        self.assertGreater(data["overall_clarity_score"], 0.5)
        self.assertEqual(len(data["structured_answers"]), 3)


if __name__ == "__main__":
    unittest.main()
