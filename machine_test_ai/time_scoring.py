"""
Zecpath-AI: Day 50 - Time-Based Scoring Engine & Real-World Scoring Model
========================================================================
Implements mathematical time decay curves, velocity bonuses, and multi-factor
composite score aggregation for real-world machine tests:
1. Pacing & Time Efficiency Telemetry
2. Exponential Overtime Decay and Velocity Bonus Curves
3. Real-World Task Composite Score Synthesis with Role Calibration
4. Cryptographic SHA-256 Audit Seal Generation

Curriculum Reference: Day 50 - Deliverable 3: Scoring Model for Real-World Tasks
"""

import math
import hashlib
from typing import Dict, List, Optional, Any
from .models import (
    MetricDimension,
    DimensionScoreBreakdown,
    TimeEfficiencyTelemetry,
    TaskEvaluationResult,
    MachineTestTask,
)


class TimeBasedScoringEngine:
    """
    Mathematical engine calculating time-efficiency multipliers and synthesizing
    the final calibrated machine test score.
    """

    # Decay rate lambda for overtime: e^(-lambda * (ratio - 1))
    DEFAULT_DECAY_LAMBDA: float = 0.35
    MAX_VELOCITY_BONUS_PTS: float = 8.0
    MAX_OVERTIME_PENALTY_PTS: float = 25.0

    def __init__(self, decay_lambda: float = DEFAULT_DECAY_LAMBDA):
        self.decay_lambda = decay_lambda

    def calculate_time_telemetry(
        self,
        actual_duration_minutes: float,
        task: MachineTestTask,
    ) -> TimeEfficiencyTelemetry:
        """
        Calculates pacing ratio, velocity bonus or overtime penalty.
        """
        baseline = task.expected_baseline_minutes
        timeout = task.max_timeout_minutes
        time_ratio = round(actual_duration_minutes / max(0.1, baseline), 3)
        is_timeout = actual_duration_minutes > timeout

        bonus_points = 0.0
        penalty_points = 0.0

        if actual_duration_minutes <= baseline:
            # Completed ahead of or exactly on schedule: awarded velocity bonus
            # Linear scaling from 0 at baseline to MAX at 40% of baseline
            savings_fraction = max(0.0, (baseline - actual_duration_minutes) / baseline)
            bonus_points = round(min(self.MAX_VELOCITY_BONUS_PTS, savings_fraction * 12.0), 2)
            speed_factor = round(1.0 + (bonus_points / 100.0), 3)
            pacing_verdict = "HIGH_VELOCITY_SOLVE" if savings_fraction >= 0.30 else "OPTIMAL_PACE"
        else:
            # Overtime: Smooth exponential decay multiplier
            overtime_ratio = time_ratio - 1.0
            decay = math.exp(-self.decay_lambda * overtime_ratio)
            speed_factor = round(max(0.60, min(1.0, decay)), 3)
            # Calculated penalty points
            penalty_points = round(min(self.MAX_OVERTIME_PENALTY_PTS, (1.0 - speed_factor) * 50.0), 2)
            if is_timeout:
                penalty_points = self.MAX_OVERTIME_PENALTY_PTS
                pacing_verdict = "HARD_TIMEOUT_BREACHED"
            else:
                pacing_verdict = "EXTENDED_OVERTIME"

        return TimeEfficiencyTelemetry(
            actual_duration_minutes=round(actual_duration_minutes, 2),
            baseline_duration_minutes=round(baseline, 2),
            time_ratio=time_ratio,
            speed_factor=speed_factor,
            bonus_points=bonus_points,
            penalty_points=penalty_points,
            is_timeout_breached=is_timeout,
            pacing_verdict=pacing_verdict,
        )

    def synthesize_final_report(
        self,
        task: MachineTestTask,
        candidate_id: str,
        submission_timestamp: float,
        actual_duration_minutes: float,
        dimension_breakdowns: Dict[MetricDimension, DimensionScoreBreakdown],
    ) -> TaskEvaluationResult:
        """
        Synthesizes the 4 pillar breakdowns into a calibrated real-world evaluation report.
        """
        # 1. Base Composite Score = sum of weighted scores
        base_composite = sum(b.weighted_score for b in dimension_breakdowns.values())
        base_composite = round(max(0.0, min(100.0, base_composite)), 2)

        # 2. Time efficiency calculation
        time_telemetry = self.calculate_time_telemetry(actual_duration_minutes, task)

        # 3. Final Time-Adjusted Score
        # Formula: Final = clamp((Base * SpeedFactor) + Bonus - Penalty, 0, 100)
        adjusted_score = (base_composite * time_telemetry.speed_factor)
        if time_telemetry.bonus_points > 0:
            adjusted_score += time_telemetry.bonus_points
        if time_telemetry.penalty_points > 0:
            adjusted_score -= (time_telemetry.penalty_points * 0.5)  # Damped penalty
        final_score = round(max(0.0, min(100.0, adjusted_score)), 1)

        # 4. Grade Verdict
        if final_score >= 85.0:
            verdict = "EXEMPLARY"
        elif final_score >= 70.0:
            verdict = "PROFICIENT"
        elif final_score >= 50.0:
            verdict = "NEEDS_IMPROVEMENT"
        else:
            verdict = "UNSATISFACTORY"

        # 5. Cryptographic SHA-256 Audit Seal
        payload_str = (
            f"{task.task_id}|{candidate_id}|{final_score}|"
            f"{time_telemetry.actual_duration_minutes}|{submission_timestamp}"
        )
        audit_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        # 6. Executive Summary Remarks
        corr_score = dimension_breakdowns[MetricDimension.CORRECTNESS].raw_score
        eff_score = dimension_breakdowns[MetricDimension.EFFICIENCY].raw_score
        remarks = (
            f"Candidate achieved {verdict} status with composite score of {final_score}/100. "
            f"Functional Correctness: {corr_score:.1f}%, Efficiency: {eff_score:.1f}%. "
            f"Pacing: {time_telemetry.pacing_verdict} ({time_telemetry.actual_duration_minutes}m vs "
            f"{time_telemetry.baseline_duration_minutes}m baseline)."
        )

        return TaskEvaluationResult(
            task_id=task.task_id,
            task_type=task.task_type,
            task_title=task.title,
            candidate_id=candidate_id,
            submission_timestamp=submission_timestamp,
            time_telemetry=time_telemetry,
            dimension_breakdowns=dimension_breakdowns,
            base_composite_score=base_composite,
            final_time_adjusted_score=final_score,
            grade_verdict=verdict,
            audit_hash_sha256=audit_hash,
            summary_remarks=remarks,
        )
