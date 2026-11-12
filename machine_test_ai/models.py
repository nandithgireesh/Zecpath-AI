"""
Zecpath-AI: Day 50 - Machine Test AI Design
===========================================
Data models, enumerations, and telemetry schemas for real-world machine tests:
1. Machine Test Types: Coding Problems, Debugging Tasks, File-Based Tasks, Mini System Design
2. Evaluation Metrics: Correctness, Efficiency, Code Quality, Problem-Solving Approach
3. Input/Output Capture: Code Snapshots, Execution Telemetry, Sandbox Traces
4. Time-Based Scoring: Baseline Baselines, Decay Constants, Time Penalties/Bonuses

Curriculum Reference: Day 50 - Machine Test AI Design
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import time
import hashlib


# ==============================================================================
# 1. CORE ENUMERATIONS
# ==============================================================================

class MachineTestType(str, Enum):
    """Four distinct archetypes of real-world technical assessments."""
    CODING_PROBLEM = "CODING_PROBLEM"          # Algorithmic & data structure challenges
    DEBUGGING_TASK = "DEBUGGING_TASK"          # Diagnosing and repairing defective codebases
    FILE_BASED_TASK = "FILE_BASED_TASK"        # Real-world ETL, log parsing, file IO
    MINI_SYSTEM_DESIGN = "MINI_SYSTEM_DESIGN"  # Modular architecture, rate limiting, in-memory caches


class MetricDimension(str, Enum):
    """The four foundational evaluation pillars."""
    CORRECTNESS = "CORRECTNESS"                      # Test suite pass rate, edge cases, assertion coverage
    EFFICIENCY = "EFFICIENCY"                        # Time/space complexity, latency, memory footprint
    CODE_QUALITY = "CODE_QUALITY"                    # Linting, cyclomatic complexity, modularity, readability
    PROBLEM_SOLVING_APPROACH = "PROBLEM_SOLVING"     # Incremental evolution, debugging agility, commit cadence


class DifficultyTier(str, Enum):
    """Task complexity classification."""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    SYSTEM_ARCHITECT = "SYSTEM_ARCHITECT"


class SnapshotEventType(str, Enum):
    """Granular action classification for timeline recording."""
    TYPING_INCREMENTAL = "TYPING_INCREMENTAL"
    PASTE_BLOCK = "PASTE_BLOCK"
    RUN_TESTS = "RUN_TESTS"
    SYNTAX_ERROR_RECOVERY = "SYNTAX_ERROR_RECOVERY"
    REFACTOR = "REFACTOR"


# ==============================================================================
# 2. INPUT / OUTPUT CAPTURE TELEMETRY SCHEMAS
# ==============================================================================

class CodeSnapshot(BaseModel):
    """Temporal snapshot of candidate code state at point in time t."""
    snapshot_id: str
    timestamp_offset_seconds: float = Field(..., ge=0.0, description="Offset from task start")
    code_content: str
    character_count: int
    line_count: int
    diff_chars_from_previous: int = 0
    event_type: SnapshotEventType = SnapshotEventType.TYPING_INCREMENTAL
    tests_triggered: bool = False
    tests_passed_count: int = 0
    total_tests_count: int = 0


class TestCaseResult(BaseModel):
    """Result of an individual test assertion."""
    test_id: str
    test_name: str
    is_hidden: bool = False
    passed: bool
    execution_time_ms: float
    memory_peak_kb: float
    error_message: Optional[str] = None
    stdout_output: Optional[str] = None


class ExecutionResult(BaseModel):
    """Captured sandbox execution telemetry and stdout/stderr artifacts."""
    execution_id: str
    exit_code: int
    total_test_cases: int
    passed_test_cases: int
    failed_test_cases: int
    wall_clock_time_ms: float
    peak_memory_mb: float
    cyclomatic_complexity: int
    pep8_violations_count: int
    test_details: List[TestCaseResult] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


# ==============================================================================
# 3. TASK DEFINITION SCHEMA
# ==============================================================================

class MachineTestTask(BaseModel):
    """Specification of an interactive machine assessment problem."""
    task_id: str
    task_type: MachineTestType
    title: str
    description: str
    difficulty: DifficultyTier
    starter_code: str
    reference_solution: Optional[str] = None
    expected_baseline_minutes: float = Field(..., description="Target benchmark completion time")
    max_timeout_minutes: float = Field(..., description="Hard cutoff halting time")
    max_memory_limit_mb: float = 128.0
    max_execution_time_limit_ms: float = 2000.0
    rubric_weights: Dict[MetricDimension, float] = Field(
        default_factory=lambda: {
            MetricDimension.CORRECTNESS: 0.40,
            MetricDimension.EFFICIENCY: 0.20,
            MetricDimension.CODE_QUALITY: 0.20,
            MetricDimension.PROBLEM_SOLVING_APPROACH: 0.20,
        }
    )


# ==============================================================================
# 4. TIME-BASED SCORING & COMPOSITE TELEMETRY
# ==============================================================================

class TimeEfficiencyTelemetry(BaseModel):
    """Quantitative evaluation of pacing, speed, and time compliance."""
    actual_duration_minutes: float
    baseline_duration_minutes: float
    time_ratio: float  # actual / baseline
    speed_factor: float  # Non-linear scalar multiplier
    bonus_points: float = 0.0
    penalty_points: float = 0.0
    is_timeout_breached: bool = False
    pacing_verdict: str  # e.g., "HIGH_VELOCITY", "OPTIMAL_PACE", "EXTENDED_OVERTIME"


class DimensionScoreBreakdown(BaseModel):
    """Detailed score for one of the four foundational dimensions."""
    dimension: MetricDimension
    raw_score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float = Field(..., ge=0.0, le=100.0)
    sub_metrics: Dict[str, float] = Field(default_factory=dict)
    diagnostics: List[str] = Field(default_factory=list)


class TaskEvaluationResult(BaseModel):
    """Comprehensive evaluation dossier for a completed machine test task."""
    task_id: str
    task_type: MachineTestType
    task_title: str
    candidate_id: str
    submission_timestamp: float
    time_telemetry: TimeEfficiencyTelemetry
    dimension_breakdowns: Dict[MetricDimension, DimensionScoreBreakdown]
    base_composite_score: float = Field(..., ge=0.0, le=100.0)
    final_time_adjusted_score: float = Field(..., ge=0.0, le=100.0)
    grade_verdict: str  # e.g., "EXEMPLARY", "PROFICIENT", "NEEDS_IMPROVEMENT", "UNSATISFACTORY"
    audit_hash_sha256: str
    summary_remarks: str
