"""
Unit Tests for Day 68 Final Optimization & Bug Fixing
Zecpath AI Automated Hiring Platform
Author: Nandith Gireesh (AI Engineering Intern)
Organisation: Zecser Business LLP
"""

import unittest
from final_validation_ai.bug_fix_engine import BugFixEngine, BugFixRecord
from final_validation_ai.consistency_validator import ConsistencyValidator
from final_validation_ai.performance_tuner import PerformanceTuner
from final_validation_ai.release_system import ReleaseReadyAISystem


class TestDay68FinalValidation(unittest.TestCase):

    def setUp(self):
        self.bug_engine = BugFixEngine()
        self.validator = ConsistencyValidator()
        self.tuner = PerformanceTuner()
        self.system = ReleaseReadyAISystem()

    # ---------------- 1. Bug Fix & Edge Case Tests ----------------

    def test_registered_bug_fixes(self):
        fixes = self.bug_engine.get_registered_fixes()
        self.assertGreaterEqual(len(fixes), 7)
        for fix in fixes:
            self.assertEqual(fix.status, "RESOLVED_VERIFIED")

    def test_unicode_normalization(self):
        raw_text = "Senior “Architect” – Python\u200B with \u2018special\u2019 quotes &amp; symbols."
        clean = self.bug_engine.normalize_unicode_text(raw_text)
        self.assertNotIn("“", clean)
        self.assertNotIn("”", clean)
        self.assertNotIn("\u200B", clean)
        self.assertIn('"Architect"', clean)
        self.assertIn("&", clean)

    def test_clamp_score(self):
        self.assertEqual(self.bug_engine.clamp_score(-15.5), 0.0)
        self.assertEqual(self.bug_engine.clamp_score(115.8), 100.0)
        self.assertEqual(self.bug_engine.clamp_score(88.456), 88.46)
        self.assertEqual(self.bug_engine.clamp_score("invalid"), 0.0)

    def test_empty_resume_edge_case(self):
        res = self.bug_engine.safe_parse_resume_content("   \n\t   ")
        self.assertFalse(res["parsed_successfully"])
        self.assertEqual(res["word_count"], 0)
        self.assertEqual(res["safe_score"], 0.0)
        self.assertEqual(res["status"], "FALLBACK_EMPTY_INPUT")

    def test_valid_resume_parsing(self):
        resume = "Full-stack engineer with 5 years experience in Python, FastAPI, Docker, and AWS."
        res = self.bug_engine.safe_parse_resume_content(resume)
        self.assertTrue(res["parsed_successfully"])
        self.assertGreater(res["word_count"], 5)
        self.assertIn("python", res["skills_detected"])
        self.assertIn("fastapi", res["skills_detected"])
        self.assertGreater(res["safe_score"], 0.0)

    def test_zero_word_star_response(self):
        # Must not raise ZeroDivisionError
        star = self.bug_engine.safe_lexical_star_eval("")
        self.assertEqual(star["word_count"], 0)
        self.assertEqual(star["lexical_density"], 0.0)
        self.assertEqual(star["score"], 0.0)

    def test_rich_star_response(self):
        resp = "In that situation, our team had a major task to optimize latency. My action was rewriting the query. As a result, latency fell by 50%."
        star = self.bug_engine.safe_lexical_star_eval(resp)
        self.assertGreater(star["word_count"], 10)
        self.assertGreater(star["lexical_density"], 0.0)
        self.assertTrue(star["star_elements_present"]["situation"])
        self.assertTrue(star["star_elements_present"]["task"])
        self.assertTrue(star["star_elements_present"]["action"])
        self.assertTrue(star["star_elements_present"]["result"])
        self.assertGreater(star["score"], 70.0)

    def test_proctoring_debounce_filter(self):
        # Micro blurs (<2.5s) should be filtered out
        blurs = [0.5, 0.8, 1.2, 0.4]
        res = self.bug_engine.safe_proctoring_filter(blurs, 100.0)
        self.assertEqual(res["sustained_events_count"], 0)
        self.assertFalse(res["is_suspicious"])
        self.assertEqual(res["integrity_score"], 100.0)

        # Prolonged blur (>=2.5s) should be tracked
        sustained_blurs = [1.0, 4.0, 5.0, 3.5]
        res_sustained = self.bug_engine.safe_proctoring_filter(sustained_blurs, 100.0)
        self.assertEqual(res_sustained["sustained_events_count"], 3)
        self.assertTrue(res_sustained["is_suspicious"])
        self.assertLess(res_sustained["integrity_score"], 80.0)

    def test_cache_compaction(self):
        # Fill cache past 1000 limit
        for i in range(1200):
            self.bug_engine._session_cache[f"key_{i}"] = i
        evicted = self.bug_engine.auto_compact_cache(max_entries=1000)
        self.assertEqual(evicted, 600)
        self.assertEqual(len(self.bug_engine._session_cache), 600)

    # ---------------- 2. Consistency Validator Tests ----------------

    def test_consistency_validation_success(self):
        payload = {
            "candidate_id": "CAND-001",
            "round_scores": {
                "ats_screening": 90.0,
                "hr_screening": 85.0,
                "tech_interview": 92.0,
                "behavioral_star": 88.0,
                "coding_machine_test": 95.0
            },
            # composite = 0.20*90 + 0.15*85 + 0.25*92 + 0.20*88 + 0.20*95 = 18 + 12.75 + 23 + 17.6 + 19 = 90.35
            "composite_score": 90.35,
            "final_decision": "STRONG_HIRE",
            "recruiter_summary": "Exceptional senior engineer showing pristine technical and architectural competence."
        }
        report = self.validator.validate_candidate_pipeline_output(payload)
        self.assertTrue(report.overall_valid)
        self.assertEqual(report.rules_failed, 0)
        self.assertEqual(len(report.integrity_hash), 64)

    def test_consistency_validation_tier_mismatch(self):
        # Score is 90.35 (STRONG_HIRE), but reported decision is REJECT
        payload = {
            "candidate_id": "CAND-002",
            "round_scores": {
                "ats_screening": 90.0,
                "hr_screening": 85.0,
                "tech_interview": 92.0,
                "behavioral_star": 88.0,
                "coding_machine_test": 95.0
            },
            "composite_score": 90.35,
            "final_decision": "REJECT",  # MISMATCH!
            "recruiter_summary": "Mismatch test"
        }
        report = self.validator.validate_candidate_pipeline_output(payload)
        self.assertFalse(report.overall_valid)
        self.assertGreater(report.rules_failed, 0)

    def test_consistency_validation_math_drift(self):
        # Composite does not match weighted formula
        payload = {
            "candidate_id": "CAND-003",
            "round_scores": {
                "ats_screening": 90.0,
                "hr_screening": 85.0,
                "tech_interview": 92.0,
                "behavioral_star": 88.0,
                "coding_machine_test": 95.0
            },
            "composite_score": 50.0,  # DRIFT!
            "final_decision": "BORDERLINE",
            "recruiter_summary": "Drift test"
        }
        report = self.validator.validate_candidate_pipeline_output(payload)
        self.assertFalse(report.overall_valid)

    # ---------------- 3. Performance Tuner Tests ----------------

    def test_performance_tuner_benchmark(self):
        scorecard = self.tuner.run_benchmark(iterations=100)
        self.assertTrue(scorecard.sla_passed)
        self.assertLess(scorecard.p99_latency_ms, 15.0)
        self.assertGreater(scorecard.throughput_evals_per_sec, 200.0)

    # ---------------- 4. Release-Ready System Tests ----------------

    def test_system_health_check(self):
        health = self.system.run_system_health_check()
        self.assertEqual(health.overall_status, "RELEASE_READY_CERTIFIED")
        self.assertEqual(health.modules_healthy, 7)
        self.assertEqual(health.total_modules, 7)

    def test_end_to_end_candidate_evaluation(self):
        res = self.system.evaluate_candidate(
            candidate_id="CAND-PROD-777",
            job_id="JOB-AI-LEAD",
            resume_text="Senior Machine Learning Specialist with 7+ years building Python, PyTorch, Docker, Kubernetes services.",
            hr_score=86.0,
            tech_score=94.0,
            star_response="In our situation we needed low latency. My task was model distillation. As an action I pruned weights. Result was 4x speedup.",
            coding_score=92.0
        )
        self.assertTrue(res.consistency_passed)
        self.assertEqual(res.final_decision, "STRONG_HIRE")
        self.assertGreater(res.composite_score, 85.0)
        self.assertLess(res.latency_ms, 20.0)

    def test_end_to_end_corrupted_input_graceful_recovery(self):
        # Empty inputs should not crash and should resolve cleanly to REJECT
        res = self.system.evaluate_candidate(
            candidate_id="CAND-EMPTY-000",
            job_id="JOB-TEST",
            resume_text=None,
            hr_score=0.0,
            tech_score=0.0,
            star_response=None,
            coding_score=0.0
        )
        self.assertTrue(res.consistency_passed)
        self.assertEqual(res.final_decision, "REJECT")
        self.assertEqual(res.composite_score, 0.0)


if __name__ == "__main__":
    unittest.main()

