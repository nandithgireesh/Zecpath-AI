"""
Day 41: Cross-Round Unified Scoring Engine (Deliverable 1)
=========================================================
Integrates telemetry across all three enterprise evaluation phases:
1. Round 1: ATS Resume & Skill Matching (Days 1 to 20)
2. Round 2: Conversational Pre-Screening Call (Days 21 to 32)
3. Round 3: In-Depth HR Interview & Situational Aptitude (Days 33 to 40)

Applies role-tailored cross-round weight systems, evaluates safety gates,
calculates hiring fit percentage, and constructs the Unified Candidate Score Object.
"""

import os
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from .models import (
    RoundType,
    RoleFamily,
    RoundScoreInput,
    CrossRoundWeightProfile,
    UnifiedCandidateScoreObject,
)
from .weight_system import CrossRoundWeightSystem
from .hiring_fit_calculator import HiringFitCalculator
from .unified_score_object import UnifiedScoreObjectFormatter


class UnifiedScoringEngine:
    """
    Deliverable 1: Master engine unifying ATS, Screening, and HR Interview scores
    into a coherent, calibrated, and audit-compliant hiring intelligence evaluation.
    """

    def __init__(self, output_dir: str = "data/unified_scores"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.weight_system = CrossRoundWeightSystem()
        self.calculator = HiringFitCalculator()
        self.formatter = UnifiedScoreObjectFormatter()

    def build_ats_round_input(
        self,
        ats_score: Union[float, Dict[str, Any]],
        strengths: Optional[List[str]] = None,
        flags: Optional[List[str]] = None,
        doc_id: Optional[str] = None,
    ) -> RoundScoreInput:
        """Constructs standardized RoundScoreInput for Round 1 (ATS Resume)."""
        if isinstance(ats_score, (int, float)):
            score_val = float(ats_score)
            dims = {"skill_score": score_val, "experience_score": score_val}
        elif isinstance(ats_score, dict):
            score_val = float(ats_score.get("final_ats_score", ats_score.get("score", 70.0)))
            dims = {
                "skill_score": float(ats_score.get("skill_score", score_val)),
                "experience_score": float(ats_score.get("experience_score", score_val)),
                "education_score": float(ats_score.get("education_score", score_val)),
                "semantic_score": float(ats_score.get("semantic_score", score_val)),
            }
        else:
            score_val = getattr(ats_score, "final_ats_score", 70.0)
            dims = {"skill_score": score_val, "experience_score": score_val}

        extracted_strengths = strengths or (ats_score.get("strengths") if isinstance(ats_score, dict) else None)
        extracted_flags = flags or (ats_score.get("flags_or_penalties") or ats_score.get("flags") if isinstance(ats_score, dict) else None)

        return RoundScoreInput(
            round_type=RoundType.ATS_RESUME,
            round_name="ATS Resume & Skill Matching (Round 1)",
            raw_score=max(0.0, min(100.0, score_val)),
            normalized_score=max(0.0, min(100.0, score_val)),
            confidence_weight=1.0,
            dimension_breakdown=dims,
            strengths=extracted_strengths or ["Strong keyword skill alignment with job description."],
            flags_or_penalties=extracted_flags or [],
            source_session_or_doc_id=doc_id,
        )

    def build_screening_round_input(
        self,
        screening_score: Union[float, Dict[str, Any]],
        strengths: Optional[List[str]] = None,
        flags: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> RoundScoreInput:
        """Constructs standardized RoundScoreInput for Round 2 (Conversational Screening)."""
        if isinstance(screening_score, (int, float)):
            score_val = float(screening_score)
            dims = {
                "clarity_score": score_val,
                "relevance_score": score_val,
                "behavioral_score": score_val,
                "consistency_score": score_val,
            }
        elif isinstance(screening_score, dict):
            score_val = float(screening_score.get("overall_score", screening_score.get("score", 70.0)))
            dims = {
                "clarity_score": float(screening_score.get("clarity_score", score_val)),
                "relevance_score": float(screening_score.get("relevance_score", score_val)),
                "behavioral_score": float(screening_score.get("behavioral_score", score_val)),
                "consistency_score": float(screening_score.get("consistency_score", score_val)),
            }
        else:
            score_val = getattr(screening_score, "overall_score", 70.0)
            dims = {"clarity_score": score_val, "behavioral_score": score_val}

        extracted_strengths = strengths or (screening_score.get("strengths") if isinstance(screening_score, dict) else None)
        extracted_flags = flags or (screening_score.get("flags_or_penalties") or screening_score.get("flags") if isinstance(screening_score, dict) else None)

        return RoundScoreInput(
            round_type=RoundType.CONVERSATIONAL_SCREENING,
            round_name="Conversational Pre-Screening (Round 2)",
            raw_score=max(0.0, min(100.0, score_val)),
            normalized_score=max(0.0, min(100.0, score_val)),
            confidence_weight=1.0,
            dimension_breakdown=dims,
            strengths=extracted_strengths or ["Satisfied baseline communication and role eligibility requirements."],
            flags_or_penalties=extracted_flags or [],
            source_session_or_doc_id=session_id,
        )

    def build_hr_round_input(
        self,
        hr_score: Union[float, Dict[str, Any]],
        strengths: Optional[List[str]] = None,
        flags: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> RoundScoreInput:
        """Constructs standardized RoundScoreInput for Round 3 (HR Interview)."""
        if isinstance(hr_score, (int, float)):
            score_val = float(hr_score)
            dims = {
                "behavioral_score": score_val,
                "communication_score": score_val,
                "confidence_score": score_val,
                "aptitude_score": score_val,
                "cultural_fit": score_val,
            }
        elif isinstance(hr_score, dict):
            score_val = float(hr_score.get("composite_score", hr_score.get("score", 70.0)))
            dims = {
                "behavioral_score": float(hr_score.get("behavioral_score", score_val)),
                "communication_score": float(hr_score.get("communication_score", score_val)),
                "confidence_score": float(hr_score.get("confidence_score", score_val)),
                "aptitude_score": float(hr_score.get("aptitude_score", score_val)),
                "cultural_fit": float(hr_score.get("cultural_fit", score_val)),
            }
        else:
            score_val = getattr(hr_score, "composite_score", 70.0)
            dims = {"behavioral_score": score_val, "communication_score": score_val}

        extracted_strengths = strengths or (hr_score.get("strengths") if isinstance(hr_score, dict) else None)
        extracted_flags = flags or (hr_score.get("flags_or_penalties") or hr_score.get("flags") if isinstance(hr_score, dict) else None)

        return RoundScoreInput(
            round_type=RoundType.HR_INTERVIEW,
            round_name="In-Depth HR Interview & Aptitude (Round 3)",
            raw_score=max(0.0, min(100.0, score_val)),
            normalized_score=max(0.0, min(100.0, score_val)),
            confidence_weight=1.0,
            dimension_breakdown=dims,
            strengths=extracted_strengths or ["Demonstrated competency in structured problem-solving and situational triage."],
            flags_or_penalties=extracted_flags or [],
            source_session_or_doc_id=session_id,
        )

    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        experience_years: float,
        ats_input: Union[float, Dict[str, Any], RoundScoreInput],
        screening_input: Union[float, Dict[str, Any], RoundScoreInput],
        hr_input: Union[float, Dict[str, Any], RoundScoreInput],
        weight_profile: Optional[CrossRoundWeightProfile] = None,
        save_artifacts: bool = True,
    ) -> UnifiedCandidateScoreObject:
        """
        Executes end-to-end multi-round evaluation and synthesizes the Unified Candidate Score Object.
        """
        # 1. Normalize Round Inputs
        round_inputs: Dict[RoundType, RoundScoreInput] = {}

        if isinstance(ats_input, RoundScoreInput):
            round_inputs[RoundType.ATS_RESUME] = ats_input
        else:
            round_inputs[RoundType.ATS_RESUME] = self.build_ats_round_input(ats_input)

        if isinstance(screening_input, RoundScoreInput):
            round_inputs[RoundType.CONVERSATIONAL_SCREENING] = screening_input
        else:
            round_inputs[RoundType.CONVERSATIONAL_SCREENING] = self.build_screening_round_input(screening_input)

        if isinstance(hr_input, RoundScoreInput):
            round_inputs[RoundType.HR_INTERVIEW] = hr_input
        else:
            round_inputs[RoundType.HR_INTERVIEW] = self.build_hr_round_input(hr_input)

        # 2. Resolve Cross-Round Weight Profile
        profile = weight_profile or self.weight_system.resolve_profile_for_role(target_role)

        # 3. Calculate Round Contributions & Safety Gates
        contributions, composite_score, gates_passed, failure_reasons = (
            self.calculator.calculate_round_contributions(round_inputs, profile)
        )

        # 4. Calculate Multi-Dimensional Hiring Fit
        hiring_fit = self.calculator.calculate_hiring_fit(round_inputs, composite_score)

        # 5. Synthesize Final Decision, Readiness, and Leveling
        decision, readiness, role_tier, verdict = self.calculator.synthesize_decision(
            hiring_fit=hiring_fit,
            all_gates_passed=gates_passed,
            candidate_experience_years=experience_years,
            target_role=target_role,
        )

        # 6. Aggregate Strengths & Developmental Focus Areas
        all_strengths = []
        all_dev_areas = []
        for r_inp in round_inputs.values():
            all_strengths.extend(r_inp.strengths)
            all_dev_areas.extend(r_inp.flags_or_penalties)

        # Deduplicate while preserving order
        unique_strengths = list(dict.fromkeys(all_strengths))
        unique_dev_areas = list(dict.fromkeys(all_dev_areas))

        # 7. Generate Audit Metadata
        audit_str = f"{candidate_id}:{target_role}:{composite_score}:{datetime.now().isoformat()}"
        audit_hash = hashlib.sha256(audit_str.encode("utf-8")).hexdigest()[:16].upper()

        score_obj = UnifiedCandidateScoreObject(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            role_family=profile.role_family,
            evaluation_date=datetime.now().isoformat(),
            round_inputs=round_inputs,
            weight_profile_used=profile,
            round_contributions=contributions,
            composite_score=composite_score,
            hiring_fit=hiring_fit,
            final_decision=decision,
            readiness_level=readiness,
            calibrated_role_tier=role_tier,
            executive_verdict=verdict,
            key_strengths=unique_strengths[:5],
            developmental_areas=unique_dev_areas[:5],
            safety_gate_passed=gates_passed,
            gate_failure_reasons=failure_reasons,
            audit_metadata={
                "audit_hash": f"ZEC-UNIFIED-{audit_hash}",
                "engine_version": "2.0-unified",
                "calibration_standard": "Enterprise Bar Raiser v2.0",
            },
        )

        # 8. Persist Artifacts (JSON & Recruiter Markdown)
        if save_artifacts:
            json_path = os.path.join(self.output_dir, f"{candidate_id}_unified_score.json")
            md_path = os.path.join(self.output_dir, f"{candidate_id}_unified_score.md")

            with open(json_path, "w", encoding="utf-8") as f:
                f.write(self.formatter.to_ats_json(score_obj))
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self.formatter.to_recruiter_markdown(score_obj))

        return score_obj
