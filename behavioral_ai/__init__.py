"""
Zecpath-AI: Behavioral AI Module
================================
Autonomous Behavioral AI Research & Design Subsystem (Day 48).
Evaluates candidate behavior during interviews using observable signals:
- Eye movement & gaze stability
- Head movement & kinematics
- Facial engagement Action Units
- Attention patterns & dispersion
- Measurable indicators (Focus, Distraction, Nervousness)
- Non-invasive ethical scoring with statutory compliance (BIPA, EU AI Act, NYC Local Law 144)
"""

from behavioral_ai.models import (
    GazeDirection,
    HeadPoseMovement,
    FacialEngagementState,
    BehavioralInsightCategory,
    EthicalScoringClassification,
    EyeMovementTelemetry,
    HeadKinematicsTelemetry,
    FacialEngagementTelemetry,
    AttentionPatternTelemetry,
    RawTurnBehavioralSignals,
    MeasurableBehavioralIndicators,
    TurnBehavioralScore,
    BehavioralAnalysisReportFormat,
)
from behavioral_ai.mapping_model import (
    BehavioralSignalMappingEngine,
)
from behavioral_ai.framework import (
    BehavioralAnalysisFramework,
)
from behavioral_ai.design_document import (
    BehavioralAIDesignDocument,
)

__all__ = [
    "GazeDirection",
    "HeadPoseMovement",
    "FacialEngagementState",
    "BehavioralInsightCategory",
    "EthicalScoringClassification",
    "EyeMovementTelemetry",
    "HeadKinematicsTelemetry",
    "FacialEngagementTelemetry",
    "AttentionPatternTelemetry",
    "RawTurnBehavioralSignals",
    "MeasurableBehavioralIndicators",
    "TurnBehavioralScore",
    "BehavioralAnalysisReportFormat",
    "BehavioralSignalMappingEngine",
    "BehavioralAnalysisFramework",
    "BehavioralAIDesignDocument",
]
