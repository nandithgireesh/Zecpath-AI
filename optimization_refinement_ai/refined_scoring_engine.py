"""
Day 54: Optimization & Refinement - Refined Scoring Engine
==========================================================
Implements mathematical refinements to candidate scoring:
1. Role-Adaptive Dynamic Thresholding with Margin Damping
2. Cross-Round Coherence Index Calculation
3. Bayesian Variance Smoothing & Outlier Damping
4. Integrated Intent Adjustment and Sub-10ms P99 Performance
"""

import time
import math
from typing import List, Dict, Optional, Tuple
from optimization_refinement_ai.models import (
    DecisionClass,
    ThresholdOptimizationConfig,
    RefinedScoringOutput,
    IntentRefinementTelemetry
)
from optimization_refinement_ai.intent_refiner import IntentRefiner


class RefinedScoringEngine:
    """
    Enterprise Refined Scoring Engine delivering calibrated, consistent,
    and high-precision candidate evaluations.
    """

    DEFAULT_CONFIGS: Dict[str, ThresholdOptimizationConfig] = {
        "DISTRIBUTED_ARCHITECT": ThresholdOptimizationConfig(
            role_track="DISTRIBUTED_SYSTEMS",
            experience_tier="SENIOR_STAFF",
            base_selected_threshold=84.0,
            base_hold_floor=68.0,
            margin_damping_factor=0.85,
            variance_tolerance_ceiling=14.0
        ),
        "FULL_STACK_SENIOR": ThresholdOptimizationConfig(
            role_track="CORE_ENGINEERING",
            experience_tier="SENIOR",
            base_selected_threshold=82.0,
            base_hold_floor=65.0,
            margin_damping_factor=0.85,
            variance_tolerance_ceiling=16.0
        ),
        "GENERAL_SDE": ThresholdOptimizationConfig(
            role_track="GENERAL_ENGINEERING",
            experience_tier="MID_LEVEL",
            base_selected_threshold=80.0,
            base_hold_floor=62.0,
            margin_damping_factor=0.90,
            variance_tolerance_ceiling=18.0
        )
    }

    def __init__(
        self,
        custom_configs: Optional[Dict[str, ThresholdOptimizationConfig]] = None,
        intent_refiner: Optional[IntentRefiner] = None
    ):
        self.configs = custom_configs or self.DEFAULT_CONFIGS
        self.intent_refiner = intent_refiner or IntentRefiner()

    def get_role_config(self, role_key: str) -> ThresholdOptimizationConfig:
        """Resolves configuration by matching key or defaults to FULL_STACK_SENIOR."""
        clean_key = role_key.upper().replace(" ", "_")
        for k, cfg in self.configs.items():
            if k in clean_key or clean_key in k:
                return cfg
        return self.configs["FULL_STACK_SENIOR"]

    def calculate_coherence_index(self, round_scores: List[float]) -> float:
        """
        Computes Cross-Stage Coherence Index:
        C_coherence = 100.0 - (std_dev * 2.5), bounded in [0.0, 100.0].
        High coherence implies consistent competence across interview stages.
        """
        if not round_scores or len(round_scores) < 2:
            return 95.0

        n = len(round_scores)
        mean_score = sum(round_scores) / n
        variance = sum((x - mean_score) ** 2 for x in round_scores) / (n - 1)
        std_dev = math.sqrt(variance)

        coherence = 100.0 - (std_dev * 2.5)
        return max(0.0, min(100.0, round(coherence, 2)))

    def apply_bayesian_variance_smoothing(
        self,
        round_scores: List[float],
        prior_mean: float = 75.0,
        prior_variance: float = 64.0
    ) -> Tuple[float, float]:
        """
        Smooths candidate score across rounds using empirical Bayesian variance shrinkage.
        Prevents a single outlier round (e.g. biased interviewer or bad question)
        from drastically misclassifying a high-performing candidate.
        
        Returns:
            Tuple[raw_mean, smoothed_score]
        """
        if not round_scores:
            return prior_mean, prior_mean

        n = len(round_scores)
        unmitigated_raw_mean = sum(round_scores) / n

        if n == 1:
            return unmitigated_raw_mean, unmitigated_raw_mean

        sample_var = sum((x - unmitigated_raw_mean) ** 2 for x in round_scores) / (n - 1)
        sample_var = max(sample_var, 1.0)
        calculation_mean = unmitigated_raw_mean

        # Outlier damping: if max deviation > 20 points, trim the extreme
        sorted_scores = sorted(round_scores)
        if sorted_scores[-1] - sorted_scores[0] > 20.0 and n >= 3:
            # Dampen extreme lowest or highest score toward median
            median_score = sorted_scores[n // 2]
            damped_scores = [
                x if abs(x - median_score) <= 15.0 else (median_score + (15.0 if x > median_score else -15.0))
                for x in round_scores
            ]
            calculation_mean = sum(damped_scores) / n
            sample_var = sum((x - calculation_mean) ** 2 for x in damped_scores) / (n - 1)

        # Bayesian shrinkage factor
        # Weight on prior: w = (sample_var / n) / (prior_var + sample_var / n)
        se2 = sample_var / n
        w_prior = se2 / (prior_variance + se2)
        smoothed = (1.0 - w_prior) * calculation_mean + w_prior * prior_mean

        return round(unmitigated_raw_mean, 2), round(smoothed, 2)

    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_name: str,
        target_role: str,
        round_scores: List[float],
        pause_duration_seconds: float = 1.0,
        transcript_segment: str = "",
        existing_penalty: float = 0.0
    ) -> RefinedScoringOutput:
        """
        Executes unified refined evaluation for a candidate:
        1. Bayesian variance smoothing on round scores.
        2. Cross-round coherence calculation.
        3. Intent telemetry & pause disambiguation.
        4. Role-adaptive dynamic thresholding with margin damping.
        5. Sub-10ms latency measurement and SHA-256 seal.
        """
        start_ns = time.perf_counter_ns()

        cfg = self.get_role_config(target_role)

        # 1. Cross-round smoothing
        raw_mean, smoothed_score = self.apply_bayesian_variance_smoothing(round_scores)
        coherence = self.calculate_coherence_index(round_scores)

        # 2. Intent refinement
        intent_tel = self.intent_refiner.refine_candidate_intent(
            pause_duration_seconds=pause_duration_seconds,
            response_transcript=transcript_segment
        )

        # Apply intent adjustments: refund unjustified pause penalties or add points
        effective_score = smoothed_score + intent_tel.penalty_adjustment_points
        # If high implicit STAR and low evasion, reward bonus
        if intent_tel.implicit_star_coverage >= 75.0 and intent_tel.evasive_deflection_probability <= 0.15:
            effective_score += 1.0
        elif intent_tel.evasive_deflection_probability >= 0.5:
            effective_score -= 3.0

        effective_score = max(0.0, min(100.0, round(effective_score, 2)))

        # 3. Dynamic Threshold Resolution & Margin Damping
        selected_thresh = cfg.base_selected_threshold
        hold_floor = cfg.base_hold_floor

        # Adjust threshold based on cross-round coherence
        # High coherence (>90) rewards consistency by lowering threshold by up to 0.75 points
        if coherence >= 90.0:
            selected_thresh -= 0.5
        elif coherence < 70.0:
            selected_thresh += 1.0

        # Margin damping around boundary zones (within 1.5 points of threshold)
        margin = 1.5
        if abs(effective_score - selected_thresh) <= margin:
            # In boundary buffer: check coherence and intent
            if coherence >= 85.0 and intent_tel.intent_confidence_score >= 88.0:
                decision = DecisionClass.SELECTED
                substatus = "SELECTED_VIA_COHERENCE_DAMPING"
                confidence = 88.5
            else:
                decision = DecisionClass.HOLD_REVIEW
                substatus = "HOLD_MARGINAL_BORDERLINE"
                confidence = 80.0
        elif effective_score >= selected_thresh:
            decision = DecisionClass.SELECTED
            substatus = "SELECTED_DEFINITIVE"
            confidence = min(99.0, 90.0 + (effective_score - selected_thresh) * 1.5)
        elif effective_score >= hold_floor:
            decision = DecisionClass.HOLD_REVIEW
            substatus = "HOLD_SECONDARY_DELIBERATION"
            confidence = 85.0
        else:
            decision = DecisionClass.REJECTED
            substatus = "REJECTED_BELOW_FLOOR"
            confidence = min(99.0, 92.0 + (hold_floor - effective_score) * 1.2)

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

        output = RefinedScoringOutput(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            target_role=target_role,
            raw_composite_score=raw_mean,
            variance_smoothed_score=effective_score,
            cross_round_coherence_index=coherence,
            dynamic_selected_threshold=round(selected_thresh, 2),
            dynamic_hold_floor=round(hold_floor, 2),
            final_decision=decision,
            decision_substatus=substatus,
            confidence_score=round(confidence, 1),
            intent_telemetry=intent_tel,
            processing_latency_ms=round(elapsed_ms, 3)
        )
        output.finalize_and_seal()
        return output
