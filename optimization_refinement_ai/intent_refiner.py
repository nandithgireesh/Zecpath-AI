"""
Day 54: Optimization & Refinement - Intent Refiner Module
=========================================================
Implements advanced intent disambiguation:
1. Disambiguates conceptual thinking pauses (deliberate algorithmic formulation)
   from nervous hesitation / knowledge gaps.
2. Identifies implicit STAR (Situation, Task, Action, Result) narrative arcs
   in unstructured answers.
3. Detects evasive deflection and non-committal circumlocution.
"""

import re
from typing import Dict, List, Optional, Tuple
from optimization_refinement_ai.models import PauseType, IntentRefinementTelemetry


class IntentRefiner:
    """
    Enterprise Intent Disambiguation Engine for technical interview responses.
    Prevents false negatives caused by penalizing deliberate problem-solving pauses.
    """

    # Technical depth indicators indicating cognitive formulation rather than hesitance
    TECHNICAL_MARKERS = {
        "distributed", "concurrency", "trade-off", "tradeoff", "latency", "throughput",
        "sharding", "replication", "eventual consistency", "idempotency", "quorum",
        "cache-aside", "write-through", "b-tree", "lsm-tree", "asynchronous", "thread",
        "mutex", "deadlock", "algorithm", "complexity", "o(n", "o(log", "partition",
        "consensus", "raft", "paxos", "backpressure", "circuit breaker", "load balancer"
    }

    # Filler markers indicating verbal hesitation
    FILLER_MARKERS = {
        "um", "uh", "er", "ah", "like", "you know", "i mean", "sort of", "kind of",
        "basically", "honestly", "actually", "to be honest", "i guess"
    }

    # Evasive phrases indicating deflection rather than direct answering
    EVASIVE_PHRASES = [
        r"i usually let (the team|others) handle",
        r"that wasn't really my responsibility",
        r"as i said earlier",
        r"it's hard to explain without my notes",
        r"it depends on too many factors to say",
        r"we didn't need to worry about that",
        r"i don't recall the specifics but it worked",
        r"someone else built that part",
        r"not something we looked into"
    ]

    # Implicit STAR indicators
    STAR_PATTERNS = {
        "situation": [
            r"\b(at|when|during|in my previous role|we faced|the system had|the context was|our client had)\b",
            r"\b(legacy code|production issue|outage|scaling bottleneck|spike in traffic)\b"
        ],
        "task": [
            r"\b(my goal was|i was tasked with|i needed to|objective was|the requirement was|we had to achieve)\b",
            r"\b(target|sla|deliver|migrate|refactor|optimize)\b"
        ],
        "action": [
            r"\b(i designed|i implemented|i profiled|i refactored|i benchmarked|i migrated|i architected|i wrote)\b",
            r"\b(we deployed|i introduced|i isolated|i added monitoring|i configured)\b"
        ],
        "result": [
            r"\b(resulting in|which reduced|improved by|achieved|lowered latency|cut costs|increased throughput)\b",
            r"\b(from \d+ to \d+|\d+ percent|zero downtime|p99 dropped|saved)\b"
        ]
    }

    def __init__(self):
        # Pre-compile regex patterns for microsecond latency
        self._compiled_evasive = [re.compile(p, re.IGNORECASE) for p in self.EVASIVE_PHRASES]
        self._compiled_star = {
            dim: [re.compile(p, re.IGNORECASE) for p in patterns]
            for dim, patterns in self.STAR_PATTERNS.items()
        }

    def classify_pause(
        self,
        pause_duration_seconds: float,
        subsequent_transcript: str
    ) -> Tuple[PauseType, float]:
        """
        Disambiguates whether a pause was conceptual thinking or nervous hesitation.
        
        Returns:
            Tuple[PauseType, penalty_adjustment_points]
            - If CONCEPTUAL_THINKING: 0 penalty (or refund previous default penalty).
            - If NERVOUS_HESITATION: negative penalty points proportional to severity.
            - If NORMAL_CADENCE: 0 penalty.
        """
        if pause_duration_seconds < 2.5:
            return PauseType.NORMAL_CADENCE, 0.0

        text_lower = subsequent_transcript.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        total_words = len(words)
        if total_words == 0:
            # Extended silence with no subsequent answer
            return PauseType.NERVOUS_HESITATION, -5.0

        # Measure technical density
        tech_hits = sum(1 for marker in self.TECHNICAL_MARKERS if marker in text_lower)
        
        # Measure filler density
        filler_hits = sum(1 for w in words if w in self.FILLER_MARKERS)
        for filler_phrase in ["you know", "i mean", "sort of", "kind of", "to be honest"]:
            if filler_phrase in text_lower:
                filler_hits += 2

        filler_ratio = filler_hits / max(1, total_words)

        # Decision rule: High technical formulation with moderate/low filler is conceptual thinking
        if tech_hits >= 2 and filler_ratio < 0.08:
            # Candidate paused to organize a complex architecture/algorithmic answer
            return PauseType.CONCEPTUAL_THINKING, 0.0
        elif pause_duration_seconds > 4.5 and (filler_ratio >= 0.08 or tech_hits == 0):
            # Nervous hesitation or struggling for answer
            penalty = -min(5.0, 1.0 + (pause_duration_seconds - 3.0) * 0.8)
            return PauseType.NERVOUS_HESITATION, round(penalty, 1)
        else:
            return PauseType.NORMAL_CADENCE, 0.0

    def evaluate_implicit_star(self, transcript: str) -> float:
        """
        Calculates implicit STAR coverage (0.0 to 100.0) from unstructured response.
        Each of S, T, A, R contributes 25 points.
        """
        if not transcript or not transcript.strip():
            return 0.0

        coverage = 0.0
        for dim, patterns in self._compiled_star.items():
            matched = any(p.search(transcript) for p in patterns)
            if matched:
                coverage += 25.0

        return coverage

    def detect_evasive_deflection(self, transcript: str) -> float:
        """
        Estimates the probability of evasive deflection in candidate response (0.0 to 1.0).
        """
        if not transcript or not transcript.strip():
            return 0.0

        matches = sum(1 for p in self._compiled_evasive if p.search(transcript))
        # Each deflection phrase raises probability
        prob = min(1.0, matches * 0.35)
        return round(prob, 2)

    def refine_candidate_intent(
        self,
        pause_duration_seconds: float,
        response_transcript: str
    ) -> IntentRefinementTelemetry:
        """
        Executes unified intent refinement telemetry for a candidate response segment.
        """
        pause_type, penalty_adj = self.classify_pause(pause_duration_seconds, response_transcript)
        star_coverage = self.evaluate_implicit_star(response_transcript)
        evasion_prob = self.detect_evasive_deflection(response_transcript)

        # Base confidence calculation
        confidence = 90.0
        if pause_type == PauseType.CONCEPTUAL_THINKING:
            confidence += 5.0
        elif pause_type == PauseType.NERVOUS_HESITATION:
            confidence -= 8.0

        if evasion_prob > 0.4:
            confidence -= 15.0

        confidence = max(50.0, min(99.0, confidence))

        return IntentRefinementTelemetry(
            pause_duration_seconds=pause_duration_seconds,
            pause_classification=pause_type,
            implicit_star_coverage=star_coverage,
            evasive_deflection_probability=evasion_prob,
            intent_confidence_score=round(confidence, 1),
            penalty_adjustment_points=penalty_adj
        )
