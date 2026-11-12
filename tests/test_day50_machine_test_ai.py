"""
Unit Test Suite: Day 50 - Machine Test AI Design
=================================================
Validates:
1. Machine Test Types: Coding Problems, Debugging Tasks, File Tasks, Mini System Design
2. Evaluation Metrics: Correctness, Efficiency, Code Quality, Problem-Solving Approach
3. Input/Output Capture: Code Snapshots, Execution Telemetry, Sandbox Traces
4. Time-Based Scoring: Pacing, Overtime Decay, Velocity Bonus, Hard Timeout
5. End-to-End Orchestrator: P99 SLA <= 150ms, SHA-256 integrity seal
"""

import unittest
import time
from machine_test_ai.models import (
    MachineTestType,
    MetricDimension,
    DifficultyTier,
    SnapshotEventType,
    CodeSnapshot,
    TestCaseResult,
    ExecutionResult,
    MachineTestTask,
)
from machine_test_ai.evaluation_engine import TaskEvaluationEngine
from machine_test_ai.time_scoring import TimeBasedScoringEngine
from machine_test_ai.framework import MachineTestAIFramework, CURATED_MACHINE_TASKS


class TestDay50MachineTestAI(unittest.TestCase):

    def setUp(self):
        self.framework = MachineTestAIFramework()
        self.eval_engine = TaskEvaluationEngine()
        self.time_engine = TimeBasedScoringEngine()
        self.task_code = CURATED_MACHINE_TASKS["TASK-CODE-01"]
        self.task_debug = CURATED_MACHINE_TASKS["TASK-DEBUG-02"]
        self.task_file = CURATED_MACHINE_TASKS["TASK-FILE-03"]
        self.task_sd = CURATED_MACHINE_TASKS["TASK-SD-04"]

    # --------------------------------------------------------------------------
    # 1. TASK REGISTRY & MACHINE TEST TYPES
    # --------------------------------------------------------------------------

    def test_curated_task_types_presence(self):
        """Verifies all four mandatory machine test types are configured in catalog."""
        coding_tasks = self.framework.list_tasks_by_type(MachineTestType.CODING_PROBLEM)
        debug_tasks = self.framework.list_tasks_by_type(MachineTestType.DEBUGGING_TASK)
        file_tasks = self.framework.list_tasks_by_type(MachineTestType.FILE_BASED_TASK)
        sd_tasks = self.framework.list_tasks_by_type(MachineTestType.MINI_SYSTEM_DESIGN)

        self.assertGreaterEqual(len(coding_tasks), 1)
        self.assertGreaterEqual(len(debug_tasks), 1)
        self.assertGreaterEqual(len(file_tasks), 1)
        self.assertGreaterEqual(len(sd_tasks), 1)

    def test_custom_task_registration(self):
        """Verifies custom real-world task registration and retrieval."""
        custom_task = MachineTestTask(
            task_id="TASK-CUSTOM-99",
            task_type=MachineTestType.CODING_PROBLEM,
            title="Custom Graph BFS Challenge",
            description="Find shortest path in directed acyclic graph.",
            difficulty=DifficultyTier.MEDIUM,
            starter_code="def bfs(): pass",
            expected_baseline_minutes=18.0,
            max_timeout_minutes=30.0,
        )
        self.framework.register_custom_task(custom_task)
        fetched = self.framework.get_task("TASK-CUSTOM-99")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Custom Graph BFS Challenge")

    # --------------------------------------------------------------------------
    # 2. PILLAR 1: CORRECTNESS EVALUATION
    # --------------------------------------------------------------------------

    def test_correctness_perfect_pass(self):
        """Verifies 100% score for complete test pass."""
        tests = [
            TestCaseResult(test_id="T1", test_name="Base case", is_hidden=False, passed=True, execution_time_ms=1.2, memory_peak_kb=10.0),
            TestCaseResult(test_id="T2", test_name="Large N", is_hidden=True, passed=True, execution_time_ms=5.4, memory_peak_kb=20.0),
        ]
        exec_res = ExecutionResult(
            execution_id="EXEC-01",
            exit_code=0,
            total_test_cases=2,
            passed_test_cases=2,
            failed_test_cases=0,
            wall_clock_time_ms=15.0,
            peak_memory_mb=12.0,
            cyclomatic_complexity=3,
            pep8_violations_count=0,
            test_details=tests,
        )
        res = self.eval_engine.evaluate_correctness(exec_res, self.task_code)
        self.assertEqual(res.raw_score, 100.0)
        self.assertEqual(res.weighted_score, 40.0)  # 100 * 0.40

    def test_correctness_partial_and_timeout_penalty(self):
        """Verifies penalties applied for test failure and process timeouts."""
        exec_res = ExecutionResult(
            execution_id="EXEC-02",
            exit_code=1,
            total_test_cases=10,
            passed_test_cases=6,
            failed_test_cases=4,
            wall_clock_time_ms=2500.0,
            peak_memory_mb=40.0,
            cyclomatic_complexity=6,
            pep8_violations_count=2,
            timed_out=True,
        )
        res = self.eval_engine.evaluate_correctness(exec_res, self.task_code)
        # 60% base - 35 timeout penalty = 25.0
        self.assertEqual(res.raw_score, 25.0)

    # --------------------------------------------------------------------------
    # 3. PILLAR 2: EFFICIENCY EVALUATION
    # --------------------------------------------------------------------------

    def test_efficiency_fast_and_linear(self):
        """Verifies high score for low latency, low memory, and linear complexity."""
        code = "def solve(arr):\n    res = []\n    for x in arr:\n        res.append(x * 2)\n    return res\n"
        exec_res = ExecutionResult(
            execution_id="EXEC-03",
            exit_code=0,
            total_test_cases=5,
            passed_test_cases=5,
            failed_test_cases=0,
            wall_clock_time_ms=50.0,  # 50ms / 500ms budget = 10% (sub-25%)
            peak_memory_mb=10.0,      # 10MB / 64MB budget = 15% (sub-30%)
            cyclomatic_complexity=2,
            pep8_violations_count=0,
        )
        res = self.eval_engine.evaluate_efficiency(exec_res, code, self.task_code)
        self.assertGreaterEqual(res.raw_score, 90.0)

    def test_efficiency_nested_cubic_loops_penalty(self):
        """Verifies nested loop complexity detection via AST."""
        cubic_code = (
            "def triple_loop(matrix):\n"
            "    for i in range(len(matrix)):\n"
            "        for j in range(len(matrix)):\n"
            "            for k in range(len(matrix)):\n"
            "                pass\n"
        )
        exec_res = ExecutionResult(
            execution_id="EXEC-04",
            exit_code=0,
            total_test_cases=1,
            passed_test_cases=1,
            failed_test_cases=0,
            wall_clock_time_ms=450.0,
            peak_memory_mb=50.0,
            cyclomatic_complexity=8,
            pep8_violations_count=1,
        )
        res = self.eval_engine.evaluate_efficiency(exec_res, cubic_code, self.task_code)
        self.assertLess(res.raw_score, 75.0)
        self.assertIn("cubic", " ".join(res.diagnostics).lower())

    # --------------------------------------------------------------------------
    # 4. PILLAR 3: CODE QUALITY EVALUATION
    # --------------------------------------------------------------------------

    def test_code_quality_modular_and_clean(self):
        """Verifies modular code with docstrings and type annotations gets high quality score."""
        clean_code = (
            '"""LRU Cache high performance implementation."""\n'
            'from typing import Optional\n\n'
            'class Node:\n'
            '    def __init__(self, key: int, val: int):\n'
            '        self.key: int = key\n'
            '        self.val: int = val\n\n'
            'def helper_func(n: int) -> bool:\n'
            '    """Validates node state."""\n'
            '    return n > 0\n'
        )
        exec_res = ExecutionResult(
            execution_id="EXEC-05",
            exit_code=0,
            total_test_cases=5,
            passed_test_cases=5,
            failed_test_cases=0,
            wall_clock_time_ms=30.0,
            peak_memory_mb=8.0,
            cyclomatic_complexity=2,
            pep8_violations_count=0,
        )
        res = self.eval_engine.evaluate_code_quality(clean_code, exec_res, self.task_code)
        self.assertGreaterEqual(res.raw_score, 90.0)

    def test_code_quality_high_cyclomatic_and_linter_violations(self):
        """Verifies penalties for high cyclomatic complexity and style violations."""
        spaghetti_code = "def f(x):\n    pass\n"
        exec_res = ExecutionResult(
            execution_id="EXEC-06",
            exit_code=0,
            total_test_cases=1,
            passed_test_cases=1,
            failed_test_cases=0,
            wall_clock_time_ms=30.0,
            peak_memory_mb=8.0,
            cyclomatic_complexity=18,    # High cognitive complexity
            pep8_violations_count=8,     # Many lint errors
        )
        res = self.eval_engine.evaluate_code_quality(spaghetti_code, exec_res, self.task_code)
        self.assertLessEqual(res.raw_score, 65.0)

    # --------------------------------------------------------------------------
    # 5. PILLAR 4: PROBLEM-SOLVING APPROACH & SNAPSHOTS
    # --------------------------------------------------------------------------

    def test_problem_solving_incremental_natural_cadence(self):
        """Verifies incremental typing with iterative test executions receives high marks."""
        snapshots = [
            CodeSnapshot(snapshot_id="S1", timestamp_offset_seconds=60, code_content="class C:", character_count=8, line_count=1, diff_chars_from_previous=8),
            CodeSnapshot(snapshot_id="S2", timestamp_offset_seconds=180, code_content="class C:\n  def get(k): return 1", character_count=32, line_count=2, diff_chars_from_previous=24, tests_triggered=True, tests_passed_count=1, total_tests_count=4),
            CodeSnapshot(snapshot_id="S3", timestamp_offset_seconds=360, code_content="class C:\n  def get(k): return 1\n  def put(k,v): pass", character_count=56, line_count=3, diff_chars_from_previous=24, tests_triggered=True, tests_passed_count=4, total_tests_count=4),
        ]
        res = self.eval_engine.evaluate_problem_solving_approach(snapshots, self.task_code)
        self.assertGreaterEqual(res.raw_score, 90.0)
        self.assertEqual(res.sub_metrics["recovery_bonus"], 10.0)

    def test_problem_solving_sudden_massive_paste_penalty(self):
        """Verifies sudden massive paste without incremental typing is flagged."""
        snapshots = [
            CodeSnapshot(snapshot_id="S1", timestamp_offset_seconds=10, code_content="", character_count=0, line_count=0),
            CodeSnapshot(snapshot_id="S2", timestamp_offset_seconds=25, code_content="X" * 1200, character_count=1200, line_count=60, diff_chars_from_previous=1200, event_type=SnapshotEventType.PASTE_BLOCK),
        ]
        res = self.eval_engine.evaluate_problem_solving_approach(snapshots, self.task_code)
        self.assertLessEqual(res.raw_score, 65.0)
        self.assertIn("paste", " ".join(res.diagnostics).lower())

    # --------------------------------------------------------------------------
    # 6. TIME-BASED SCORING & VELOCITY CURVES
    # --------------------------------------------------------------------------

    def test_time_scoring_fast_solve_awards_bonus(self):
        """Verifies early completion awards positive velocity bonus points."""
        # 12 minutes on a 20-minute baseline (40% time savings)
        telemetry = self.time_engine.calculate_time_telemetry(12.0, self.task_code)
        self.assertGreater(telemetry.bonus_points, 0.0)
        self.assertEqual(telemetry.penalty_points, 0.0)
        self.assertIn("HIGH_VELOCITY", telemetry.pacing_verdict)

    def test_time_scoring_overtime_decays_score(self):
        """Verifies overtime beyond baseline triggers exponential decay."""
        # 30 minutes on a 20-minute baseline (1.5x ratio)
        telemetry = self.time_engine.calculate_time_telemetry(30.0, self.task_code)
        self.assertEqual(telemetry.bonus_points, 0.0)
        self.assertGreater(telemetry.penalty_points, 0.0)
        self.assertLess(telemetry.speed_factor, 1.0)
        self.assertEqual(telemetry.pacing_verdict, "EXTENDED_OVERTIME")

    def test_time_scoring_hard_timeout_breach(self):
        """Verifies hard cutoff when exceeding max timeout."""
        # 38 minutes on a 35-minute max timeout
        telemetry = self.time_engine.calculate_time_telemetry(38.0, self.task_code)
        self.assertTrue(telemetry.is_timeout_breached)
        self.assertEqual(telemetry.pacing_verdict, "HARD_TIMEOUT_BREACHED")

    # --------------------------------------------------------------------------
    # 7. END-TO-END ORCHESTRATION & SLA VALIDATION
    # --------------------------------------------------------------------------

    def test_end_to_end_evaluation_pipeline(self):
        """Verifies full framework submission execution, grading, and cryptographic hash."""
        snapshots = [
            CodeSnapshot(snapshot_id="S1", timestamp_offset_seconds=120, code_content="class Solution:\n    pass", character_count=24, line_count=2, diff_chars_from_previous=24),
            CodeSnapshot(snapshot_id="S2", timestamp_offset_seconds=300, code_content="class Solution:\n    def run(self): return True", character_count=52, line_count=2, diff_chars_from_previous=28, tests_triggered=True, tests_passed_count=3, total_tests_count=3),
        ]
        exec_res = ExecutionResult(
            execution_id="EXEC-E2E-01",
            exit_code=0,
            total_test_cases=3,
            passed_test_cases=3,
            failed_test_cases=0,
            wall_clock_time_ms=85.0,
            peak_memory_mb=14.0,
            cyclomatic_complexity=2,
            pep8_violations_count=0,
        )

        t0 = time.perf_counter()
        report = self.framework.evaluate_submission(
            task_id="TASK-CODE-01",
            candidate_id="CAND-TEST-42",
            final_code="class Solution:\n    def run(self): return True",
            snapshots=snapshots,
            execution_result=exec_res,
            actual_duration_minutes=15.0,  # ahead of 20m baseline
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # SLA Guarantee: P99 <= 150ms
        self.assertLessEqual(elapsed_ms, 150.0)
        self.assertEqual(report.grade_verdict, "EXEMPLARY")
        self.assertGreaterEqual(report.final_time_adjusted_score, 85.0)
        self.assertEqual(len(report.audit_hash_sha256), 64)  # Valid SHA-256

    def test_framework_manifest_integrity(self):
        """Verifies architectural manifest generation with deterministic hash."""
        manifest = self.framework.generate_framework_manifest()
        self.assertEqual(manifest["framework_id"], "FRAMEWORK-DAY50-MACHINE-TEST-AI")
        self.assertEqual(len(manifest["sha256_integrity_hash"]), 64)
        self.assertEqual(manifest["registered_tasks_count"], 4)


if __name__ == "__main__":
    unittest.main()
