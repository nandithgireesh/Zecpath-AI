import os
import sys
import json
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from screening_ai.eligibility_engine import EligibilityDecisionEngine
from screening_ai.eligibility_config import get_rule_config_for_role


class TestEligibilityRealData(unittest.TestCase):

    def setUp(self):
        self.engine = EligibilityDecisionEngine()
        self.profiles_dir = "data/parsed_profiles"

    def test_evaluate_real_candidates(self):
        candidates = []

        # Load candidates from data/parsed_profiles
        if os.path.exists(self.profiles_dir):
            for fname in os.listdir(self.profiles_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.profiles_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            # Add synthetic/parsed ATS score if missing for test
                            if "ats_score" not in data:
                                if "strong" in fname.lower() or "resume 1" in fname.lower():
                                    data["ats_score"] = 86.5
                                elif "partial" in fname.lower() or "resume 2" in fname.lower():
                                    data["ats_score"] = 62.0
                                else:
                                    data["ats_score"] = 42.0
                            data["candidate_id"] = fname.replace(".json", "")
                            candidates.append(data)
                        except Exception:
                            pass

        # Fallback if no parsed files
        if not candidates:
            candidates = [
                {
                    "candidate_id": "Resume 1",
                    "name": "Jisto C S",
                    "skills": ["Python", "SQL", "TensorFlow", "Pandas", "Transformers"],
                    "total_experience": "1.5 years",
                    "location": "Thrissur, Kerala",
                    "ats_score": 88.0,
                },
                {
                    "candidate_id": "Resume 2",
                    "name": "Alex Kumar",
                    "skills": ["Python", "HTML", "CSS"],
                    "total_experience": "0.5 years",
                    "location": "Bangalore",
                    "ats_score": 58.0,
                },
                {
                    "candidate_id": "Resume 3",
                    "name": "Sam Taylor",
                    "skills": ["Sales", "Communication"],
                    "total_experience": "3.0 years",
                    "location": "Delhi",
                    "ats_score": 38.0,
                },
            ]

        # Evaluate against Machine Learning Engineer Role
        config = get_rule_config_for_role("Machine Learning Engineer")
        report = self.engine.batch_evaluate(candidates, config)

        output_path = "data/screening_output/eligibility_decision_report.json"
        saved_file = self.engine.save_report(report, output_path)

        self.assertTrue(os.path.exists(saved_file))
        self.assertGreater(report["summary"]["total_candidates_evaluated"], 0)
        self.assertIn("eligible_candidates", report)
        self.assertIn("summary", report)

        print("\n========== DAY 21 ELIGIBILITY EVALUATION REPORT ==========")
        print(f"Role Evaluated   : {report['summary']['role']}")
        print(f"Total Candidates : {report['summary']['total_candidates_evaluated']}")
        print(f"Eligible (Calls) : {report['summary']['eligible_count']}")
        print(f"Review Required  : {report['summary']['review_count']}")
        print(f"Rejected         : {report['summary']['rejected_count']}")
        print(f"Eligibility Rate : {report['summary']['eligibility_rate_percentage']}%")
        print(f"Report File      : {saved_file}")
        print("==========================================================")


if __name__ == "__main__":
    unittest.main()
