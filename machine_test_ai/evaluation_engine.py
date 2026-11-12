"""
Zecpath-AI: Day 50 - Task Evaluation Logic Engine
=================================================
Automated evaluation engine analyzing candidate submissions across the four
mandated evaluation pillars:
1. Correctness: Test suite pass rates, hidden edge cases, assertion coverage
2. Efficiency: Algorithmic complexity, wall-clock execution time, peak memory usage
3. Code Quality: Modularity, cyclomatic complexity, PEP 8 hygiene, type annotations
4. Problem-Solving Approach: Snapshot cadence, iterative debugging, copy-paste velocity

Curriculum Reference: Day 50 - Deliverable 2: Task Evaluation Logic
"""

import math
import re
import ast
from typing import List, Dict, Tuple, Optional, Any
from .models import (
    MachineTestType,
    MetricDimension,
    CodeSnapshot,
    ExecutionResult,
    DimensionScoreBreakdown,
    MachineTestTask,
    SnapshotEventType,
)


class TaskEvaluationEngine:
    """
    Core algorithmic evaluator assessing real-world technical submissions
    via deterministic telemetry extraction and semantic code inspection.
    """

    def __init__(self):
        pass

    # ==========================================================================
    # 1. PILLAR 1: CORRECTNESS EVALUATION
    # ==========================================================================

    def evaluate_correctness(
        self,
        execution_result: ExecutionResult,
        task: MachineTestTask,
    ) -> DimensionScoreBreakdown:
        """
        Evaluates functional correctness based on visible and hidden assertions.
        """
        diagnostics = []
        if execution_result.total_test_cases == 0:
            return DimensionScoreBreakdown(
                dimension=MetricDimension.CORRECTNESS,
                raw_score=0.0,
                weight=task.rubric_weights.get(MetricDimension.CORRECTNESS, 0.40),
                weighted_score=0.0,
                sub_metrics={"pass_rate": 0.0, "edge_case_score": 0.0},
                diagnostics=["Critical: No test assertions executed."],
            )

        # Baseline pass rate
        pass_ratio = execution_result.passed_test_cases / execution_result.total_test_cases
        base_correctness = pass_ratio * 100.0

        # Separate visible vs hidden edge cases
        visible_tests = [t for t in execution_result.test_details if not t.is_hidden]
        hidden_tests = [t for t in execution_result.test_details if t.is_hidden]

        hidden_pass_ratio = 1.0
        if hidden_tests:
            hidden_passed = sum(1 for t in hidden_tests if t.passed)
            hidden_pass_ratio = hidden_passed / len(hidden_tests)
            if hidden_pass_ratio < 1.0:
                diagnostics.append(
                    f"Failed {len(hidden_tests) - hidden_passed}/{len(hidden_tests)} hidden edge-case assertions."
                )

        # Penalty for timeout or unhandled exceptions
        exit_code_penalty = 0.0
        if execution_result.timed_out:
            exit_code_penalty = 35.0
            diagnostics.append("Process timed out before completing test suite (-35.0 pts).")
        elif execution_result.exit_code != 0:
            exit_code_penalty = 20.0
            diagnostics.append(f"Non-zero exit code ({execution_result.exit_code}) encountered (-20.0 pts).")

        raw_score = max(0.0, min(100.0, base_correctness - exit_code_penalty))
        weight = task.rubric_weights.get(MetricDimension.CORRECTNESS, 0.40)
        weighted_score = round(raw_score * weight, 2)

        diagnostics.append(
            f"Functional Assertions: {execution_result.passed_test_cases}/{execution_result.total_test_cases} passed ({base_correctness:.1f}%)."
        )

        return DimensionScoreBreakdown(
            dimension=MetricDimension.CORRECTNESS,
            raw_score=round(raw_score, 2),
            weight=weight,
            weighted_score=weighted_score,
            sub_metrics={
                "pass_rate_pct": round(pass_ratio * 100, 2),
                "hidden_pass_pct": round(hidden_pass_ratio * 100, 2),
                "exit_code_penalty": exit_code_penalty,
            },
            diagnostics=diagnostics,
        )

    # ==========================================================================
    # 2. PILLAR 2: EFFICIENCY EVALUATION
    # ==========================================================================

    def evaluate_efficiency(
        self,
        execution_result: ExecutionResult,
        final_code: str,
        task: MachineTestTask,
    ) -> DimensionScoreBreakdown:
        """
        Evaluates latency, memory footprint, and asymptotic algorithmic efficiency.
        """
        diagnostics = []

        # 1. Execution Latency Factor (Max budget = max_execution_time_limit_ms)
        latency = execution_result.wall_clock_time_ms
        latency_ratio = min(2.0, latency / max(1.0, task.max_execution_time_limit_ms))
        if latency_ratio <= 0.25:
            latency_score = 100.0
            diagnostics.append(f"Sub-25% execution budget ({latency:.1f}ms): High execution efficiency.")
        elif latency_ratio <= 0.60:
            latency_score = 85.0
            diagnostics.append(f"Moderate latency consumption ({latency:.1f}ms): Acceptable efficiency.")
        elif latency_ratio <= 1.0:
            latency_score = 65.0
            diagnostics.append(f"High latency consumption ({latency:.1f}ms): Near timeout threshold.")
        else:
            latency_score = 30.0
            diagnostics.append(f"Severe latency bottleneck ({latency:.1f}ms): Exceeded soft budget.")

        # 2. Memory Footprint Factor
        mem_mb = execution_result.peak_memory_mb
        mem_ratio = mem_mb / max(1.0, task.max_memory_limit_mb)
        if mem_ratio <= 0.30:
            memory_score = 100.0
        elif mem_ratio <= 0.70:
            memory_score = 80.0
        else:
            memory_score = 50.0
            diagnostics.append(f"High memory overhead ({mem_mb:.1f}MB / {task.max_memory_limit_mb:.0f}MB budget).")

        # 3. Algorithmic Complexity Heuristic (Ast inspection for nested loops)
        complexity_score = 90.0
        try:
            tree = ast.parse(final_code)
            nested_depth = self._calculate_loop_nesting_depth(tree)
            if nested_depth >= 3:
                complexity_score = 50.0
                diagnostics.append(f"Detected cubic or higher O(N^{nested_depth}) nested looping pattern.")
            elif nested_depth == 2:
                # O(N^2)
                complexity_score = 75.0
                diagnostics.append("Detected quadratic O(N^2) nested loop construct.")
            else:
                complexity_score = 95.0
                diagnostics.append(f"Linear or sub-linear O(N) loop hierarchy (depth {nested_depth}).")
        except Exception:
            complexity_score = 75.0

        # Weighted aggregate for efficiency
        raw_score = (latency_score * 0.40) + (memory_score * 0.30) + (complexity_score * 0.30)
        raw_score = max(0.0, min(100.0, raw_score))
        weight = task.rubric_weights.get(MetricDimension.EFFICIENCY, 0.20)

        return DimensionScoreBreakdown(
            dimension=MetricDimension.EFFICIENCY,
            raw_score=round(raw_score, 2),
            weight=weight,
            weighted_score=round(raw_score * weight, 2),
            sub_metrics={
                "latency_score": latency_score,
                "memory_score": memory_score,
                "complexity_score": complexity_score,
                "wall_clock_ms": latency,
                "peak_memory_mb": mem_mb,
            },
            diagnostics=diagnostics,
        )

    # ==========================================================================
    # 3. PILLAR 3: CODE QUALITY EVALUATION
    # ==========================================================================

    def evaluate_code_quality(
        self,
        final_code: str,
        execution_result: ExecutionResult,
        task: MachineTestTask,
    ) -> DimensionScoreBreakdown:
        """
        Assesses structural modularity, cyclomatic complexity, and stylistic hygiene.
        """
        diagnostics = []

        # 1. Cyclomatic Complexity Score
        cyclo = execution_result.cyclomatic_complexity
        if cyclo <= 5:
            cyclo_score = 100.0
        elif cyclo <= 10:
            cyclo_score = 85.0
        elif cyclo <= 15:
            cyclo_score = 65.0
            diagnostics.append(f"Moderate cyclomatic complexity ({cyclo}): Consider breaking down branching.")
        else:
            cyclo_score = 40.0
            diagnostics.append(f"High cyclomatic complexity ({cyclo}): High cognitive load / branching density.")

        # 2. PEP 8 & Linter Hygiene
        violations = execution_result.pep8_violations_count
        linter_penalty = min(50.0, violations * 5.0)
        linter_score = max(50.0, 100.0 - linter_penalty)
        if violations > 0:
            diagnostics.append(f"Identified {violations} style/lint violations (-{linter_penalty:.0f} pts).")
        else:
            diagnostics.append("Zero style or lint violations: Clean formatting.")

        # 3. Modularity & Documentation
        docstring_count = len(re.findall(r'(""".*?"""|\'\'\'.*?\'\'\')', final_code, re.DOTALL))
        type_hints_count = len(re.findall(r':\s*(int|str|float|bool|List|Dict|Optional|Tuple|Any)', final_code))
        function_defs = len(re.findall(r'def\s+\w+\(', final_code))

        modularity_score = 70.0
        if function_defs >= 2:
            modularity_score += 15.0
        if docstring_count >= 1:
            modularity_score += 10.0
        if type_hints_count >= 2:
            modularity_score += 5.0
        modularity_score = min(100.0, modularity_score)

        raw_score = (cyclo_score * 0.35) + (linter_score * 0.35) + (modularity_score * 0.30)
        raw_score = max(0.0, min(100.0, raw_score))
        weight = task.rubric_weights.get(MetricDimension.CODE_QUALITY, 0.20)

        return DimensionScoreBreakdown(
            dimension=MetricDimension.CODE_QUALITY,
            raw_score=round(raw_score, 2),
            weight=weight,
            weighted_score=round(raw_score * weight, 2),
            sub_metrics={
                "cyclomatic_score": cyclo_score,
                "linter_score": linter_score,
                "modularity_score": modularity_score,
                "cyclomatic_raw": cyclo,
                "lint_violations_count": violations,
            },
            diagnostics=diagnostics,
        )

    # ==========================================================================
    # 4. PILLAR 4: PROBLEM-SOLVING APPROACH EVALUATION
    # ==========================================================================

    def evaluate_problem_solving_approach(
        self,
        snapshots: List[CodeSnapshot],
        task: MachineTestTask,
    ) -> DimensionScoreBreakdown:
        """
        Analyzes the candidate's development cadence, debugging loops, and copy-paste velocity.
        """
        diagnostics = []
        if not snapshots:
            return DimensionScoreBreakdown(
                dimension=MetricDimension.PROBLEM_SOLVING_APPROACH,
                raw_score=50.0,
                weight=task.rubric_weights.get(MetricDimension.PROBLEM_SOLVING_APPROACH, 0.20),
                weighted_score=10.0,
                sub_metrics={"incremental_ratio": 0.5, "debugging_agility": 0.5},
                diagnostics=["Insufficient snapshot telemetry captured."],
            )

        # 1. Incremental vs Instant Large Paste Velocity
        total_snapshots = len(snapshots)
        paste_events = [s for s in snapshots if s.event_type == SnapshotEventType.PASTE_BLOCK]
        paste_ratio = len(paste_events) / max(1, total_snapshots)

        # Look for massive single-turn character leap
        max_char_jump = max((s.diff_chars_from_previous for s in snapshots), default=0)
        if max_char_jump > 600 and paste_ratio > 0.40:
            typing_score = 45.0
            diagnostics.append(f"Suspicious sudden code paste detected ({max_char_jump} chars in one snapshot).")
        elif max_char_jump > 300:
            typing_score = 70.0
            diagnostics.append("Moderate paste activity observed; mostly structured entry.")
        else:
            typing_score = 95.0
            diagnostics.append("Healthy organic keystroke cadence with genuine incremental construction.")

        # 2. Test Execution Frequency & Debugging Turnaround
        test_runs = [s for s in snapshots if s.tests_triggered]
        if len(test_runs) >= 3:
            debugging_score = 95.0
            diagnostics.append(f"Proactive iterative validation: Triggered {len(test_runs)} intermediate test runs.")
        elif len(test_runs) in (1, 2):
            debugging_score = 75.0
            diagnostics.append(f"Moderate testing frequency ({len(test_runs)} runs).")
        else:
            debugging_score = 55.0
            diagnostics.append("Big-bang submission: Only tested solution upon final submission.")

        # 3. Error Recovery Velocity (Did tests fail, then pass?)
        passed_progression = [s.tests_passed_count for s in test_runs if s.total_tests_count > 0]
        if len(passed_progression) >= 2 and passed_progression[-1] > passed_progression[0]:
            recovery_bonus = 10.0
            diagnostics.append("Demonstrated positive error correction: Fixed failing tests across turns.")
        else:
            recovery_bonus = 0.0

        raw_score = (typing_score * 0.50) + (debugging_score * 0.50) + recovery_bonus
        raw_score = max(0.0, min(100.0, raw_score))
        weight = task.rubric_weights.get(MetricDimension.PROBLEM_SOLVING_APPROACH, 0.20)

        return DimensionScoreBreakdown(
            dimension=MetricDimension.PROBLEM_SOLVING_APPROACH,
            raw_score=round(raw_score, 2),
            weight=weight,
            weighted_score=round(raw_score * weight, 2),
            sub_metrics={
                "typing_cadence_score": typing_score,
                "debugging_loop_score": debugging_score,
                "recovery_bonus": recovery_bonus,
                "total_snapshots_analyzed": total_snapshots,
                "test_runs_count": len(test_runs),
            },
            diagnostics=diagnostics,
        )

    # ==========================================================================
    # HELPER UTILITIES
    # ==========================================================================

    def _calculate_loop_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively computes the maximum loop nesting level in AST."""
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._calculate_loop_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_loop_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        return max_depth
