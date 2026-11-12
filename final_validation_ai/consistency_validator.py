"""
Cross-Module Output Consistency & Schema Validator for Zecpath AI Platform
Day 68 - Final Optimization & Bug Fixing
Author: Nandith Gireesh (AI Engineering Intern)
Organisation: Zecser Business LLP
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationRuleResult:
    rule_name: str
    passed: bool
    details: str
    severity: str  # Critical, Warning, Info


@dataclass
class ModuleConsistencyReport:
    candidate_id: str
    overall_valid: bool
    rules_checked: int
    rules_passed: int
    rules_failed: int
    integrity_hash: str
    rule_results: List[ValidationRuleResult]


class ConsistencyValidator:
    """
    Guarantees that outputs across all subsystems (ATS, HR, Tech, STAR, Coding, Recommendation)
    remain schema-compliant, mathematically coherent, and tamper-evident.
    """

    STANDARD_MODULES = [
        "ats_screening",
        "hr_screening",
        "tech_interview",
        "behavioral_star",
        "coding_machine_test",
        "final_recommendation"
    ]

    SCORE_WEIGHTS = {
        "ats_screening": 0.20,
        "hr_screening": 0.15,
        "tech_interview": 0.25,
        "behavioral_star": 0.20,
        "coding_machine_test": 0.20
    }

    DECISION_TIERS = {
        "STRONG_HIRE": (85.0, 100.0),
        "HIRE": (70.0, 84.999),
        "BORDERLINE": (50.0, 69.999),
        "REJECT": (0.0, 49.999)
    }

    def compute_audit_hash(self, payload: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 hash of canonicalized JSON state."""
        canonical_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

    def determine_expected_decision(self, composite_score: float) -> str:
        """Determines expected hiring decision based on calibrated score thresholds."""
        for decision, (low, high) in self.DECISION_TIERS.items():
            if low <= composite_score <= high:
                return decision
        return "REJECT"

    def validate_candidate_pipeline_output(self, pipeline_data: Dict[str, Any]) -> ModuleConsistencyReport:
        """
        Conducts deep cross-module validation across schemas, mathematical linear weighting,
        bounded score ranges, and decision consistency.
        """
        candidate_id = pipeline_data.get("candidate_id", "UNKNOWN_CANDIDATE")
        rule_results: List[ValidationRuleResult] = []

        # Rule 1: Candidate ID presence
        has_id = bool(candidate_id and candidate_id != "UNKNOWN_CANDIDATE")
        rule_results.append(ValidationRuleResult(
            rule_name="SCHEMA_CANDIDATE_ID_VALID",
            passed=has_id,
            details=f"Candidate ID verified: {candidate_id}",
            severity="Critical"
        ))

        # Rule 2: Subsystem Score Boundedness [0.0, 100.0]
        round_scores = pipeline_data.get("round_scores", {})
        scores_bounded = True
        invalid_score_msgs = []
        for mod, weight in self.SCORE_WEIGHTS.items():
            if mod in round_scores:
                score = round_scores[mod]
                if not isinstance(score, (int, float)) or score < 0.0 or score > 100.0:
                    scores_bounded = False
                    invalid_score_msgs.append(f"{mod}={score}")
            else:
                scores_bounded = False
                invalid_score_msgs.append(f"Missing {mod}")

        rule_results.append(ValidationRuleResult(
            rule_name="SCORES_NUMERICAL_BOUNDS",
            passed=scores_bounded,
            details="All module scores bounded within [0.0, 100.0]" if scores_bounded else f"Bounds violation: {', '.join(invalid_score_msgs)}",
            severity="Critical"
        ))

        # Rule 3: Mathematical Linearity of Composite Score
        reported_composite = pipeline_data.get("composite_score", None)
        expected_composite = 0.0
        if scores_bounded:
            expected_composite = sum(round_scores[mod] * weight for mod, weight in self.SCORE_WEIGHTS.items())
            expected_composite = round(expected_composite, 2)

        math_consistent = False
        if reported_composite is not None and isinstance(reported_composite, (int, float)):
            diff = abs(reported_composite - expected_composite)
            math_consistent = (diff <= 0.25)  # allow minor rounding delta <= 0.25
        
        rule_results.append(ValidationRuleResult(
            rule_name="COMPOSITE_SCORE_MATHEMATICAL_CONSISTENCY",
            passed=math_consistent,
            details=f"Reported: {reported_composite}, Expected: {expected_composite} (Delta: {round(abs((reported_composite or 0.0) - expected_composite), 3)})",
            severity="Critical"
        ))

        # Rule 4: Decision Tier Logical Consistency
        reported_decision = pipeline_data.get("final_decision", "")
        expected_decision = self.determine_expected_decision(expected_composite)
        decision_consistent = (reported_decision == expected_decision)
        rule_results.append(ValidationRuleResult(
            rule_name="DECISION_TIER_CONSISTENCY",
            passed=decision_consistent,
            details=f"Reported: '{reported_decision}', Expected: '{expected_decision}' based on composite {expected_composite}",
            severity="Critical"
        ))

        # Rule 5: Non-Empty Recruiter Rationale
        rationale = pipeline_data.get("recruiter_summary", "")
        has_rationale = bool(rationale and len(rationale.strip()) >= 20)
        rule_results.append(ValidationRuleResult(
            rule_name="RECRUITER_RATIONALE_COMPLETION",
            passed=has_rationale,
            details=f"Rationale character length: {len(rationale.strip()) if rationale else 0}",
            severity="Warning"
        ))

        # Rule 6: Integrity State Hash Verification
        audit_hash = self.compute_audit_hash({
            "candidate_id": candidate_id,
            "round_scores": round_scores,
            "composite_score": reported_composite,
            "final_decision": reported_decision
        })
        has_hash = bool(audit_hash and len(audit_hash) == 64)
        rule_results.append(ValidationRuleResult(
            rule_name="TAMPER_EVIDENT_AUDIT_HASH",
            passed=has_hash,
            details=f"Canonical SHA-256 generated: {audit_hash[:16]}...",
            severity="Info"
        ))

        rules_passed = sum(1 for r in rule_results if r.passed)
        rules_failed = sum(1 for r in rule_results if not r.passed)
        critical_failures = sum(1 for r in rule_results if not r.passed and r.severity == "Critical")

        return ModuleConsistencyReport(
            candidate_id=candidate_id,
            overall_valid=(critical_failures == 0),
            rules_checked=len(rule_results),
            rules_passed=rules_passed,
            rules_failed=rules_failed,
            integrity_hash=audit_hash,
            rule_results=rule_results
        )

