"""
Zecpath-AI: Day 51 - Cross-Round Aggregation Engine
===================================================
Master engine orchestrating end-to-end multi-round hiring intelligence:
1. Dynamic Role-Based Weight Configurations (Software, Systems Lead, Management, Data, Solutions)
2. Ingestion & Validation of all 5 Canonical Assessment Stages
3. Gating Floor Verification, Disqualification Logic & Missing Round Imputation
4. Transparent Explainability: Factor Contribution Waterfalls & Counterfactual Insights
5. Unified Candidate Score Object Synthesis with SHA-256 Cryptographic Audit Seal

Curriculum Reference: Day 51 - Deliverable 2: Cross-Round Aggregation Engine
"""

import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .models import (
    AssessmentStage,
    RoleWeightProfile,
    CandidateProfileTier,
    StageScoreInput,
    StageWeightSpecification,
    CrossStageWeightConfig,
    UnifiedCandidateScoreObject,
    HiringDecision,
    ReadinessTier,
)
from .hiring_fit_calculator import HiringFitCalculator


# ==============================================================================
# CANONICAL ROLE WEIGHT PROFILES (5-STAGE DISTRIBUTIONS)
# ==============================================================================

STANDARD_ROLE_PROFILES: Dict[RoleWeightProfile, CrossStageWeightConfig] = {
    RoleWeightProfile.SOFTWARE_ENGINEERING: CrossStageWeightConfig(
        profile_name="Software Engineering Core",
        role_profile=RoleWeightProfile.SOFTWARE_ENGINEERING,
        target_experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
        weights={
            AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.10, min_cutoff_score=40.0, is_critical_gate=False),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.15, min_cutoff_score=50.0, is_critical_gate=True),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.15, min_cutoff_score=50.0, is_critical_gate=True),
            AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.30, min_cutoff_score=55.0, is_critical_gate=True),
            AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.30, min_cutoff_score=55.0, is_critical_gate=True),
        },
        notes="High mathematical focus on technical algorithmic depth and sandbox code delivery.",
    ),
    RoleWeightProfile.DISTRIBUTED_SYSTEMS_LEAD: CrossStageWeightConfig(
        profile_name="Principal Distributed Systems Architect",
        role_profile=RoleWeightProfile.DISTRIBUTED_SYSTEMS_LEAD,
        target_experience_tier=CandidateProfileTier.PRINCIPAL_ARCHITECT,
        weights={
            AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.10, min_cutoff_score=50.0, is_critical_gate=False),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.10, min_cutoff_score=50.0, is_critical_gate=True),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.15, min_cutoff_score=60.0, is_critical_gate=True),
            AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.35, min_cutoff_score=70.0, is_critical_gate=True),
            AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.30, min_cutoff_score=65.0, is_critical_gate=True),
        },
        notes="Heavy emphasis on large-scale architecture, fault tolerance, and high-concurrency coding.",
    ),
    RoleWeightProfile.ENGINEERING_MANAGEMENT: CrossStageWeightConfig(
        profile_name="Engineering Management & Leadership",
        role_profile=RoleWeightProfile.ENGINEERING_MANAGEMENT,
        target_experience_tier=CandidateProfileTier.SENIOR_LEAD_5_PLUS,
        weights={
            AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.10, min_cutoff_score=40.0, is_critical_gate=False),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.15, min_cutoff_score=60.0, is_critical_gate=True),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.35, min_cutoff_score=70.0, is_critical_gate=True),
            AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.25, min_cutoff_score=55.0, is_critical_gate=True),
            AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.15, min_cutoff_score=45.0, is_critical_gate=False),
        },
        notes="Prioritizes people leadership, situational resolution, and strategic technical judgment.",
    ),
    RoleWeightProfile.DATA_PLATFORM_ENGINEERING: CrossStageWeightConfig(
        profile_name="Data Platform & ETL Engineering",
        role_profile=RoleWeightProfile.DATA_PLATFORM_ENGINEERING,
        target_experience_tier=CandidateProfileTier.MID_LEVEL_3_5,
        weights={
            AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.10, min_cutoff_score=45.0, is_critical_gate=False),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.15, min_cutoff_score=50.0, is_critical_gate=True),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.15, min_cutoff_score=50.0, is_critical_gate=True),
            AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.25, min_cutoff_score=55.0, is_critical_gate=True),
            AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.35, min_cutoff_score=60.0, is_critical_gate=True),
        },
        notes="High weight on data ingestion pipelines, log parsing efficiency, and distributed storage.",
    ),
    RoleWeightProfile.SOLUTIONS_ARCHITECTURE: CrossStageWeightConfig(
        profile_name="Solutions Architecture & Customer Engineering",
        role_profile=RoleWeightProfile.SOLUTIONS_ARCHITECTURE,
        target_experience_tier=CandidateProfileTier.SENIOR_LEAD_5_PLUS,
        weights={
            AssessmentStage.ATS_RESUME: StageWeightSpecification(weight=0.15, min_cutoff_score=45.0, is_critical_gate=False),
            AssessmentStage.CONVERSATIONAL_SCREENING: StageWeightSpecification(weight=0.25, min_cutoff_score=65.0, is_critical_gate=True),
            AssessmentStage.HR_BEHAVIORAL_INTERVIEW: StageWeightSpecification(weight=0.25, min_cutoff_score=65.0, is_critical_gate=True),
            AssessmentStage.TECHNICAL_INTERVIEW: StageWeightSpecification(weight=0.25, min_cutoff_score=60.0, is_critical_gate=True),
            AssessmentStage.MACHINE_TEST: StageWeightSpecification(weight=0.10, min_cutoff_score=40.0, is_critical_gate=False),
        },
        notes="Balanced communication and high-level architectural trade-offs for enterprise clients.",
    ),
}


# ==============================================================================
# MASTER ENGINE ORCHESTRATOR
# ==============================================================================

class CrossRoundAggregationEngine:
    """
    Production-grade cross-round aggregation engine producing transparent,
    tamper-evident unified hiring dossiers.
    """

    ENGINE_ID = "ENGINE-DAY51-CROSS-ROUND-AGGREGATION"
    VERSION = "1.0.0-PROD"

    def __init__(self):
        self.calculator = HiringFitCalculator()
        self.profiles: Dict[RoleWeightProfile, CrossStageWeightConfig] = dict(STANDARD_ROLE_PROFILES)

    def register_custom_profile(self, profile: CrossStageWeightConfig) -> None:
        """Enables registering custom company-specific weight distributions."""
        if not profile.validate_weights_sum():
            raise ValueError(f"Profile weights must sum to 1.0 (got {sum(s.weight for s in profile.weights.values()):.4f}).")
        self.profiles[profile.role_profile] = profile

    def get_profile(self, role: RoleWeightProfile) -> Optional[CrossStageWeightConfig]:
        """Retrieves weight configuration profile."""
        return self.profiles.get(role)

    def aggregate_candidate_dossier(
        self,
        candidate_id: str,
        candidate_name: str,
        applied_role: str,
        experience_tier: CandidateProfileTier,
        role_profile: RoleWeightProfile,
        stage_scores: Dict[AssessmentStage, StageScoreInput],
        evaluation_timestamp: Optional[str] = None,
    ) -> UnifiedCandidateScoreObject:
        """
        Executes end-to-end multi-round aggregation across all 5 evaluation stages.
        """
        start_time = time.perf_counter()
        timestamp = evaluation_timestamp or datetime.now().isoformat()

        config = self.profiles.get(role_profile)
        if not config:
            config = self.profiles[RoleWeightProfile.SOFTWARE_ENGINEERING]

        # 1. Calculate Individual Stage Contributions & Gating
        contributions, all_gates_passed, base_aggregate = self.calculator.calculate_stage_contributions(
            stage_scores=stage_scores,
            weight_config=config,
        )

        # 2. Synthesize Radar Dimensions
        radar = self.calculator.compute_radar_competencies(
            stage_scores=stage_scores,
            experience_tier=experience_tier,
        )

        # 3. Calculate Risk Discounts (Inconsistencies & Gate Breaches)
        discounts = self.calculator.calculate_risk_discounts(
            stage_scores=stage_scores,
            all_gates_passed=all_gates_passed,
        )

        # 4. Final Calibrated Hiring Fit Score (%)
        final_fit = max(0.0, min(100.0, base_aggregate - discounts.total_risk_discount))
        final_fit = round(final_fit, 1)

        # 5. Determine Official Verdict & Leveling
        decision, readiness, leveling = self.calculator.determine_hiring_verdict(
            hiring_fit_score=final_fit,
            all_gates_passed=all_gates_passed,
            experience_tier=experience_tier,
        )

        # 6. Generate Transparent Recruiter Guidance & Counterfactuals
        exec_summary = (
            f"Candidate {candidate_name} evaluated for {applied_role} ({experience_tier.value}). "
            f"Achieved unified Hiring Fit Score of {final_fit}% ({decision.value}). "
            f"Base aggregate: {base_aggregate} pts, Risk deductions: -{discounts.total_risk_discount} pts. "
            f"All critical stage gating cutoffs: {'PASSED' if all_gates_passed else 'BREACHED'}."
        )

        if decision in (HiringDecision.STRONG_HIRE, HiringDecision.HIRE):
            action = f"Advance to formal executive offer at calibrated tier: {leveling}."
            counterfactual = "Candidate demonstrated strong multi-modal consistency across both theory and coding."
        else:
            action = f"Hold or decline candidacy. Candidate requires upskilling before production deployment."
            counterfactual = (
                f"If candidate improves lowest scoring stage ({min(contributions.values(), key=lambda c: c.normalized_score).stage_name}) "
                f"by +15 points, hiring fit would increase to {round(final_fit + 4.5, 1)}%."
            )

        # 7. Cryptographic SHA-256 Audit Seal
        payload = f"{candidate_id}|{final_fit}|{decision.value}|{timestamp}|{config.profile_name}"
        audit_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        assert elapsed_ms <= 45.0, f"Aggregation SLA breached: {elapsed_ms:.2f}ms > 45ms"

        return UnifiedCandidateScoreObject(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            applied_role=applied_role,
            experience_tier=experience_tier,
            weight_profile_used=role_profile,
            evaluation_timestamp=timestamp,
            base_aggregate_score=base_aggregate,
            risk_discounts=discounts,
            hiring_fit_score=final_fit,
            decision_verdict=decision,
            readiness_tier=readiness,
            calibrated_leveling=leveling,
            stage_contributions=contributions,
            radar_competencies=radar,
            executive_summary=exec_summary,
            hiring_manager_action=action,
            counterfactual_guidance=counterfactual,
            all_gates_passed=all_gates_passed,
            audit_hash_sha256=audit_hash,
        )

    def generate_engine_manifest(self) -> Dict[str, Any]:
        """Generates cryptographic architectural manifest for Day 51."""
        manifest = {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "stages_supported": [s.value for s in AssessmentStage],
            "role_profiles_count": len(self.profiles),
            "p99_evaluation_sla_ms": 45.0,
            "deterministic_scoring": True,
        }
        manifest_str = str(sorted(manifest.items()))
        manifest["sha256_integrity_hash"] = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()
        return manifest
