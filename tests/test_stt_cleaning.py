import unittest
import os
import json
from screening_ai.stt_models import (
    AccentType,
    NoiseCondition,
    SpeechEdgeCaseType,
    CleanTranscriptResult,
)
from screening_ai.stt_cleaner import CleanTranscriptProcessor
from screening_ai.stt_service import SpeechToTextService
from screening_ai.stt_benchmark import (
    STTAccuracyBenchmarkHarness,
    calculate_wer,
    calculate_cer,
    levenshtein_distance,
)


class TestSTTCleaningAndEdgeCases(unittest.TestCase):

    def setUp(self):
        self.cleaner = CleanTranscriptProcessor()
        self.service = SpeechToTextService()
        self.benchmark = STTAccuracyBenchmarkHarness()

    # -------------------------------------------------------------
    # 1. Text Cleanup: Filler Word Removal
    # -------------------------------------------------------------
    def test_filler_word_removal_standard(self):
        raw = "Um, I have, uh, basically 4 years of experience, you know, in Python."
        cleaned, fillers = self.cleaner.remove_filler_words(raw)
        self.assertNotIn("um", cleaned.lower())
        self.assertNotIn("uh", cleaned.lower())
        self.assertNotIn("basically", cleaned.lower())
        self.assertNotIn("you know", cleaned.lower())
        self.assertIn("4 years of experience", cleaned)
        self.assertTrue(len(fillers) >= 3)

    def test_filler_word_removal_indian_english(self):
        raw = "I am ready to relocate, yaar, matlab I want to join immediately na, toh that is fine."
        cleaned, fillers = self.cleaner.remove_filler_words(raw)
        self.assertNotIn("yaar", cleaned.lower())
        self.assertNotIn("matlab", cleaned.lower())
        self.assertNotIn("na", cleaned.lower().split())
        self.assertNotIn("toh", cleaned.lower().split())
        self.assertIn("ready to relocate", cleaned)

    # -------------------------------------------------------------
    # 2. Punctuation Correction & Question Inference
    # -------------------------------------------------------------
    def test_correct_punctuation_statement(self):
        raw = "i have worked with fastapi and docker"
        punctuated = self.cleaner.correct_punctuation(raw)
        self.assertTrue(punctuated.startswith("I"))
        self.assertTrue(punctuated.endswith("."))

    def test_correct_punctuation_question_inference(self):
        raw = "can you tell me more about the compensation package"
        punctuated = self.cleaner.correct_punctuation(raw)
        self.assertTrue(punctuated.startswith("Can"))
        self.assertTrue(punctuated.endswith("?"))

        raw_what = "what is the remote work policy"
        punctuated_what = self.cleaner.correct_punctuation(raw_what)
        self.assertTrue(punctuated_what.endswith("?"))

    # -------------------------------------------------------------
    # 3. Canonical Proper Noun Casing
    # -------------------------------------------------------------
    def test_normalize_case_technical_terms(self):
        raw = "I built backend APIs with python, pytorch, tensorflow, and docker in bangalore for 15 lpa."
        normalized = self.cleaner.normalize_case(raw)
        self.assertIn("Python", normalized)
        self.assertIn("PyTorch", normalized)
        self.assertIn("TensorFlow", normalized)
        self.assertIn("Docker", normalized)
        self.assertIn("Bangalore", normalized)
        self.assertIn("LPA", normalized)

    def test_normalize_case_education_degrees(self):
        raw = "I completed my b.tech degree and currently pursuing m.tech."
        normalized = self.cleaner.normalize_case(raw)
        self.assertIn("B.Tech", normalized)
        self.assertIn("M.Tech", normalized)

    # -------------------------------------------------------------
    # 4. Conversational Edge Cases: Interrupted Speech
    # -------------------------------------------------------------
    def test_interrupted_speech_trailing_dashes(self):
        text = "I was leading the data engineering pipeline and then--"
        is_interrupted, prompt = self.cleaner.detect_interrupted_speech(text)
        self.assertTrue(is_interrupted)
        self.assertIsNotNone(prompt)
        self.assertIn("cut off", prompt)

    def test_interrupted_speech_dangling_conjunction(self):
        text = "I would be very interested in this role because"
        is_interrupted, prompt = self.cleaner.detect_interrupted_speech(text)
        self.assertTrue(is_interrupted)
        self.assertIsNotNone(prompt)
        self.assertIn("complete your sentence", prompt)

    def test_normal_uninterrupted_speech(self):
        text = "I have 5 years of experience in distributed systems."
        is_interrupted, prompt = self.cleaner.detect_interrupted_speech(text)
        self.assertFalse(is_interrupted)
        self.assertIsNone(prompt)

    # -------------------------------------------------------------
    # 5. Conversational Edge Cases: Partial Answers
    # -------------------------------------------------------------
    def test_partial_answer_salary_missing_number(self):
        category = "Salary Expectation"
        text = "Yes, I am looking for a competitive industry standard salary."
        is_partial, missing, prompt = self.cleaner.detect_partial_answer(category, text)
        self.assertTrue(is_partial)
        self.assertIn("expected_ctc_lpa", missing)
        self.assertIsNotNone(prompt)
        self.assertIn("LPA", prompt)

    def test_complete_answer_salary(self):
        category = "Salary Expectation"
        text = "My current CTC is 12 LPA and I am expecting 16 LPA."
        is_partial, missing, prompt = self.cleaner.detect_partial_answer(category, text)
        self.assertFalse(is_partial)
        self.assertEqual(len(missing), 0)

    def test_partial_answer_notice_period(self):
        category = "Notice Period"
        text = "I am currently employed at my company."
        is_partial, missing, prompt = self.cleaner.detect_partial_answer(category, text)
        self.assertTrue(is_partial)
        self.assertIn("notice_period_duration", missing)

    def test_complete_answer_notice_period(self):
        category = "Notice Period"
        text = "My official notice period is 30 days."
        is_partial, missing, prompt = self.cleaner.detect_partial_answer(category, text)
        self.assertFalse(is_partial)

    # -------------------------------------------------------------
    # 6. Conversational Edge Cases: Silence Detection
    # -------------------------------------------------------------
    def test_silence_detection_empty_text(self):
        is_silence, prompt = self.cleaner.detect_silence("", 0.0)
        self.assertTrue(is_silence)
        self.assertIn("still with me", prompt)

    def test_silence_detection_long_silence_duration(self):
        is_silence, prompt = self.cleaner.detect_silence("hello", 3.5)
        self.assertTrue(is_silence)
        self.assertIn("still with me", prompt)

    def test_non_silence(self):
        is_silence, prompt = self.cleaner.detect_silence("I am here and ready to speak.", 0.5)
        self.assertFalse(is_silence)
        self.assertIsNone(prompt)

    # -------------------------------------------------------------
    # 7. End-to-End process_transcript Pipeline
    # -------------------------------------------------------------
    def test_full_process_transcript_cleaning_pipeline(self):
        raw = "um basically my current ctc is 15 lpa and i am looking for 18 lpa in bangalore na"
        res = self.cleaner.process_transcript(raw, category="Salary Expectation")
        self.assertIsInstance(res, CleanTranscriptResult)
        self.assertNotIn("um", res.cleaned_text.lower().split())
        self.assertNotIn("basically", res.cleaned_text.lower().split())
        self.assertIn("15 LPA", res.cleaned_text)
        self.assertIn("Bangalore", res.cleaned_text)
        self.assertEqual(res.edge_case_analysis.edge_case, SpeechEdgeCaseType.NORMAL)
        self.assertTrue(res.punctuation_corrected)
        self.assertTrue(res.proper_case_applied)

    # -------------------------------------------------------------
    # 8. STT Accuracy Benchmarking (WER / CER Metrics)
    # -------------------------------------------------------------
    def test_wer_exact_match(self):
        ref = "I have five years of experience in Python"
        hyp = "I have five years of experience in Python"
        self.assertEqual(calculate_wer(ref, hyp), 0.0)
        self.assertEqual(calculate_cer(ref, hyp), 0.0)

    def test_wer_substitution_and_deletion(self):
        ref = "I have five years of experience"
        hyp = "I have four years experience"
        # 1 substitution (five -> four), 1 deletion (of) -> 2 errors / 6 words = 0.3333
        wer = calculate_wer(ref, hyp)
        self.assertAlmostEqual(wer, 0.3333, places=2)

    def test_run_benchmark_suite(self):
        report = self.benchmark.run_benchmark()
        self.assertGreater(report.total_tests, 0)
        self.assertGreaterEqual(report.overall_wer, 0.0)
        self.assertGreaterEqual(report.overall_cer, 0.0)
        self.assertIn(AccentType.INDIAN_ENGLISH.value, report.accent_breakdown)
        self.assertIn(NoiseCondition.CLEAN_STUDIO.value, report.noise_breakdown)
        self.assertTrue(os.path.exists(self.benchmark.output_report_path))


if __name__ == "__main__":
    unittest.main()
