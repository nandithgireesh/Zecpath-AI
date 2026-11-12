"""
Zecpath-AI: Day 50 - Machine Test AI Package
============================================
Exported modules and data models for Machine Test AI System:
- Framework orchestrator
- Evaluation engine (4 foundational pillars)
- Time-based scoring engine
- Real-world task registry
"""

from .models import (
    MachineTestType,
    MetricDimension,
    DifficultyTier,
    SnapshotEventType,
    CodeSnapshot,
    TestCaseResult,
    ExecutionResult,
    MachineTestTask,
    TimeEfficiencyTelemetry,
    DimensionScoreBreakdown,
    TaskEvaluationResult,
)
from .evaluation_engine import TaskEvaluationEngine
from .time_scoring import TimeBasedScoringEngine
from .framework import (
    MachineTestAIFramework,
    CURATED_MACHINE_TASKS,
)

__all__ = [
    "MachineTestType",
    "MetricDimension",
    "DifficultyTier",
    "SnapshotEventType",
    "CodeSnapshot",
    "TestCaseResult",
    "ExecutionResult",
    "MachineTestTask",
    "TimeEfficiencyTelemetry",
    "DimensionScoreBreakdown",
    "TaskEvaluationResult",
    "TaskEvaluationEngine",
    "TimeBasedScoringEngine",
    "MachineTestAIFramework",
    "CURATED_MACHINE_TASKS",
]
