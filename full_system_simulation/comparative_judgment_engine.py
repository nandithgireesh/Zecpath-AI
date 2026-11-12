"""
Day 56: Comparative Judgment Engine - AI vs. Human Assessment Evaluation
========================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Performs statistical, psychometric, and confusion-matrix comparison between
AI automated evaluation and expert human hiring committees.
"""

import math
from typing import Dict, List, Tuple, Any, Optional

from full_system_simulation.models import (
    DecisionVerdict, ComparativeEvaluation, CompleteJourneyDossier
)


class ComparativeJudgmentEngine:
    """
    Evaluates alignment, agreement metrics, and error rates between
    AI predictions and human hiring panel decisions.
    """

    HIRE_VERDICTS = {DecisionVerdict.STRONG_HIRE, DecisionVerdict.HIRE, DecisionVerdict.LEAN_HIRE}
    REJECT_VERDICTS = {DecisionVerdict.HOLD_REVIEW, DecisionVerdict.LEAN_REJECT, DecisionVerdict.REJECT}

    def evaluate_candidate(
        self,
        dossier: CompleteJourneyDossier,
        human_score: float,
        human_verdict: DecisionVerdict,
        human_bias_marker: Optional[str] = None
    ) -> ComparativeEvaluation:
        """
        Compares an individual candidate's AI evaluation against human assessment.
        """
        ai_score = dossier.final_decision.variance_smoothed_score
        ai_verdict = dossier.final_decision.ai_verdict
        score_delta = round(ai_score - human_score, 2)
        concordance = (ai_verdict == human_verdict)

        ai_is_hire = ai_verdict in self.HIRE_VERDICTS
        human_is_hire = human_verdict in self.HIRE_VERDICTS

        if ai_is_hire and human_is_hire:
            quadrant = "TRUE_POSITIVE"
        elif not ai_is_hire and not human_is_hire:
            quadrant = "TRUE_NEGATIVE"
        elif ai_is_hire and not human_is_hire:
            quadrant = "FALSE_POSITIVE" # AI lenient or Human strict
        else:
            quadrant = "FALSE_NEGATIVE" # AI strict or Human lenient

        ai_bias_marker = None
        if quadrant == "FALSE_NEGATIVE" and dossier.hr_result.speech_pause_telemetry < 50.0:
            ai_bias_marker = "SPEECH_TELEMETRY_RIGIDITY"
        elif quadrant == "FALSE_POSITIVE" and dossier.ats_result.composite_ats_score > 90.0:
            ai_bias_marker = "RESUME_KEYWORD_OVERWEIGHTING"

        record = ComparativeEvaluation(
            candidate_id=dossier.candidate_id,
            candidate_name=dossier.candidate_name,
            ai_score=ai_score,
            human_score=human_score,
            score_delta=score_delta,
            ai_verdict=ai_verdict,
            human_verdict=human_verdict,
            verdict_concordance=concordance,
            classification_quadrant=quadrant,
            human_bias_marker=human_bias_marker,
            ai_bias_marker=ai_bias_marker
        )
        dossier.comparative_record = record
        return record

    def compute_cohort_metrics(
        self,
        comparisons: List[ComparativeEvaluation]
    ) -> Dict[str, Any]:
        """
        Computes aggregate inter-rater reliability, confusion matrix,
        and statistical correlation metrics across a candidate cohort.
        """
        if not comparisons:
            return {}

        n = len(comparisons)
        tp = sum(1 for c in comparisons if c.classification_quadrant == "TRUE_POSITIVE")
        tn = sum(1 for c in comparisons if c.classification_quadrant == "TRUE_NEGATIVE")
        fp = sum(1 for c in comparisons if c.classification_quadrant == "FALSE_POSITIVE")
        fn = sum(1 for c in comparisons if c.classification_quadrant == "FALSE_NEGATIVE")

        accuracy = (tp + tn) / n if n > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Exact verdict match rate
        exact_matches = sum(1 for c in comparisons if c.verdict_concordance)
        exact_concordance_rate = exact_matches / n

        # Numerical correlation (Pearson r)
        ai_scores = [c.ai_score for c in comparisons]
        human_scores = [c.human_score for c in comparisons]
        mean_ai = sum(ai_scores) / n
        mean_human = sum(human_scores) / n

        num = sum((a - mean_ai) * (h - mean_human) for a, h in zip(ai_scores, human_scores))
        den_ai = math.sqrt(sum((a - mean_ai) ** 2 for a in ai_scores))
        den_human = math.sqrt(sum((h - mean_human) ** 2 for h in human_scores))
        pearson_r = num / (den_ai * den_human) if (den_ai * den_human) > 0 else 0.0

        # Mean Absolute Error (MAE) and RMSE
        mae = sum(abs(c.score_delta) for c in comparisons) / n
        rmse = math.sqrt(sum(c.score_delta ** 2 for c in comparisons) / n)

        # Cohen's Kappa for binary hire/no-hire decision
        # Po = observed agreement (accuracy)
        # Pe = chance agreement
        p_ai_hire = (tp + fp) / n
        p_human_hire = (tp + fn) / n
        p_ai_reject = (tn + fn) / n
        p_human_reject = (tn + fp) / n
        p_e = (p_ai_hire * p_human_hire) + (p_ai_reject * p_human_reject)
        
        cohen_kappa = (accuracy - p_e) / (1.0 - p_e) if (1.0 - p_e) > 0 else 1.0

        return {
            "total_candidates": n,
            "confusion_matrix": {
                "true_positives": tp,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn
            },
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "specificity": round(specificity, 4),
                "f1_score": round(f1_score, 4),
                "exact_concordance_rate": round(exact_concordance_rate, 4),
                "cohen_kappa": round(cohen_kappa, 4),
                "pearson_r": round(pearson_r, 4),
                "mae": round(mae, 2),
                "rmse": round(rmse, 2)
            }
        }
