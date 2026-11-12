"""
Day 27: Confidence Analysis Logic
=================================
Analyzes spoken candidate responses for:
1. Hesitation patterns (verbal fillers, stutters, repetitions, extended pauses, response latency)
2. Response length and conversational pace (Words Per Minute - WPM)
3. Uncertainty markers, epistemic hedging, and qualifiers
4. Consolidated confidence score calculation and categorization
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from screening_ai.behavioral_models import (
    HesitationType,
    HesitationIncident,
    PaceRating,
    PaceMetrics,
    UncertaintySignal,
    TurnConfidenceMetrics,
)


class ConfidenceAnalyzer:
    """
    Evaluates vocal confidence, hesitation patterns, pacing, and certainty
    from transcript text and speech timing metadata.
    """

    # Common verbal fillers and hesitation sounds
    VOCAL_FILLERS = [
        (r"\b(um+h?|uh+m?|er+h?|ah+h?|hmm+)\b", HesitationType.FILLER_WORD, 4.0, "Vocal hesitation sound"),
        (r"\b(well|like|you know|sort of|kind of|i mean)\b", HesitationType.FILLER_WORD, 3.0, "Conversational filler"),
        (r"\b(basically|actually|literally)\b", HesitationType.FILLER_WORD, 1.5, "Verbal crutch word"),
    ]

    # Stutters and word repetitions (e.g. "I I", "the the", "we- we")
    REPETITION_PATTERN = re.compile(r"\b([a-zA-Z]{2,})\s+\1\b", re.IGNORECASE)
    FALSE_START_PATTERN = re.compile(r"\b([a-zA-Z]{1,4})-\s*([a-zA-Z]+)\b", re.IGNORECASE)

    # Uncertainty markers and epistemic hedging phrases
    HEDGING_PATTERNS = [
        r"\bi (think|guess|suppose|believe)\b",
        r"\b(maybe|perhaps|probably|possibly)\b",
        r"\b(not (really )?sure|not certain|hard to say)\b",
        r"\b(might be|could be|would say)\b",
        r"\b(as far as i (know|remember))\b",
        r"\b(to the best of my knowledge)\b",
        r"\b(kind of|sort of)\b",
    ]

    def __init__(
        self,
        optimal_wpm_min: float = 120.0,
        optimal_wpm_max: float = 165.0,
        latency_normal_max_ms: int = 3000,
    ):
        self.optimal_wpm_min = optimal_wpm_min
        self.optimal_wpm_max = optimal_wpm_max
        self.latency_normal_max_ms = latency_normal_max_ms

    def analyze_hesitations(
        self,
        text: str,
        latency_ms: Optional[int] = None,
        word_confidences: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[HesitationIncident], float]:
        """
        Detects fillers, repetitions, stutters, and timing latency.
        Returns a list of HesitationIncidents and the total penalty incurred.
        """
        incidents: List[HesitationIncident] = []
        total_penalty = 0.0

        if not text or not text.strip():
            return incidents, total_penalty

        lower_text = text.lower()

        # 1. Detect vocal fillers
        for regex_pat, h_type, penalty_per_hit, desc in self.VOCAL_FILLERS:
            matches = list(re.finditer(regex_pat, lower_text, re.IGNORECASE))
            if matches:
                count = len(matches)
                penalty = min(20.0, count * penalty_per_hit)
                incidents.append(
                    HesitationIncident(
                        type=h_type,
                        pattern=matches[0].group(0),
                        count=count,
                        penalty=penalty,
                        description=f"{desc} ('{matches[0].group(0)}') detected {count} time(s).",
                    )
                )
                total_penalty += penalty

        # 2. Detect direct word repetitions ("I I think", "the the code")
        rep_matches = list(self.REPETITION_PATTERN.finditer(lower_text))
        if rep_matches:
            count = len(rep_matches)
            penalty = min(15.0, count * 4.0)
            rep_words = [m.group(1) for m in rep_matches[:3]]
            incidents.append(
                HesitationIncident(
                    type=HesitationType.REPETITION,
                    pattern=", ".join(rep_words),
                    count=count,
                    penalty=penalty,
                    description=f"Word repetition detected {count} time(s): {', '.join(rep_words)}.",
                )
            )
            total_penalty += penalty

        # 3. Detect false starts and hyphenated stutters ("w- we built")
        false_starts = list(self.FALSE_START_PATTERN.finditer(lower_text))
        if false_starts:
            count = len(false_starts)
            penalty = min(15.0, count * 5.0)
            incidents.append(
                HesitationIncident(
                    type=HesitationType.FALSE_START,
                    pattern=false_starts[0].group(0),
                    count=count,
                    penalty=penalty,
                    description=f"False start/stutter detected {count} time(s).",
                )
            )
            total_penalty += penalty

        # 4. Latency delay (delay before starting answer)
        if latency_ms is not None and latency_ms > self.latency_normal_max_ms:
            excess_delay_sec = (latency_ms - self.latency_normal_max_ms) / 1000.0
            penalty = min(15.0, round(excess_delay_sec * 3.0, 1))
            incidents.append(
                HesitationIncident(
                    type=HesitationType.LATENCY_DELAY,
                    pattern=f"{latency_ms}ms",
                    count=1,
                    penalty=penalty,
                    description=f"Candidate paused for {latency_ms}ms before initiating answer.",
                )
            )
            total_penalty += penalty

        # 5. Extended internal pauses from word-level timings (>600ms between words)
        if word_confidences and len(word_confidences) > 1:
            extended_pauses = 0
            for i in range(len(word_confidences) - 1):
                cur_end = word_confidences[i].get("end_ms")
                next_start = word_confidences[i + 1].get("start_ms")
                if cur_end is not None and next_start is not None and (next_start - cur_end) > 650:
                    extended_pauses += 1
            if extended_pauses > 0:
                pause_penalty = min(12.0, extended_pauses * 3.0)
                incidents.append(
                    HesitationIncident(
                        type=HesitationType.EXTENDED_PAUSE,
                        pattern=f"{extended_pauses} pauses",
                        count=extended_pauses,
                        penalty=pause_penalty,
                        description=f"{extended_pauses} extended within-sentence pause(s) (>650ms) detected.",
                    )
                )
                total_penalty += pause_penalty

        # Cap total hesitation penalty at 35 points
        total_penalty = min(35.0, round(total_penalty, 1))
        return incidents, total_penalty

    def calculate_pacing(
        self,
        text: str,
        duration_seconds: Optional[float] = None,
        latency_ms: Optional[int] = None,
    ) -> PaceMetrics:
        """
        Measures word count, duration, Words Per Minute (WPM), and rates conversational pace.
        """
        words = text.split()
        word_count = len(words)

        # Estimate duration if not provided
        if duration_seconds is None or duration_seconds <= 0.0:
            # Baseline estimate: ~2.3 words per second (138 WPM)
            duration_seconds = max(1.0, round(word_count / 2.3, 2))
        else:
            duration_seconds = max(0.5, round(duration_seconds, 2))

        wpm = round((word_count / duration_seconds) * 60.0, 1)

        # Classify pace
        if wpm < 100.0:
            pace_rating = PaceRating.VERY_SLOW
            pacing_score = max(50.0, round(50.0 + (wpm / 100.0) * 25.0, 1))
        elif wpm < 120.0:
            pace_rating = PaceRating.SLOW
            pacing_score = round(75.0 + ((wpm - 100.0) / 20.0) * 15.0, 1)
        elif wpm <= 165.0:
            pace_rating = PaceRating.OPTIMAL
            pacing_score = 100.0
        elif wpm <= 185.0:
            pace_rating = PaceRating.FAST
            pacing_score = round(90.0 - ((wpm - 165.0) / 20.0) * 10.0, 1)
        else:
            pace_rating = PaceRating.RUSHED
            excess = min(60.0, wpm - 185.0)
            pacing_score = max(55.0, round(80.0 - (excess / 60.0) * 25.0, 1))

        latency_rating = None
        if latency_ms is not None:
            if latency_ms < 1500:
                latency_rating = "IMMEDIATE"
            elif latency_ms <= 3000:
                latency_rating = "NATURAL"
            elif latency_ms <= 5000:
                latency_rating = "THOUGHTFUL_PAUSE"
            else:
                latency_rating = "EXTENDED_DELAY"

        return PaceMetrics(
            duration_seconds=duration_seconds,
            word_count=word_count,
            wpm=wpm,
            pace_rating=pace_rating,
            latency_ms=latency_ms,
            latency_rating=latency_rating,
            pacing_score=pacing_score,
        )

    def detect_uncertainty(self, text: str) -> UncertaintySignal:
        """
        Identifies epistemic hedges, tentative language, and qualifiers.
        """
        if not text or not text.strip():
            return UncertaintySignal(
                hedging_phrases=[],
                hedging_count=0,
                uncertainty_score=0.0,
                confidence_discount=0.0,
                flagged_statements=[],
            )

        lower_text = text.lower()
        found_hedges: List[str] = []
        flagged_statements: List[str] = []

        sentences = re.split(r"[.!?]+", text)

        for pat in self.HEDGING_PATTERNS:
            matches = re.finditer(pat, lower_text, re.IGNORECASE)
            for m in matches:
                phrase = m.group(0).strip()
                if phrase not in found_hedges:
                    found_hedges.append(phrase)

        # Flag the specific sentences that contained hedging
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue
            for hedge in found_hedges:
                if re.search(r"\b" + re.escape(hedge) + r"\b", sent_clean, re.IGNORECASE):
                    if sent_clean not in flagged_statements:
                        flagged_statements.append(sent_clean)
                    break

        hedging_count = len(found_hedges)
        if hedging_count == 0:
            uncertainty_score = 0.0
            confidence_discount = 0.0
        elif hedging_count == 1:
            uncertainty_score = 30.0
            confidence_discount = 10.0
        elif hedging_count == 2:
            uncertainty_score = 55.0
            confidence_discount = 18.0
        elif hedging_count == 3:
            uncertainty_score = 75.0
            confidence_discount = 25.0
        else:
            uncertainty_score = min(100.0, 75.0 + (hedging_count - 3) * 8.0)
            confidence_discount = min(30.0, 25.0 + (hedging_count - 3) * 2.5)

        return UncertaintySignal(
            hedging_phrases=found_hedges,
            hedging_count=hedging_count,
            uncertainty_score=round(uncertainty_score, 1),
            confidence_discount=round(confidence_discount, 1),
            flagged_statements=flagged_statements[:3],
        )

    def evaluate_turn_confidence(
        self,
        raw_text: str,
        duration_seconds: Optional[float] = None,
        latency_ms: Optional[int] = None,
        stt_acoustic_confidence: Optional[float] = None,
        word_confidences: Optional[List[Dict[str, Any]]] = None,
    ) -> TurnConfidenceMetrics:
        """
        Consolidates hesitation, pacing, and uncertainty into an overall TurnConfidenceMetrics.
        """
        # Baseline acoustic score
        if stt_acoustic_confidence is not None:
            raw_confidence = min(100.0, max(0.0, stt_acoustic_confidence * 100.0))
        else:
            raw_confidence = 100.0

        # Hesitation Analysis
        incidents, hesitation_penalty = self.analyze_hesitations(
            raw_text, latency_ms=latency_ms, word_confidences=word_confidences
        )

        # Pacing Analysis
        pace_metrics = self.calculate_pacing(raw_text, duration_seconds=duration_seconds, latency_ms=latency_ms)

        # Uncertainty Analysis
        uncertainty = self.detect_uncertainty(raw_text)

        # Compute final score
        # Pace deduction if extreme (<70 pacing score)
        pace_deduction = max(0.0, round((100.0 - pace_metrics.pacing_score) * 0.2, 1))

        final_score = raw_confidence - hesitation_penalty - uncertainty.confidence_discount - pace_deduction
        final_score = max(10.0, min(100.0, round(final_score, 1)))

        if final_score >= 80.0:
            tier = "HIGH"
        elif final_score >= 60.0:
            tier = "MODERATE"
        else:
            tier = "LOW"

        return TurnConfidenceMetrics(
            raw_confidence=raw_confidence,
            hesitation_incidents=incidents,
            total_hesitation_penalty=hesitation_penalty,
            pace_metrics=pace_metrics,
            uncertainty=uncertainty,
            final_confidence_score=final_score,
            confidence_tier=tier,
        )
