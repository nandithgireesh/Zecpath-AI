"""
Day 30 - System Testing & Evaluation Harness
============================================
Comprehensive test harness that evaluates the entire AI screening system against
human recruiter ground-truth benchmark calls. Measures accuracy, F1, Cohen's Kappa,
and validates false rejection reduction.
"""

import os
import json
from typing import List, Dict, Any, Optional

from screening_ai.optimization_models import (
    OptimizationComparisonReport,
    EvaluationMetrics,
    SimulatedCallResult,
)
from screening_ai.threshold_optimizer import ScreeningThresholdOptimizer
from screening_ai.simulation_engine import ScreeningSimulationEngine


class ScreeningSystemEvaluator:
    """
    Day 30 - System-wide evaluation harness.
    Compares baseline uncalibrated behavior with Day 30 optimized performance.
    """

    def __init__(
        self,
        benchmark_file: Optional[str] = None,
        threshold_optimizer: Optional[ScreeningThresholdOptimizer] = None,
    ):
        self.optimizer = threshold_optimizer or ScreeningThresholdOptimizer()
        self.simulation_engine = ScreeningSimulationEngine(
            benchmark_file=benchmark_file,
            threshold_optimizer=self.optimizer,
        )

    def run_full_benchmark_evaluation(self) -> OptimizationComparisonReport:
        """
        Runs comprehensive benchmark evaluation across all 12 candidate profiles.
        Computes side-by-side metrics comparing baseline and optimized systems.
        """
        profiles = self.simulation_engine.get_profiles()
        if not profiles:
            raise ValueError("No benchmark profiles available for evaluation")

        comparison_report = self.optimizer.compare_benchmarks(
            benchmark_profiles=profiles,
            baseline_cfg=self.optimizer.get_baseline_config(),
            optimized_cfg=self.optimizer.get_optimized_config(),
        )

        return comparison_report

    def evaluate_intent_accuracy(self) -> Dict[str, Any]:
        """
        Evaluates intent classification accuracy on benchmark turns across baseline vs. improved intent.
        """
        profiles = self.simulation_engine.get_profiles()
        from screening_ai.intent_classifier import CandidateIntentClassifier
        from screening_ai.improved_intent import OptimizedIntentClassifier

        base_clf = CandidateIntentClassifier()
        opt_clf = OptimizedIntentClassifier()

        total_turns = 0
        base_correct = 0
        opt_correct = 0

        for p in profiles:
            for turn in p.get("turns", []):
                total_turns += 1
                text = turn["candidate_response"]
                cat = turn.get("question_category")
                prompt = turn.get("question_text")
                expected = turn.get("human_intent")

                # Baseline intent classification
                base_intent, _, _ = base_clf.classify_intent(text, question_category=cat, question_prompt=prompt)
                if base_intent.value == expected:
                    base_correct += 1

                # Optimized intent classification
                opt_intent, _, _ = opt_clf.classify_intent(text, question_category=cat, question_prompt=prompt)
                if opt_intent.value == expected:
                    opt_correct += 1

        base_acc = round(base_correct / max(1, total_turns), 4)
        opt_acc = round(opt_correct / max(1, total_turns), 4)

        return {
            "total_turns_evaluated": total_turns,
            "baseline_correct": base_correct,
            "baseline_accuracy": base_acc,
            "optimized_correct": opt_correct,
            "optimized_accuracy": opt_acc,
            "accuracy_lift_pct": round((opt_acc - base_acc) * 100.0, 1),
        }
