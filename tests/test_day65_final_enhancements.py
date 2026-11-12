"""
Unit Tests for Day 65: Final Enhancements & Feature Polish
Platform: Zecpath Automated Hiring Platform
"""

import unittest
from final_enhancements import FinalFeatureEnhancer


class TestFinalEnhancements(unittest.TestCase):
    def test_sanitize_candidate_input_empty(self):
        res = FinalFeatureEnhancer.sanitize_candidate_input("")
        self.assertEqual(res, "NO_RESPONSE_PROVIDED")

        res_none = FinalFeatureEnhancer.sanitize_candidate_input(None)
        self.assertEqual(res_none, "NO_RESPONSE_PROVIDED")

        res_spaces = FinalFeatureEnhancer.sanitize_candidate_input("   \n\t  ")
        self.assertEqual(res_spaces, "NO_RESPONSE_PROVIDED")

    def test_sanitize_candidate_input_clean(self):
        cleaned = FinalFeatureEnhancer.sanitize_candidate_input("We deployed Kafka with 3 replicas.\x00\x08")
        self.assertEqual(cleaned, "We deployed Kafka with 3 replicas.")

    def test_sanitize_code_submission(self):
        empty_res = FinalFeatureEnhancer.sanitize_code_submission("")
        self.assertFalse(empty_res["valid"])
        self.assertEqual(empty_res["status"], "EMPTY_CODE")

        stub_res = FinalFeatureEnhancer.sanitize_code_submission("pass")
        self.assertTrue(stub_res["valid"])
        self.assertEqual(stub_res["status"], "INCOMPLETE_STUB")

        valid_res = FinalFeatureEnhancer.sanitize_code_submission("def solve(): return True")
        self.assertTrue(valid_res["valid"])
        self.assertEqual(valid_res["status"], "READY_FOR_AST")

    def test_generate_recruiter_summary(self):
        summary_strong = FinalFeatureEnhancer.generate_recruiter_summary(
            "Aditi Rao", "Senior Systems Architect", 97.0, "STRONG_HIRE", 100.0, 100.0, 95.0
        )
        self.assertIn("Aditi Rao", summary_strong)
        self.assertIn("Immediate offer", summary_strong)

        summary_reject = FinalFeatureEnhancer.generate_recruiter_summary(
            "Vikram Singh", "Senior Systems Architect", 14.8, "REJECT", 10.0, 25.0, 5.0
        )
        self.assertIn("Politely decline", summary_reject)


if __name__ == "__main__":
    unittest.main()

