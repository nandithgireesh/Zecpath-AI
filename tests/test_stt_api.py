import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestSTTAPI(unittest.TestCase):
    """
    Day 24 Integration Tests for Speech-to-Text Integration & Cleaning Endpoints:
    - POST /screening/stt/clean
    - POST /screening/stt/transcribe
    - POST /screening/stt/benchmark/run
    - GET /screening/stt/benchmark/report
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. POST /screening/stt/clean
    # -------------------------------------------------------------
    def test_clean_transcript_endpoint_success(self):
        payload = {
            "raw_text": "um basically i have been building apps using python and pytorch in bangalore, you know",
            "question_category": "General",
            "silence_duration_seconds": 0.0
        }
        response = self.client.post("/screening/stt/clean", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("cleaned_text", data)
        self.assertNotIn("um", data["cleaned_text"].lower().split())
        self.assertNotIn("basically", data["cleaned_text"].lower().split())
        self.assertIn("Python", data["cleaned_text"])
        self.assertIn("PyTorch", data["cleaned_text"])
        self.assertIn("Bangalore", data["cleaned_text"])
        self.assertTrue(data["punctuation_corrected"])
        self.assertTrue(data["proper_case_applied"])
        self.assertEqual(data["edge_case_analysis"]["edge_case"], "NORMAL")

    def test_clean_transcript_interrupted_edge_case(self):
        payload = {
            "raw_text": "I was previously working at an MNC and then--",
            "question_category": "General",
            "silence_duration_seconds": 0.0
        }
        response = self.client.post("/screening/stt/clean", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["edge_case_analysis"]["edge_case"], "INTERRUPTED_SPEECH")
        self.assertTrue(data["edge_case_analysis"]["is_interrupted"])
        self.assertIsNotNone(data["edge_case_analysis"]["recovery_prompt"])

    def test_clean_transcript_partial_answer_edge_case(self):
        payload = {
            "raw_text": "I expect standard compensation.",
            "question_category": "Salary Expectation",
            "silence_duration_seconds": 0.0
        }
        response = self.client.post("/screening/stt/clean", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["edge_case_analysis"]["edge_case"], "PARTIAL_ANSWER")
        self.assertTrue(data["edge_case_analysis"]["is_partial"])
        self.assertIn("expected_ctc_lpa", data["edge_case_analysis"]["missing_required_entities"])
        self.assertIn("LPA", data["edge_case_analysis"]["recovery_prompt"])

    def test_clean_transcript_silence_edge_case(self):
        payload = {
            "raw_text": "",
            "question_category": "General",
            "silence_duration_seconds": 4.0
        }
        response = self.client.post("/screening/stt/clean", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["edge_case_analysis"]["edge_case"], "SILENCE_DETECTED")
        self.assertTrue(data["edge_case_analysis"]["is_silence"])
        self.assertIn("still with me", data["edge_case_analysis"]["recovery_prompt"])

    # -------------------------------------------------------------
    # 2. POST /screening/stt/transcribe
    # -------------------------------------------------------------
    def test_transcribe_simulated_speech_stream(self):
        payload = {
            "text_payload": "uh i have worked with docker and fastapi for 3 years, actually.",
            "accent": "INDIAN_ENGLISH",
            "noise_condition": "OFFICE_BACKGROUND",
            "question_category": "General"
        }
        response = self.client.post("/screening/stt/transcribe", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("cleaned_transcript", data)
        self.assertIn("Docker", data["cleaned_transcript"])
        self.assertIn("FastAPI", data["cleaned_transcript"])
        self.assertEqual(data["detected_accent"], "INDIAN_ENGLISH")
        self.assertGreater(data["confidence"], 0.0)
        self.assertLessEqual(data["confidence"], 1.0)
        self.assertGreater(len(data["word_confidences"]), 0)
        self.assertEqual(data["edge_case"], "NORMAL")

    def test_transcribe_missing_payload_returns_400(self):
        payload = {
            "accent": "INDIAN_ENGLISH",
            "noise_condition": "CLEAN_STUDIO"
        }
        response = self.client.post("/screening/stt/transcribe", json=payload)
        self.assertEqual(response.status_code, 400)

    # -------------------------------------------------------------
    # 3. POST /screening/stt/benchmark/run
    # -------------------------------------------------------------
    def test_run_benchmark_endpoint(self):
        response = self.client.post("/screening/stt/benchmark/run")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_tests", data)
        self.assertGreater(data["total_tests"], 0)
        self.assertIn("overall_wer", data)
        self.assertIn("overall_cer", data)
        self.assertIn("accent_breakdown", data)
        self.assertIn("noise_breakdown", data)
        self.assertEqual(data["status"], "COMPLETED")

    # -------------------------------------------------------------
    # 4. GET /screening/stt/benchmark/report
    # -------------------------------------------------------------
    def test_get_benchmark_report_endpoint(self):
        response = self.client.get("/screening/stt/benchmark/report")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_tests", data)
        self.assertGreater(data["total_tests"], 0)
        self.assertIn("overall_wer", data)
        self.assertIn("overall_cer", data)
        self.assertEqual(data["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
