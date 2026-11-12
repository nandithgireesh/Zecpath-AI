"""
Zecpath-AI: Day 51 - Cross-Round Aggregation Engine Package
===========================================================
Exports unified 5-stage aggregation modules:
- AssessmentStage, RoleWeightProfile, CandidateProfileTier, HiringDecision, ReadinessTier
- UnifiedCandidateScoreObject, StageScoreInput, StageScoreContribution
- HiringFitCalculator
- CrossRoundAggregationEngine, STANDARD_ROLE_PROFILES
"""

from .models import (
    AssessmentStage,
    RoleWeightProfile,
    CandidateProfileTier,
    HiringDecision,
    ReadinessTier,
    StageScoreInput,
    StageWeightSpecification,
    CrossStageWeightConfig,
    StageScoreContribution,
    RadarDimensionScore,
    RiskDiscountTelemetry,
    UnifiedCandidateScoreObject,
)
from .hiring_fit_calculator import HiringFitCalculator
from .aggregation_engine import (
    CrossRoundAggregationEngine,
    STANDARD_ROLE_PROFILES,
)

__all__ = [
    "AssessmentStage",
    "RoleWeightProfile",
    "CandidateProfileTier",
    "HiringDecision",
    "ReadinessTier",
    "StageScoreInput",
    "StageWeightSpecification",
    "CrossStageWeightConfig",
    "StageScoreContribution",
    "RadarDimensionScore",
    "RiskDiscountTelemetry",
    "UnifiedCandidateScoreObject",
    "HiringFitCalculator",
    "CrossRoundAggregationEngine",
    "STANDARD_ROLE_PROFILES",
]
