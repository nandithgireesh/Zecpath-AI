"""
Day 41: Unified Scoring Engine Package
======================================
Provides end-to-end multi-round hiring intelligence combining:
1. ATS Resume Matching (Days 1 to 20)
2. Conversational Pre-Screening (Days 21 to 32)
3. In-Depth HR Interview (Days 33 to 40)
"""

from .models import (
    RoundType,
    RoleFamily,
    HiringDecisionTier,
    ReadinessLevel,
    RoundScoreInput,
    CrossRoundWeightProfile,
    RoundContribution,
    HiringFitBreakdown,
    UnifiedCandidateScoreObject,
)
from .weight_system import CrossRoundWeightSystem, WeightConfigurationError
from .hiring_fit_calculator import HiringFitCalculator
from .unified_score_object import UnifiedScoreObjectFormatter
from .cross_round_engine import UnifiedScoringEngine

__all__ = [
    "RoundType",
    "RoleFamily",
    "HiringDecisionTier",
    "ReadinessLevel",
    "RoundScoreInput",
    "CrossRoundWeightProfile",
    "RoundContribution",
    "HiringFitBreakdown",
    "UnifiedCandidateScoreObject",
    "CrossRoundWeightSystem",
    "WeightConfigurationError",
    "HiringFitCalculator",
    "UnifiedScoreObjectFormatter",
    "UnifiedScoringEngine",
]
