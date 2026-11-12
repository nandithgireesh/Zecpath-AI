"""
Unit Tests for Day 31: Language Mixing & Code-Switching Normalizer
"""

import unittest
from screening_ai.failure_models import (
    LanguageMixingCategory,
    CodeSwitchResult,
)
from screening_ai.language_mixing_normalizer import LanguageMixingNormalizer


class TestLanguageMixingNormalizer(unittest.TestCase):

    def test_monolingual_english(self):
        """Standard English utterance should remain unchanged."""
        text = "We configured Celery workers backed by Redis for asynchronous job processing."
        res = LanguageMixingNormalizer.analyze_and_normalize(text)
        self.assertEqual(res.detected_category, LanguageMixingCategory.MONOLINGUAL_ENGLISH)
        self.assertEqual(res.hindi_token_count, 0)
        self.assertEqual(res.normalized_english_text, text)
        self.assertIn("celery", res.extracted_entities.get("technologies", []))
        self.assertIn("redis", res.extracted_entities.get("technologies", []))

    def test_hinglish_salary_extraction(self):
        """Hinglish compensation with 'bees lakh' and 'pachees LPA' should be normalized."""
        text = "Current CTC bees lakh hai aur expected pachees LPA hai, but negotiable hai."
        res = LanguageMixingNormalizer.analyze_and_normalize(text)
        self.assertIn(res.detected_category, [
            LanguageMixingCategory.HINGLISH_CODE_SWITCH,
            LanguageMixingCategory.BILINGUAL_TECHNICAL,
        ])
        self.assertGreater(res.hindi_token_count, 2)
        self.assertEqual(res.extracted_entities.get("salary_lpa"), 25.0)
        self.assertIn("25 LPA", res.normalized_english_text)

    def test_hinglish_tech_architecture(self):
        """Hinglish architecture statement should preserve tech terms and normalize connectives."""
        text = "Humne Celery aur Redis use kiya tha async processing ke liye kyunki scale high tha aur latency kam thi."
        res = LanguageMixingNormalizer.analyze_and_normalize(text)
        self.assertEqual(res.detected_category, LanguageMixingCategory.BILINGUAL_TECHNICAL)
        self.assertIn("celery", res.extracted_entities.get("technologies", []))
        self.assertIn("redis", res.extracted_entities.get("technologies", []))
        # Verify normalized English text
        norm = res.normalized_english_text.lower()
        self.assertIn("celery", norm)
        self.assertIn("redis", norm)
        self.assertIn("because", norm)
        self.assertTrue("latency was low" in norm or "was low" in norm or "was very low" in norm)

    def test_bilingual_notice_and_buyout(self):
        """Translates 'do mahine' to 60 days and detects buyout flexibility."""
        text = "Mera notice period do mahine ka hai lekin manager se baat hui thi aur buyout possible hai."
        res = LanguageMixingNormalizer.analyze_and_normalize(text)
        self.assertEqual(res.extracted_entities.get("notice_days"), 60)
        self.assertTrue(res.extracted_entities.get("buyout_flexible"))
        norm = res.normalized_english_text.lower()
        self.assertIn("60 days", norm)
        self.assertIn("buyout is possible", norm)

    def test_transliterated_experience(self):
        """Translates 'paanch saal' to 5 years experience and preserves Docker/Python."""
        text = "Mujhe paanch saal ka experience hai Python aur Docker mein."
        res = LanguageMixingNormalizer.analyze_and_normalize(text)
        self.assertIn("python", res.extracted_entities.get("technologies", []))
        self.assertIn("docker", res.extracted_entities.get("technologies", []))
        norm = res.normalized_english_text.lower()
        self.assertIn("5 years", norm)

    def test_empty_utterance(self):
        """Empty string should return clean empty structure without exceptions."""
        res = LanguageMixingNormalizer.analyze_and_normalize("")
        self.assertEqual(res.detected_category, LanguageMixingCategory.MONOLINGUAL_ENGLISH)
        self.assertEqual(res.normalized_english_text, "")
        self.assertEqual(res.hindi_token_count, 0)


if __name__ == "__main__":
    unittest.main()
