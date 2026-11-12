"""
Unit Tests for Day 63: Demo Dataset & Simulation Environment
Platform: Zecpath Automated Hiring Platform
"""

import unittest
from demo_dataset_ai import (
    CURATED_JOB_DESCRIPTIONS,
    CURATED_CANDIDATE_RESUMES,
    CURATED_CANDIDATE_RESPONSES,
    EndToEndSimulationEnvironment,
)


class TestCuratedDataset(unittest.TestCase):
    def test_job_descriptions_loaded(self):
        self.assertIn("JOB-BACKEND-SR", CURATED_JOB_DESCRIPTIONS)
        job = CURATED_JOB_DESCRIPTIONS["JOB-BACKEND-SR"]
        self.assertEqual(job.min_experience_years, 5.0)
        self.assertTrue("Python" in job.required_skills)
        self.assertEqual(len(job.target_competencies), 4)

    def test_candidate_resumes_loaded(self):
        self.assertEqual(len(CURATED_CANDIDATE_RESUMES), 4)
        senior = CURATED_CANDIDATE_RESUMES["CAND-ARCH-01"]
        self.assertEqual(senior.archetype, "HIGH_CALIBER_SENIOR")
        self.assertGreaterEqual(senior.experience_years, 7.0)

        mismatched = CURATED_CANDIDATE_RESUMES["CAND-MISMATCH-04"]
        self.assertEqual(mismatched.archetype, "MISMATCHED_PROFILE")
        self.assertTrue("Adobe Photoshop" in mismatched.skills)

    def test_candidate_responses_loaded(self):
        self.assertEqual(len(CURATED_CANDIDATE_RESPONSES), 4)
        senior_resp = CURATED_CANDIDATE_RESPONSES["CAND-ARCH-01"]
        self.assertIn("Kafka", senior_resp.technical_answer)
        self.assertGreaterEqual(senior_resp.formulation_pause_sec, 2.0)
        self.assertIn("solve_two_sum", senior_resp.machine_test_code)


class TestSimulationEnvironment(unittest.TestCase):
    def setUp(self):
        self.sim = EndToEndSimulationEnvironment()

    def test_senior_candidate_pipeline_simulation(self):
        report = self.sim.simulate_candidate("CAND-ARCH-01")
        self.assertEqual(report.candidate_id, "CAND-ARCH-01")
        self.assertEqual(len(report.stages), 5)
        self.assertEqual(report.final_verdict, "STRONG_HIRE")
        self.assertGreaterEqual(report.final_composite_score, 85.0)
        self.assertTrue(len(report.cryptographic_seal) == 64)
        self.assertGreaterEqual(report.adverse_impact_ratio, 0.80)

    def test_mid_candidate_pipeline_simulation(self):
        report = self.sim.simulate_candidate("CAND-MID-02")
        self.assertEqual(report.candidate_id, "CAND-MID-02")
        self.assertEqual(report.final_verdict, "OFFER")
        self.assertGreaterEqual(report.final_composite_score, 60.0)

    def test_junior_candidate_pipeline_simulation(self):
        report = self.sim.simulate_candidate("CAND-JUNIOR-03")
        self.assertEqual(report.candidate_id, "CAND-JUNIOR-03")
        self.assertIn(report.final_verdict, ["HOLD", "REJECT"])

    def test_mismatched_candidate_pipeline_simulation(self):
        report = self.sim.simulate_candidate("CAND-MISMATCH-04")
        self.assertEqual(report.candidate_id, "CAND-MISMATCH-04")
        self.assertEqual(report.final_verdict, "REJECT")
        self.assertLess(report.final_composite_score, 50.0)

    def test_run_all_simulations(self):
        all_reports = self.sim.run_all_simulations()
        self.assertEqual(len(all_reports), 4)
        verdicts = [r.final_verdict for r in all_reports]
        self.assertIn("STRONG_HIRE", verdicts)
        self.assertIn("OFFER", verdicts)
        self.assertIn("REJECT", verdicts)


if __name__ == "__main__":
    unittest.main()
