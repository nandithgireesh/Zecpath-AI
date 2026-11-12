import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from screening_ai.eligibility_engine import EligibilityDecisionEngine
from screening_ai.eligibility_config import EligibilityRuleConfig, get_rule_config_for_role


class TestEligibilityDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = EligibilityDecisionEngine()
        self.custom_config = EligibilityRuleConfig(
            role_name="Backend Python Developer",
            min_ats_score=70.0,
            review_ats_score=55.0,
            mandatory_skills=["Python", "FastAPI", "PostgreSQL"],
            min_experience_years=2.0,
            max_experience_years=6.0,
            allowed_locations=["Bangalore", "Remote"],
            max_notice_period_days=30,
            allow_remote=True,
        )

    def test_eligible_candidate(self):
        candidate = {
            "candidate_id": "CAND-001",
            "name": "Alice Smith",
            "ats_score": 85.0,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            "total_experience": "3.5 years",
            "location": "Bangalore, India",
            "notice_period_days": 15,
        }
        res = self.engine.evaluate_candidate(candidate, self.custom_config)
        self.assertEqual(res["status"], "ELIGIBLE")
        self.assertEqual(res["call_priority"], "HIGH")
        self.assertTrue(res["checks"]["mandatory_skills_passed"])
        self.assertTrue(res["checks"]["ats_score_cutoff_met"])

    def test_missing_mandatory_skills_rejected(self):
        candidate = {
            "candidate_id": "CAND-002",
            "name": "Bob Jones",
            "ats_score": 75.0,
            "skills": ["Java", "Spring Boot", "MySQL"],
            "total_experience": "4.0 years",
            "location": "Remote",
        }
        res = self.engine.evaluate_candidate(candidate, self.custom_config)
        self.assertEqual(res["status"], "REJECTED")
        self.assertFalse(res["checks"]["mandatory_skills_passed"])
        self.assertIn("Python", res["missing_mandatory_skills"])

    def test_borderline_ats_score_review(self):
        candidate = {
            "candidate_id": "CAND-003",
            "name": "Charlie Brown",
            "ats_score": 62.0,  # in [55.0, 70.0)
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "total_experience": "2.5 years",
            "location": "Bangalore",
        }
        res = self.engine.evaluate_candidate(candidate, self.custom_config)
        self.assertEqual(res["status"], "REVIEW")
        self.assertEqual(res["call_priority"], "LOW")

    def test_below_cutoff_rejected(self):
        candidate = {
            "candidate_id": "CAND-004",
            "name": "David Miller",
            "ats_score": 45.0,  # Below 55.0
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "total_experience": "2.0 years",
            "location": "Bangalore",
        }
        res = self.engine.evaluate_candidate(candidate, self.custom_config)
        self.assertEqual(res["status"], "REJECTED")

    def test_location_mismatch(self):
        strict_config = EligibilityRuleConfig(
            role_name="Onsite Role",
            min_ats_score=70.0,
            review_ats_score=50.0,
            mandatory_skills=["Python"],
            allowed_locations=["Kochi", "Trivandrum"],
            allow_remote=False,
        )
        candidate = {
            "candidate_id": "CAND-005",
            "ats_score": 80.0,
            "skills": ["Python"],
            "location": "Mumbai",
        }
        res = self.engine.evaluate_candidate(candidate, strict_config)
        self.assertEqual(res["status"], "REJECTED")
        self.assertFalse(res["checks"]["location_passed"])

    def test_batch_evaluation_and_summary(self):
        candidates = [
            {
                "candidate_id": "C1",
                "ats_score": 88.0,
                "skills": ["React", "Node.js", "MongoDB", "JavaScript"],
                "total_experience": "2 years",
            },
            {
                "candidate_id": "C2",
                "ats_score": 60.0,
                "skills": ["React", "Node.js", "MongoDB", "JavaScript"],
                "total_experience": "1 year",
            },
            {
                "candidate_id": "C3",
                "ats_score": 35.0,
                "skills": ["PHP"],
                "total_experience": "0 years",
            },
        ]
        mern_config = get_rule_config_for_role("MERN Stack Developer")
        batch_res = self.engine.batch_evaluate(candidates, mern_config)

        self.assertEqual(batch_res["summary"]["total_candidates_evaluated"], 3)
        self.assertEqual(batch_res["summary"]["eligible_count"], 1)
        self.assertEqual(batch_res["summary"]["review_count"], 1)
        self.assertEqual(batch_res["summary"]["rejected_count"], 1)
        self.assertEqual(batch_res["eligible_candidates"][0]["candidate_id"], "C1")


if __name__ == "__main__":
    unittest.main()
