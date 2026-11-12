"""
Day 29: Error-Handling Flow Design
==================================
Implements comprehensive conversational error recovery:
1. Silence Management (Multi-Tier Latency Nudges: 5s, 12s, 20s)
2. Confusion Detection & Dynamic Question Simplification
3. Repeated Answer Detection & Pivot Handling
4. Polite Failure & Circuit Breaker Logic (Max 2 Retries, Max 3 Failures)
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from screening_ai.flow_models import (
    NudgeLevel,
    SilenceEvent,
    ConfusionEvent,
    RepetitionEvent,
    RetryPolicyAction,
    DisruptionType,
)
from screening_ai.fallback_bank import (
    get_silence_nudge,
    get_simplified_question,
    get_paraphrase,
    CONFUSION_RESPONSES,
    REPETITION_PIVOTS,
    POLITE_SKIP_BRIDGES,
    DISCONNECT_WRAPUP,
)


class ErrorHandlingFlowManager:
    """
    Coordinates detection and response generation for conversational disruptions:
    Silence, Confusion, Repetition, and Retry Circuit Breakers.
    """

    # Thresholds (in milliseconds)
    SILENCE_GENTLE_THRESHOLD_MS = 5000     # 5 seconds
    SILENCE_ASSIST_THRESHOLD_MS = 10000    # 10 seconds
    SILENCE_TIMEOUT_THRESHOLD_MS = 20000   # 20 seconds

    MAX_RETRIES_PER_QUESTION = 2
    MAX_CONSECUTIVE_FAILURES = 3
    REPETITION_JACCARD_THRESHOLD = 0.60

    # Common linguistic confusion markers
    CONFUSION_PATTERNS = [
        r"\b(don't|do not) (understand|get it|follow)\b",
        r"\bwhat do you mean\b",
        r"\bcan you\b.*?\b(rephrase|clarify|repeat|explain|simplify)\b",
        r"\bcould you\b.*?\b(rephrase|clarify|repeat|explain|simplify)\b",
        r"\bnot sure what (you mean|you're asking|to say)\b",
        r"\b(sorry|pardon|excuse me)\b.*\b(again|repeat|what)\b",
        r"\b(too complicated|unclear|confusing)\b",
        r"\bwhat was the question\b",
        r"\bcome again\b"
    ]

    # Explicit repetition cues
    REPETITION_CUES = [
        r"\bas (i|we) (mentioned|said|stated|told you|explained)\b",
        r"\b(already|previously) (answered|told you|mentioned|said)\b",
        r"\blike i (said|mentioned) before\b",
        r"\bsame (answer|thing) as (before|earlier)\b",
        r"\bi already have (explained|said)\b"
    ]

    def __init__(self):
        self._compiled_confusion = [re.compile(p, re.IGNORECASE) for p in self.CONFUSION_PATTERNS]
        self._compiled_repetition = [re.compile(p, re.IGNORECASE) for p in self.REPETITION_CUES]

    # -------------------------------------------------------------------------
    # 1. Silence Handling
    # -------------------------------------------------------------------------
    def evaluate_silence(self, duration_ms: int, consecutive_silence_count: int = 1) -> SilenceEvent:
        """
        Evaluate candidate silence duration and emit the appropriate multi-tier nudge.
        """
        if duration_ms >= self.SILENCE_TIMEOUT_THRESHOLD_MS or consecutive_silence_count >= 3:
            level = NudgeLevel.TIMEOUT_TRANSITION
            is_timeout = True
            prompt = get_silence_nudge(level, consecutive_silence_count - 1)
        elif duration_ms >= self.SILENCE_ASSIST_THRESHOLD_MS or consecutive_silence_count == 2:
            level = NudgeLevel.ASSIST_REPHRASE
            is_timeout = False
            prompt = get_silence_nudge(level, consecutive_silence_count - 1)
        else:
            level = NudgeLevel.GENTLE_CHECK
            is_timeout = False
            prompt = get_silence_nudge(level, consecutive_silence_count - 1)

        return SilenceEvent(
            silence_duration_ms=duration_ms,
            nudge_level=level,
            consecutive_silence_count=consecutive_silence_count,
            is_timeout=is_timeout,
            nudge_prompt=prompt
        )

    # -------------------------------------------------------------------------
    # 2. Confusion Handling
    # -------------------------------------------------------------------------
    def detect_confusion(self, candidate_text: str, question_id: Optional[str] = None) -> Optional[ConfusionEvent]:
        """
        Detect if the candidate is expressing confusion or requesting a rephrase.
        Returns ConfusionEvent if matched, otherwise None.
        """
        if not candidate_text:
            return None

        clean_text = candidate_text.strip().lower()

        # Check explicit regex cues
        matched_cue = None
        for pattern in self._compiled_confusion:
            match = pattern.search(clean_text)
            if match:
                matched_cue = match.group(0)
                break

        # Check short ambiguous statements
        if not matched_cue:
            if clean_text in ("what?", "huh?", "sorry?", "pardon?", "can you repeat?", "i don't know"):
                matched_cue = clean_text

        if not matched_cue:
            return None

        # Build empathic clarification
        acknowledgment = CONFUSION_RESPONSES[hash(matched_cue) % len(CONFUSION_RESPONSES)]
        fallback_q = None
        if question_id:
            fallback_q = get_simplified_question(question_id)
            suggested_text = f"{acknowledgment} {fallback_q}"
        else:
            suggested_text = f"{acknowledgment} Let's look at this through a simple real-world example."

        return ConfusionEvent(
            trigger_phrase=matched_cue,
            confusion_level="MODERATE" if "simplify" in clean_text else "MILD",
            suggested_clarification=suggested_text,
            fallback_question_used=fallback_q
        )

    # -------------------------------------------------------------------------
    # 3. Repetition Handling
    # -------------------------------------------------------------------------
    def detect_repetition(
        self,
        candidate_text: str,
        previous_turns: List[str]
    ) -> Optional[RepetitionEvent]:
        """
        Detect if candidate is repeating their prior answers or explicitly signaling repetition.
        """
        if not candidate_text or not previous_turns:
            return None

        clean_text = candidate_text.strip().lower()

        # Check explicit linguistic repetition markers ("as I said before")
        for pattern in self._compiled_repetition:
            match = pattern.search(clean_text)
            if match:
                pivot = REPETITION_PIVOTS[0]
                return RepetitionEvent(
                    previous_turn_index=len(previous_turns) - 1,
                    similarity_score=1.0,
                    repeated_snippet=match.group(0),
                    pivot_prompt=pivot
                )

        # Token-based Jaccard similarity against recent turns
        tokens_current = set(re.findall(r"\w+", clean_text))
        # Remove common stop words for reliable comparison
        stopwords = {"i", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "my", "is", "was", "it"}
        tokens_current = tokens_current - stopwords

        if len(tokens_current) < 3:
            return None

        for idx, prev_text in enumerate(reversed(previous_turns[-3:])):
            tokens_prev = set(re.findall(r"\w+", prev_text.lower())) - stopwords
            if not tokens_prev:
                continue

            intersection = tokens_current.intersection(tokens_prev)
            union = tokens_current.union(tokens_prev)
            jaccard = len(intersection) / len(union) if union else 0.0

            if jaccard >= self.REPETITION_JACCARD_THRESHOLD:
                pivot = REPETITION_PIVOTS[idx % len(REPETITION_PIVOTS)]
                overlap_sample = ", ".join(list(intersection)[:4])
                return RepetitionEvent(
                    previous_turn_index=len(previous_turns) - 1 - idx,
                    similarity_score=round(jaccard, 2),
                    repeated_snippet=overlap_sample,
                    pivot_prompt=pivot
                )

        return None

    # -------------------------------------------------------------------------
    # 4. Polite Failure & Retry Circuit Breaker
    # -------------------------------------------------------------------------
    def evaluate_retry_policy(
        self,
        question_id: str,
        current_retries: int,
        consecutive_failures: int
    ) -> Tuple[RetryPolicyAction, str]:
        """
        Determine if the question should be retried, simplified, skipped, or call ended.
        """
        # Global failure threshold: if 3 questions fail in a row with zero audio or disconnect
        if consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            return RetryPolicyAction.ABORT_CALL, DISCONNECT_WRAPUP

        # Question-level retry circuit breaker
        if current_retries >= self.MAX_RETRIES_PER_QUESTION:
            bridge = POLITE_SKIP_BRIDGES[current_retries % len(POLITE_SKIP_BRIDGES)]
            return RetryPolicyAction.SKIP_QUESTION, bridge

        if current_retries == 1:
            # First retry: offer simplified question
            simplified = get_simplified_question(question_id)
            prompt = f"No worries at all. Let me rephrase: {simplified}"
            return RetryPolicyAction.TRY_FALLBACK, prompt

        # Zero retries: normal attempt
        return RetryPolicyAction.RETRY_PRIMARY, "Let's take another look at this."
