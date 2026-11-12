import os
import shutil
import tempfile
import unittest
from screening_ai.transcript_models import (
    SpeakerType,
    CallStatus,
    ConfidenceLevel,
    TranscriptTurn,
    QuestionInteractionRecord,
    CallMetadata,
    VoiceTranscriptPayload,
    ExtractedEntities,
)
from screening_ai.transcript_normalizer import TranscriptNormalizer
from screening_ai.transcript_db import TranscriptDatabaseManager
from screening_ai.transcript_storage import TranscriptStorageManager


class TestTranscriptArchitecture(unittest.TestCase):
    """
    Day 23 Unit Tests for Transcript Data Architecture:
    - Metadata standards verification
    - Normalization rules (fillers, numbers, notice period, CTC, experience)
    - SQLite relational storage
    - Hierarchical file-based archival
    """

    def setUp(self):
        self.normalizer = TranscriptNormalizer(confidence_threshold=0.70)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_screening.db")
        self.temp_storage_dir = os.path.join(self.temp_dir, "test_transcripts")
        self.db_manager = TranscriptDatabaseManager(db_path=self.temp_db)
        self.storage_manager = TranscriptStorageManager(base_dir=self.temp_storage_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_filler_word_removal(self):
        """Verify conversational fillers and verbal disfluencies are stripped cleanly."""
        noisy_text = "Um, actually I have like basically three years of experience, you know."
        cleaned, removed = self.normalizer.remove_filler_words(noisy_text)
        self.assertNotIn("um", cleaned.lower())
        self.assertNotIn("actually", cleaned.lower())
        self.assertNotIn("basically", cleaned.lower())
        self.assertNotIn("you know", cleaned.lower())
        self.assertIn("three years of experience", cleaned.lower())
        self.assertTrue(len(removed) >= 3)

    def test_number_and_experience_normalization(self):
        """Test conversion of spoken words and duration patterns into numeric years."""
        text_1 = "I have around three and a half years of industry experience"
        exp_1 = self.normalizer.normalize_experience(text_1)
        self.assertEqual(exp_1, 3.5)

        text_2 = "I've been working from 2022 to 2025 as a backend developer"
        exp_2 = self.normalizer.normalize_experience(text_2)
        self.assertEqual(exp_2, 3.0)

    def test_notice_period_normalization(self):
        """Verify notice period expressions are normalized into integer days and immediate joiner flag."""
        # Immediate joiner
        days_0, is_imm_0 = self.normalizer.normalize_notice_period("I am an immediate joiner and ready to join right now")
        self.assertEqual(days_0, 0)
        self.assertTrue(is_imm_0)

        # 60 days
        days_60, is_imm_60 = self.normalizer.normalize_notice_period("My official notice period is sixty days")
        self.assertEqual(days_60, 60)
        self.assertFalse(is_imm_60)

        # Months converted to days
        days_30, _ = self.normalizer.normalize_notice_period("I have one month notice period with my company")
        self.assertEqual(days_30, 30)

        days_14, _ = self.normalizer.normalize_notice_period("I can join in two weeks")
        self.assertEqual(days_14, 14)

    def test_salary_ctc_normalization(self):
        """Verify CTC and salary utterances are converted into numeric LPA and negotiation flag."""
        text_1 = "My expected CTC is twelve LPA and it is negotiable"
        ctc_1, neg_1 = self.normalizer.normalize_salary(text_1)
        self.assertEqual(ctc_1, 12.0)
        self.assertTrue(neg_1)

        text_2 = "Currently I am drawing 15,00,000 per annum"
        ctc_2, neg_2 = self.normalizer.normalize_salary(text_2)
        self.assertEqual(ctc_2, 15.0)
        self.assertFalse(neg_2)

    def test_confidence_level_thresholding(self):
        """Verify STT confidence scores are mapped to proper levels and low confidence flags."""
        high_level, is_low_high = self.normalizer.evaluate_confidence(0.92)
        self.assertEqual(high_level, ConfidenceLevel.HIGH)
        self.assertFalse(is_low_high)

        med_level, is_low_med = self.normalizer.evaluate_confidence(0.78)
        self.assertEqual(med_level, ConfidenceLevel.MEDIUM)
        self.assertFalse(is_low_med)

        low_level, is_low_low = self.normalizer.evaluate_confidence(0.60)
        self.assertEqual(low_level, ConfidenceLevel.LOW)
        self.assertTrue(is_low_low)

        crit_level, is_low_crit = self.normalizer.evaluate_confidence(0.35)
        self.assertEqual(crit_level, ConfidenceLevel.CRITICAL_LOW)
        self.assertTrue(is_low_crit)

    def test_full_transcript_normalization(self):
        """Test full normalization pipeline over a complete voice screening call payload."""
        meta = CallMetadata(
            candidate_id="CAND_101",
            candidate_name="Nandith Gireesh",
            job_id="JOB_ML_01",
            role_name="Machine Learning Engineer",
            call_id="CALL_SESSION_999",
            duration_seconds=360.0,
            avg_confidence=0.88,
        )
        turns = [
            TranscriptTurn(
                turn_id="TURN_01",
                speaker=SpeakerType.BOT,
                raw_text="Hello Nandith! Can you tell me about your notice period?",
                confidence=0.98,
            ),
            TranscriptTurn(
                turn_id="TURN_02",
                speaker=SpeakerType.CANDIDATE,
                raw_text="Um, basically my notice period is like thirty days, you know.",
                confidence=0.91,
            ),
        ]
        interactions = [
            QuestionInteractionRecord(
                interaction_id="INT_01",
                question_id="NP_01",
                category="Notice period",
                prompt_text="What is your notice period?",
                response_raw="Um, basically my notice period is like thirty days.",
                confidence=0.91,
            ),
            QuestionInteractionRecord(
                interaction_id="INT_02",
                question_id="SAL_02",
                category="Salary",
                prompt_text="What is your expected CTC?",
                response_raw="Actually my expected CTC is around twelve LPA, open for discussion.",
                confidence=0.89,
            ),
        ]
        payload = VoiceTranscriptPayload(
            session_id="CALL_SESSION_999",
            metadata=meta,
            turns=turns,
            question_interactions=interactions,
        )

        norm_data = self.normalizer.normalize_full_transcript(payload)
        self.assertEqual(norm_data.candidate_id, "CAND_101")
        self.assertEqual(norm_data.extracted_profile.notice_period_days, 30)
        self.assertEqual(norm_data.extracted_profile.expected_ctc_lpa, 12.0)
        self.assertTrue(norm_data.extracted_profile.ctc_negotiable)
        self.assertTrue(norm_data.readiness_for_scoring)

    def test_sqlite_database_persistence_and_query(self):
        """Verify relational SQLite database properly inserts, indexes, and queries call sessions."""
        meta = CallMetadata(
            candidate_id="CAND_202",
            candidate_name="Alice Smith",
            job_id="JOB_DEV_02",
            role_name="Backend Developer",
            call_id="CALL_TEST_001",
            session_id="SESS_TEST_001",
            duration_seconds=240.0,
            avg_confidence=0.89,
        )
        turns = [
            TranscriptTurn(
                turn_id="T1",
                speaker=SpeakerType.BOT,
                raw_text="Hello Alice, what frameworks do you use?",
                confidence=0.99,
            ),
            TranscriptTurn(
                turn_id="T2",
                speaker=SpeakerType.CANDIDATE,
                raw_text="I work heavily with Python, FastAPI, and Docker.",
                confidence=0.92,
            ),
        ]
        interactions = [
            QuestionInteractionRecord(
                interaction_id="I1",
                question_id="SKILL_01",
                category="Skills",
                prompt_text="What frameworks do you use?",
                response_raw="I work heavily with Python, FastAPI, and Docker.",
                confidence=0.92,
                extracted_entities=ExtractedEntities(skills_confirmed=["python", "fastapi", "docker"]),
            )
        ]
        payload = VoiceTranscriptPayload(
            session_id="SESS_TEST_001",
            metadata=meta,
            turns=turns,
            question_interactions=interactions,
        )

        # 1. Save to DB
        saved_id = self.db_manager.save_call_session(payload)
        self.assertEqual(saved_id, "CALL_TEST_001")

        # 2. Retrieve session
        session = self.db_manager.get_call_session(saved_id)
        self.assertIsNotNone(session)
        self.assertEqual(session["candidate_name"], "Alice Smith")
        self.assertEqual(len(session["turns"]), 2)
        self.assertEqual(len(session["question_interactions"]), 1)

        # 3. Query by candidate
        cand_calls = self.db_manager.get_calls_by_candidate("CAND_202")
        self.assertEqual(len(cand_calls), 1)

        # 4. Summary metrics
        summary = self.db_manager.get_db_summary()
        self.assertEqual(summary["total_calls"], 1)
        self.assertEqual(summary["total_turns"], 2)
        self.assertEqual(summary["total_question_interactions"], 1)

    def test_hierarchical_file_storage(self):
        """Verify file-based archival writes structured JSON in {job_id}/{candidate_id}/{call_id}.json."""
        meta = CallMetadata(
            candidate_id="CAND_303",
            job_id="JOB_AI_05",
            call_id="CALL_ARC_100",
            session_id="CALL_ARC_100",
            duration_seconds=120.0,
            avg_confidence=0.95,
        )
        payload = VoiceTranscriptPayload(
            session_id="CALL_ARC_100",
            metadata=meta,
            turns=[
                TranscriptTurn(turn_id="T1", speaker=SpeakerType.BOT, raw_text="Welcome", confidence=1.0)
            ],
        )

        saved_path = self.storage_manager.save_transcript(payload)
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue(saved_path.endswith("CALL_ARC_100.json"))

        loaded = self.storage_manager.get_transcript("JOB_AI_05", "CAND_303", "CALL_ARC_100")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["metadata"]["candidate_id"], "CAND_303")

        # List transcripts
        all_transcripts = self.storage_manager.list_transcripts(job_id="JOB_AI_05")
        self.assertEqual(len(all_transcripts), 1)


if __name__ == "__main__":
    unittest.main()
