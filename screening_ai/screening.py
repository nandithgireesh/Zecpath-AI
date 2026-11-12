"""
screening_ai/screening.py

Main interface for Day 21 & Day 22 Screening Decision & Question AI.
Coordinates candidate eligibility checks and dynamic AI screening question generation.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from screening_ai.eligibility_engine import EligibilityDecisionEngine
from screening_ai.eligibility_config import EligibilityRuleConfig, get_rule_config_for_role
from screening_ai.question_bank import ScreeningQuestionBank
from screening_ai.question_models import ScreeningCallScript


# ==========================================
# Day 21: Eligibility Helpers
# ==========================================

def evaluate_eligibility(
    candidate: Dict[str, Any],
    role_name: Optional[str] = None,
    custom_rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a single candidate's screening eligibility.
    """
    if custom_rules:
        config = EligibilityRuleConfig.from_dict(custom_rules)
    elif role_name:
        config = get_rule_config_for_role(role_name)
    else:
        config = EligibilityRuleConfig()

    engine = EligibilityDecisionEngine()
    return engine.evaluate_candidate(candidate, config)


def batch_evaluate_eligibility(
    candidates: List[Dict[str, Any]],
    role_name: Optional[str] = None,
    custom_rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to batch evaluate candidates and produce an eligibility report.
    """
    if custom_rules:
        config = EligibilityRuleConfig.from_dict(custom_rules)
    elif role_name:
        config = get_rule_config_for_role(role_name)
    else:
        config = EligibilityRuleConfig()

    engine = EligibilityDecisionEngine()
    return engine.batch_evaluate(candidates, config)


# ==========================================
# Day 22: Question Bank & Call Script Helpers
# ==========================================

_GLOBAL_QUESTION_BANK: Optional[ScreeningQuestionBank] = None


def get_question_bank() -> ScreeningQuestionBank:
    """Retrieve or initialize singleton ScreeningQuestionBank instance."""
    global _GLOBAL_QUESTION_BANK
    if _GLOBAL_QUESTION_BANK is None:
        _GLOBAL_QUESTION_BANK = ScreeningQuestionBank()
    return _GLOBAL_QUESTION_BANK


def get_screening_questions_for_role(role_name: str) -> Dict[str, Any]:
    """Retrieve categorized questions relevant for a given job role."""
    bank = get_question_bank()
    categorized = bank.get_questions_for_role(role_name)
    return {
        category: [q.model_dump() for q in q_list]
        for category, q_list in categorized.items()
    }


def generate_candidate_screening_script(
    candidate_data: Dict[str, Any],
    role_name: str = "Software Engineer",
    job_location: str = "Bangalore",
    language: str = "en",
) -> ScreeningCallScript:
    """Generate a structured, ready-to-run conversational call script for AI screening calls."""
    bank = get_question_bank()
    return bank.generate_call_script(
        candidate_data=candidate_data,
        role_name=role_name,
        job_location=job_location,
        language=language,
    )


if __name__ == "__main__":
    sample_candidate = {
        "candidate_id": "CAND-001",
        "name": "Nandith Gireesh",
        "ats_score": 85.0,
        "skills": ["Python", "TensorFlow", "Pandas", "Machine Learning", "SQL"],
        "total_experience": "2.5 years",
        "location": "Kerala, Remote",
    }

    print("\n1. Evaluating Eligibility (Day 21):")
    res_eligibility = evaluate_eligibility(sample_candidate, role_name="Machine Learning Engineer")
    print(f"Status: {res_eligibility['status']} | Priority: {res_eligibility['call_priority']}")

    print("\n2. Generating Call Script (Day 22):")
    script = generate_candidate_screening_script(
        sample_candidate, role_name="Machine Learning Engineer", language="en"
    )
    print(f"Total Stages: {script.total_stages} | Est. Duration: {script.estimated_call_duration_minutes} min")
    for item in script.script_items[:4]:
        print(f"  [{item.stage_id}] ({item.category}): {item.rendered_prompt}")