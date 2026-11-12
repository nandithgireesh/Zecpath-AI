"""
Zecpath-AI: Technical Interview AI Package
==========================================
Role-Based Technical Interview Engine & Scoring Model for scalable candidate evaluations.

Curriculum Reference:
- Day 46: Technical Interview System Design
- Day 47: Technical Skill Scoring Model
"""

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    InterviewFlowState,
    SubTurnAction,
    RecommendationVerdict,
    CandidateProfile,
    TechnicalInterviewConfig,
    TechnicalEvaluationRubric,
    TechnicalInterviewAIBlueprint,
)

from tech_interview.question_hierarchy import (
    QuestionNode,
    SkillDomainDefinition,
    ROLE_SKILL_DOMAINS,
    CURATED_QUESTION_BANK,
    DynamicDifficultyProgressionEngine,
    QuestionHierarchyRepository,
)

from tech_interview.flow_engine import (
    LEGAL_STATE_TRANSITIONS,
    InterviewTurnRecord,
    StateTransitionEvent,
    TechnicalInterviewReport,
    TechnicalInterviewFlowEngine,
)

from tech_interview.scoring_models import (
    ScoringParameter,
    AnswerDepthClassification,
    SkillProficiencyLevel,
    QuestionTypeRubric,
    QUESTION_TYPE_RUBRICS,
    ShallowAnswerDiagnostics,
    ParameterScoreBreakdown,
    NormalizedTurnScore,
    ExplainableScoringOutput,
    SkillDomainScore,
    TechnicalEvaluationReportFormat,
)

from tech_interview.scoring_engine import TechnicalSkillScoringEngine

__all__ = [
    # Day 46 System Design
    "JobRole",
    "ExperienceTier",
    "QuestionCategory",
    "DifficultyLevel",
    "BloomsTaxonomyLevel",
    "InterviewFlowState",
    "SubTurnAction",
    "RecommendationVerdict",
    "CandidateProfile",
    "TechnicalInterviewConfig",
    "TechnicalEvaluationRubric",
    "TechnicalInterviewAIBlueprint",
    "QuestionNode",
    "SkillDomainDefinition",
    "ROLE_SKILL_DOMAINS",
    "CURATED_QUESTION_BANK",
    "DynamicDifficultyProgressionEngine",
    "QuestionHierarchyRepository",
    "LEGAL_STATE_TRANSITIONS",
    "InterviewTurnRecord",
    "StateTransitionEvent",
    "TechnicalInterviewReport",
    "TechnicalInterviewFlowEngine",
    # Day 47 Technical Skill Scoring Model
    "ScoringParameter",
    "AnswerDepthClassification",
    "SkillProficiencyLevel",
    "QuestionTypeRubric",
    "QUESTION_TYPE_RUBRICS",
    "ShallowAnswerDiagnostics",
    "ParameterScoreBreakdown",
    "NormalizedTurnScore",
    "ExplainableScoringOutput",
    "SkillDomainScore",
    "TechnicalEvaluationReportFormat",
    "TechnicalSkillScoringEngine",
]
