"""
Zecpath-AI: Day 52 - Final Recommendation AI Module
===================================================
Orchestrates enterprise hiring outcome decisions:
- Decision categories: Selected, Hold / Review, Rejected
- Rule + Score Hybrid Logic
- Quantified Decision Confidence Scoring (0 - 100%)
- Multi-dimensional Risk Factor Telemetry (Behavior & Integrity)
- Explainable outputs with counterfactual guidance
- Cryptographic SHA-256 Audit Seal
"""

from final_recommendation_ai.models import (
    FinalDecisionCategory,
    DecisionSubStatus,
    OverallRiskLevel,
    ConfidenceBand,
    RuleStatus,
    BehavioralRiskFactor,
    IntegrityRiskFactor,
    RiskFactorsTelemetry,
    EvaluatedRule,
    DecisionConfidenceTelemetry,
    ExplainableDriver,
    CounterfactualGuidance,
    CandidateDecisionOutput,
)
from final_recommendation_ai.recommendation_logic import RecommendationLogicEngine
from final_recommendation_ai.decision_engine import FinalDecisionAIEngine

__all__ = [
    "FinalDecisionCategory",
    "DecisionSubStatus",
    "OverallRiskLevel",
    "ConfidenceBand",
    "RuleStatus",
    "BehavioralRiskFactor",
    "IntegrityRiskFactor",
    "RiskFactorsTelemetry",
    "EvaluatedRule",
    "DecisionConfidenceTelemetry",
    "ExplainableDriver",
    "CounterfactualGuidance",
    "CandidateDecisionOutput",
    "RecommendationLogicEngine",
    "FinalDecisionAIEngine",
]
