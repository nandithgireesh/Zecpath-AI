import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestTranscriptAPI(unittest.TestCase):
    """
    Day 23 Integration Tests for Voice Transcript API Endpoints:
    - POST /screening/transcripts/normalize
    - POST /screening/transcripts/ingest
    - GET /screening/transcripts/{call_id}
    - GET /screening/transcripts/candidate/{candidate_id}
    - GET /screening/transcripts/metadata/standards
    - GET /screening/transcripts/db/summary
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_normalize_utterance_endpoint(self):
        """Test POST /screening/transcripts/normalize removes fillers and extracts entities."""
        payload = {
            "raw_text": "Um, basically I have around four years of experience in Python and machine learning, you know.",
            "confidence": 0.94
        }
        response = self.client.post("/screening/transcripts/normalize", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("cleaned_text", data)
        self.assertNotIn("um", data["cleaned_text"].lower())
        self.assertNotIn("basically", data["cleaned_text"].lower())
        self.assertEqual(data["confidence_level"], "HIGH")
        self.assertFalse(data["is_low_confidence"])
        self.assertEqual(data["normalized_entities"]["experience_years"], 4.0)
        self.assertIn("python", data["normalized_entities"]["skills"])

    def test_normalize_low_confidence_flag(self):
        """Test low confidence utterance is flagged properly."""
        payload = {
            "raw_text": "Muffled speech...",
            "confidence": 0.55
        }
        response = self.client.post("/screening/transcripts/normalize", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["confidence_level"], "LOW")
        self.assertTrue(data["is_low_confidence"])

    def test_ingest_voice_transcript_endpoint(self):
        """Test POST /screening/transcripts/ingest parses, normalizes, stores, and indexes a full call."""
        payload = {
            "session_id": "API_CALL_TEST_99",
            "metadata": {
                "candidate_id": "API_CAND_888",
                "candidate_name": "Jane Doe",
                "job_id": "JOB_ML_99",
                "role_name": "Machine Learning Engineer",
                "call_id": "API_CALL_TEST_99",
                "duration_seconds": 320.0,
                "avg_confidence": 0.92,
                "call_status": "COMPLETED",
                "language": "en"
            },
            "turns": [
                {
                    "turn_id": "T_01",
                    "speaker": "BOT",
                    "raw_text": "Hello Jane, what is your official notice period?",
                    "confidence": 0.99
                },
                {
                    "turn_id": "T_02",
                    "speaker": "CANDIDATE",
                    "raw_text": "Uh, like my notice period is two months with current employer.",
                    "confidence": 0.91
                }
            ],
            "question_interactions": [
                {
                    "interaction_id": "QI_01",
                    "question_id": "NP_01",
                    "category": "Notice period",
                    "prompt_text": "What is your official notice period?",
                    "response_raw": "Uh, like my notice period is two months.",
                    "confidence": 0.91
                },
                {
                    "interaction_id": "QI_02",
                    "question_id": "SAL_02",
                    "category": "Salary",
                    "prompt_text": "What is your expected compensation?",
                    "response_raw": "My expected CTC is around 18 LPA, negotiable.",
                    "confidence": 0.89
                }
            ]
        }

        # 1. Ingest call
        response = self.client.post("/screening/transcripts/ingest", json=payload)
        self.assertEqual(response.status_code, 200)
        ingest_data = response.json()
        self.assertEqual(ingest_data["status"], "INGESTED")
        self.assertEqual(ingest_data["call_id"], "API_CALL_TEST_99")
        self.assertEqual(ingest_data["total_turns"], 2)
        self.assertTrue(ingest_data["db_persisted"])
        self.assertIn("file_storage_path", ingest_data)

        # 2. Query session by ID
        get_res = self.client.get("/screening/transcripts/API_CALL_TEST_99")
        self.assertEqual(get_res.status_code, 200)
        session_data = get_res.json()
        self.assertEqual(session_data["candidate_id"], "API_CAND_888")
        self.assertEqual(len(session_data["turns"]), 2)
        self.assertEqual(len(session_data["question_interactions"]), 2)

        # 3. Query calls for candidate
        cand_res = self.client.get("/screening/transcripts/candidate/API_CAND_888")
        self.assertEqual(cand_res.status_code, 200)
        cand_data = cand_res.json()
        self.assertEqual(cand_data["total_calls"], 1)

    def test_metadata_standards_endpoint(self):
        """Test GET /screening/transcripts/metadata/standards returns formal documentation."""
        response = self.client.get("/screening/transcripts/metadata/standards")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("candidate_id", data["metadata_fields"])
        self.assertIn("question_id", data["metadata_fields"])
        self.assertTrue(len(data["normalization_rules"]) >= 5)
        self.assertIn("screening_calls", str(data["database_tables"]))

    def test_db_summary_endpoint(self):
        """Test GET /screening/transcripts/db/summary returns metrics."""
        response = self.client.get("/screening/transcripts/db/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_calls", data)
        self.assertIn("total_turns", data)
        self.assertIn("total_question_interactions", data)


if __name__ == "__main__":
    unittest.main()
