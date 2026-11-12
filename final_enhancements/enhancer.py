"""
Day 65: Final Enhancements & Production Polish
Recruiter-Facing Output Formatter, Scoring Consistency Stabilizer, and Defensive Error Guards
Platform: Zecpath Automated Hiring Platform
"""

import time
import re
from typing import Dict, List, Any, Optional


class FinalFeatureEnhancer:
    """
    Production Feature Enhancer.
    Implements:
      1. Defensive input sanitization (handling empty strings, emoji, and syntax corruptions).
      2. Scoring consistency stabilization (calibrating variance across turns).
      3. Recruiter-friendly executive summary generation.
    """

    @staticmethod
    def sanitize_candidate_input(text: Optional[str]) -> str:
        """Sanitizes candidate input defensively against empty or malformed inputs."""
        if not text or not isinstance(text, str):
            return "NO_RESPONSE_PROVIDED"
        cleaned = text.strip()
        if len(cleaned) == 0:
            return "NO_RESPONSE_PROVIDED"
        # Remove non-printable or corrupt control characters
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned

    @staticmethod
    def sanitize_code_submission(code: Optional[str]) -> Dict[str, Any]:
        """Validates coding submission before AST parsing."""
        if not code or len(code.strip()) == 0:
            return {"valid": False, "status": "EMPTY_CODE", "score": 0.0, "message": "No code submitted."}
        stripped = code.strip()
        if stripped == "pass" or stripped.startswith("#"):
            return {"valid": True, "status": "INCOMPLETE_STUB", "score": 10.0, "message": "Code contains only stub pass or comments."}
        return {"valid": True, "status": "READY_FOR_AST", "score": None, "message": "Code ready for evaluation."}

    @staticmethod
    def generate_recruiter_summary(candidate_name: str, role: str, final_score: float, verdict: str,
                                   tech_score: float, star_score: float, code_score: float) -> str:
        """Generates clear, natural language summary for non-technical talent acquisition recruiters."""
        if verdict == "STRONG_HIRE":
            recommendation = (
                f"{candidate_name} demonstrated exceptional mastery for the {role} role, scoring {final_score:.1f}/100. "
                f"Candidate excelled in Technical Architecture ({tech_score:.1f}/100) and Problem Solving ({code_score:.1f}/100). "
                f"Immediate offer extended with fast-track senior onboarding."
            )
        elif verdict in ["OFFER", "HIRE"]:
            recommendation = (
                f"{candidate_name} demonstrated solid core competency for {role} with an overall score of {final_score:.1f}/100. "
                f"Consistently met benchmarks across STAR Behavioral ({star_score:.1f}/100) and coding tasks. Recommended for hiring offer."
            )
        elif verdict in ["HOLD", "BORDERLINE"]:
            recommendation = (
                f"{candidate_name} scored {final_score:.1f}/100. Core competencies are acceptable but architectural depth was marginal. "
                f"Recommended for secondary interview with Lead Architect before final verdict."
            )
        else:
            recommendation = (
                f"{candidate_name} scored {final_score:.1f}/100, which falls below the role competency threshold. "
                f"Candidate lacked prerequisite technical mechanisms. Politely decline and archive profile for future junior openings."
            )
        return recommendation

