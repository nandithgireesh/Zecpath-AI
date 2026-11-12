"""
Day 57: Scoring Stabilizer - Fix Scoring Inconsistencies & Numerical Safeguards
==============================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Remediates:
  1. Score clipping & zero-division errors.
  2. Outlier skew via Winsorization.
  3. Dialect-neutral speech telemetry smoothing (fixes Day 56 accent bias).
  4. Decoupled fluency-to-technical hard gating (fixes Day 56 fluency disguise).
"""

import math
from typing import Dict, List, Optional, Tuple, Any

from debugging_stabilization_ai.models import PipelineErrorCode, SeverityLevel, DebugIncidentLog


class ScoringStabilizer:
    """
    Ensures mathematical determinism, bounded scores, dialect-neutral smoothing,
    and anti-inflation guards across all scoring subsystems.
    """

    MIN_TECH_FLOOR_FOR_HIRE = 50.0

    @staticmethod
    def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
        """Protects against ZeroDivisionError and NaN generation."""
        if denominator == 0.0 or math.isnan(denominator) or math.isnan(numerator):
            return fallback
        return numerator / denominator

    @staticmethod
    def clamp_score(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Guarantees scores strictly conform to [min_val, max_val]."""
        if math.isnan(val) or math.isinf(val):
            return min_val
        return max(min_val, min(val, max_val))

    def smooth_speech_telemetry(
        self,
        raw_pause_score: float,
        is_non_native_speaker: bool = False,
        confidence_clarity_score: float = 75.0
    ) -> float:
        """
        Remediates the Day 56 Speech Telemetry Accent Anomaly.
        If a candidate is deliberate or non-native, pauses must not be penalized
        as hesitation if verbal clarity is high.
        """
        clamped_pause = self.clamp_score(raw_pause_score)
        if is_non_native_speaker or confidence_clarity_score >= 70.0:
            # Dialect-neutral acoustic adjustment factor
            boost = min((confidence_clarity_score - 50.0) * 0.40, 25.0)
            adjusted = clamped_pause + boost
            return round(self.clamp_score(adjusted), 1)
        return round(clamped_pause, 1)

    def calculate_stabilized_composite(
        self,
        ats_score: float,
        screening_score: float,
        hr_score: float,
        technical_score: float,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, float, List[str]]:
        """
        Computes a stable, variance-damped composite score with anti-fluency disguise guards.
        
        Returns:
            Tuple of (raw_score, variance_smoothed_score, applied_safeguards)
        """
        safeguards_applied = []

        # 1. Clamp all inputs
        c_ats = self.clamp_score(ats_score)
        c_scr = self.clamp_score(screening_score)
        c_hr = self.clamp_score(hr_score)
        c_tech = self.clamp_score(technical_score)

        if not weights:
            weights = {"ats": 0.15, "screening": 0.10, "hr": 0.30, "tech": 0.45}

        # Safe weight normalization
        total_w = sum(weights.values())
        norm_w = {k: self.safe_divide(v, total_w, 0.25) for k, v in weights.items()}

        raw_score = (
            norm_w["ats"] * c_ats +
            norm_w["screening"] * c_scr +
            norm_w["hr"] * c_hr +
            norm_w["tech"] * c_tech
        )

        # 2. Fluency Disguise Hard Gate (Day 56 Bugfix)
        # If technical capability is below floor, HR verbal charm cannot carry candidate to a HIRE
        if c_tech < self.MIN_TECH_FLOOR_FOR_HIRE and c_hr >= 75.0:
            penalty = (c_hr - c_tech) * 0.35
            raw_score = max(raw_score - penalty, c_tech)
            safeguards_applied.append(
                f"FLUENCY_DISGUISE_GUARD: Applied {penalty:.1f} pt damping penalty due to technical deficit ({c_tech:.1f}%)."
            )

        # 3. Cross-Round Variance Damping
        round_scores = [c_ats, c_scr, c_hr, c_tech]
        mean_s = sum(round_scores) / 4.0
        variance = sum((s - mean_s) ** 2 for s in round_scores) / 4.0
        std_dev = math.sqrt(variance)

        # Winsorized stability penalty
        stability_penalty = min(std_dev * 0.15, 6.0)
        smoothed_score = round(self.clamp_score(raw_score - stability_penalty), 2)

        if stability_penalty >= 2.0:
            safeguards_applied.append(
                f"VARIANCE_DAMPING: Damped {stability_penalty:.2f} pts due to cross-round standard deviation ({std_dev:.1f})."
            )

        return round(raw_score, 2), smoothed_score, safeguards_applied
