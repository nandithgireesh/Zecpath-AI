"""
Day 37: HR Interview AI Module
==============================
Exposes core models, question generation, state flow controllers,
communication evaluators, behavioral confidence analyzers, and scoring engines
for the AI HR interview platform.
"""

from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    FollowUpTriggerReason,
    FollowUpProbeCategory,
    AdaptationTier,
    HRQuestionTemplate,
    InterviewTurnState,
    HRInterviewConfig,
    HRInterviewSession,
    CommunicationScoreBreakdown,
)
from interview_ai.confidence_models import (
    HesitationType,
    HesitationSignal,
    SentimentPolarity,
    SentimentTone,
    SentimentTurnScore,
    ContradictionSeverity,
    ContradictionIncident,
    StressLevel,
    StressIndicators,
    ConfidenceTier,
    TurnConfidenceBreakdown,
    SessionConfidenceSummary,
)
from interview_ai.sentiment_scoring_engine import InterviewSentimentScorer
from interview_ai.confidence_analyzer import (
    HesitationPatternDetector,
    ContradictionDetector,
    StressIndicatorScorer,
    ConfidenceAnalyzer,
)
from interview_ai.hr_question_generator import (
    HRQuestionBank,
    HRQuestionGenerator,
)
from interview_ai.dynamic_followup_engine import (
    VaguenessAmbiguityAnalyzer,
    DynamicFollowUpEngine,
)
from interview_ai.communication_evaluator import (
    FluencyAnalyzer,
    GrammarQualityAnalyzer,
    VocabularyAnalyzer,
    ClarityAnalyzer,
    FillerWordDetector,
    AnswerStructureAnalyzer,
    CommunicationEvaluator,
)
from interview_ai.hr_scoring_models import (
    ScoringParameter,
    HiringRecommendation,
    RoleTrackPreset,
    WeightProfile,
    TurnRelevanceEvaluation,
    LengthNormalizationMetadata,
    ParameterContribution,
    CandidateHRScoreReport,
)
from interview_ai.weight_config import (
    WeightConfigurationSystem,
    WeightConfigurationError,
)
from interview_ai.hr_scoring_engine import (
    AnswerRelevanceAnalyzer,
    LengthNormalizationEngine,
    HRInterviewScoringEngine,
)
from interview_ai.hr_score_report import HRScoreReportFormatter
from interview_ai.hr_flow_engine import HRInterviewFlowEngine
from interview_ai.aptitude_models import (
    CognitiveDimension,
    ScenarioCategory,
    CognitiveMaturityLevel,
    FrameworkType,
    IdealAnswerStructure,
    ReasoningQuestion,
    SituationalScenario,
    LogicalReasoningBreakdown,
    ProblemSolvingClarityBreakdown,
    ScenarioEvaluationResult,
)
from interview_ai.logical_reasoning_scorer import LogicalReasoningScorer
from interview_ai.scenario_evaluator import (
    ProblemSolvingClarityAnalyzer,
    ScenarioEvaluator,
)
from interview_ai.aptitude_engine import AptitudeAIEngine
from interview_ai.summary_models import (
    CulturalFitDimension,
    InconsistencyType,
    InconsistencySeverity,
    InconsistencyFlag,
    CulturalFitAssessment,
    OverallHRPerformanceSummary,
    NaturalLanguageDossier,
    CandidateInterviewSummary,
)
from interview_ai.inconsistency_detector import InconsistencyDetector
from interview_ai.interview_summary_generator import InterviewSummaryGenerator
from interview_ai.interview import interview
from interview_ai.simulation_models import (
    CandidateArchetype,
    HumanExpertPanelScore,
    SimulatedCandidateProfile,
    SimulationTurnData,
    SessionSimulationResult,
    DiscrepancyAnalysis,
    AccuracyBenchmarkReport,
)
from interview_ai.simulation_engine import HRInterviewSimulationEngine
from interview_ai.accuracy_evaluator import AccuracyEvaluator

__all__ = [
    "HRCategory",
    "ExperienceTier",
    "RoleTrack",
    "InterviewPhase",
    "FollowUpTriggerReason",
    "FollowUpProbeCategory",
    "AdaptationTier",
    "HRQuestionTemplate",
    "InterviewTurnState",
    "CommunicationScoreBreakdown",
    "HRInterviewConfig",
    "HRInterviewSession",
    "HesitationType",
    "HesitationSignal",
    "SentimentPolarity",
    "SentimentTone",
    "SentimentTurnScore",
    "ContradictionSeverity",
    "ContradictionIncident",
    "StressLevel",
    "StressIndicators",
    "ConfidenceTier",
    "TurnConfidenceBreakdown",
    "SessionConfidenceSummary",
    "InterviewSentimentScorer",
    "HesitationPatternDetector",
    "ContradictionDetector",
    "StressIndicatorScorer",
    "ConfidenceAnalyzer",
    "HRQuestionBank",
    "HRQuestionGenerator",
    "VaguenessAmbiguityAnalyzer",
    "DynamicFollowUpEngine",
    "FluencyAnalyzer",
    "GrammarQualityAnalyzer",
    "VocabularyAnalyzer",
    "ClarityAnalyzer",
    "FillerWordDetector",
    "AnswerStructureAnalyzer",
    "CommunicationEvaluator",
    "ScoringParameter",
    "HiringRecommendation",
    "RoleTrackPreset",
    "WeightProfile",
    "TurnRelevanceEvaluation",
    "LengthNormalizationMetadata",
    "ParameterContribution",
    "CandidateHRScoreReport",
    "WeightConfigurationSystem",
    "WeightConfigurationError",
    "AnswerRelevanceAnalyzer",
    "LengthNormalizationEngine",
    "HRInterviewScoringEngine",
    "HRScoreReportFormatter",
    "HRInterviewFlowEngine",
    "CognitiveDimension",
    "ScenarioCategory",
    "CognitiveMaturityLevel",
    "FrameworkType",
    "IdealAnswerStructure",
    "ReasoningQuestion",
    "SituationalScenario",
    "LogicalReasoningBreakdown",
    "ProblemSolvingClarityBreakdown",
    "ScenarioEvaluationResult",
    "LogicalReasoningScorer",
    "ProblemSolvingClarityAnalyzer",
    "ScenarioEvaluator",
    "AptitudeAIEngine",
    "CulturalFitDimension",
    "InconsistencyType",
    "InconsistencySeverity",
    "InconsistencyFlag",
    "CulturalFitAssessment",
    "OverallHRPerformanceSummary",
    "NaturalLanguageDossier",
    "CandidateInterviewSummary",
    "InconsistencyDetector",
    "InterviewSummaryGenerator",
    "interview",
    "CandidateArchetype",
    "HumanExpertPanelScore",
    "SimulatedCandidateProfile",
    "SimulationTurnData",
    "SessionSimulationResult",
    "DiscrepancyAnalysis",
    "AccuracyBenchmarkReport",
    "HRInterviewSimulationEngine",
    "AccuracyEvaluator",
    # Day 42: Optimization & Stability
    "TranscriptCleaner",
    "CleaningResult",
    "StableHRFlowEngine",
    "FlowGuardConfig",
    "DynamicProbeDecision",
    "RefinedDecisionTier",
    "LevelingUpgradeTier",
    "CognitiveDeliberationMetric",
    "BoundedPenaltyBreakdown",
    "RefinedScoreSummary",
    "RefinedScoringEngine",
    "OptimizationBenchmarkSuite",
    "OptimizationReportData",
    "MicrobenchmarkMetric",
    "AccuracyComparisonMetric",
]

# Day 42 Imports
from interview_ai.transcript_cleaner import TranscriptCleaner, CleaningResult
from interview_ai.stable_hr_flow_engine import (
    StableHRFlowEngine,
    FlowGuardConfig,
    DynamicProbeDecision,
)
from interview_ai.refined_scoring_models import (
    RefinedDecisionTier,
    LevelingUpgradeTier,
    CognitiveDeliberationMetric,
    BoundedPenaltyBreakdown,
    RefinedScoreSummary,
)
from interview_ai.refined_scoring_engine import RefinedScoringEngine
from interview_ai.optimization_benchmarks import (
    OptimizationBenchmarkSuite,
    OptimizationReportData,
    MicrobenchmarkMetric,
    AccuracyComparisonMetric,
)


