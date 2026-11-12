"""
Day 38: Logical Reasoning Scoring Model (Deliverable 2)
======================================================
Evaluates candidate cognitive reasoning capabilities:
- Premise identification & boundary grounding
- Multi-step causal inference chains (deductive & inductive reasoning)
- Trade-off evaluation & counter-factual depth
- Logical fallacy detection (false dilemma, hasty conclusion, circular logic, blame deflection)
- Calibrated Logical Reasoning Score in [0, 100]
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from interview_ai.aptitude_models import LogicalReasoningBreakdown, ReasoningQuestion, SituationalScenario


class LogicalReasoningScorer:
    """
    Quantitative evaluation engine for logical thinking ability and cognitive soundness.
    Analyzes premise grounding, causal chain density, trade-off awareness, and fallacies.
    """

    # 1. Causal Inference Connectors
    CAUSAL_CONNECTORS = [
        "because", "therefore", "as a result", "consequently", "leads to",
        "due to", "this implies", "subsequently", "which causes", "in order to",
        "so that", "since", "stemming from", "resulting in", "yields",
    ]

    # 2. Premise & Hypothesis Framing Cues
    PREMISE_MARKERS = [
        "the core issue", "the root cause", "primary bottleneck", "underlying problem",
        "assuming that", "given that", "the key premise", "we must first establish",
        "initial hypothesis", "first identify", "baseline", "boundary condition",
    ]

    # 3. Trade-off & Nuance Indicators
    TRADEOFF_MARKERS = [
        "trade-off", "tradeoff", "on the other hand", "on one hand",
        "downside is", "upside is", "compromise", "while this optimizes",
        "alternatively", "cost versus benefit", "short-term versus long-term",
        "mitigate", "at the expense of", "pros and cons", "weighing the impact",
    ]

    # 4. Fallacy Regex Patterns & Deductions
    FALLACY_RULES = [
        (
            "FALSE_DILEMMA",
            re.compile(r"\b(only option is|have no choice but|either we .* or (everything|we) (fails|dies)|there is no other way)\b", re.IGNORECASE),
            10.0,
            "False Dilemma: Framed resolution as an extreme binary without considering intermediate mitigations."
        ),
        (
            "HASTY_CONCLUSION",
            re.compile(r"\b(just rewrite the whole|fire the (person|engineer|developer)|scrap everything and start over|obviously everyone knows)\b", re.IGNORECASE),
            12.0,
            "Hasty Conclusion: Jumped to aggressive overhauls or punitive actions without root-cause diagnosis."
        ),
        (
            "CIRCULAR_REASONING",
            re.compile(r"\b(it is broken because it does not work|failed because it was failing|important because it is critical)\b", re.IGNORECASE),
            8.0,
            "Circular Reasoning: Asserted tautological claims without explanatory causal backing."
        ),
        (
            "BLAME_DEFLECTION",
            re.compile(r"\b(not my problem|not my job|management's fault|pm messed up|their mistake not mine)\b", re.IGNORECASE),
            10.0,
            "Blame Deflection: Deflected professional ownership toward external parties instead of solving the constraint."
        ),
    ]

    def __init__(self):
        pass

    def evaluate(
        self,
        candidate_response: str,
        question_or_scenario: Optional[Any] = None,
    ) -> LogicalReasoningBreakdown:
        """
        Evaluate candidate response for logical rigor, premise analysis, and fallacy avoidance.
        """
        if not candidate_response or not candidate_response.strip():
            return LogicalReasoningBreakdown(
                premise_identification_score=0.0,
                causal_inference_score=0.0,
                tradeoff_depth_score=0.0,
                fallacy_deductions=0.0,
                detected_fallacies=["EMPTY_RESPONSE"],
                calibrated_logic_score=0.0,
            )

        resp_lower = candidate_response.lower()
        word_count = len(re.findall(r"\b\w+\b", candidate_response))

        # 1. Premise Identification Score (0 - 100)
        premise_score = self._score_premise_identification(resp_lower, word_count, question_or_scenario)

        # 2. Causal Inference Score (0 - 100)
        causal_score = self._score_causal_chains(resp_lower, word_count)

        # 3. Trade-off & Nuance Depth Score (0 - 100)
        tradeoff_score = self._score_tradeoff_depth(resp_lower, word_count, question_or_scenario)

        # 4. Fallacy Detection & Deductions
        fallacy_deductions, detected_fallacies = self._detect_fallacies(resp_lower)

        # 5. Composite Calibration
        # Base weightage: Premise 30%, Causal 40%, Trade-off 30%
        raw_composite = (0.30 * premise_score) + (0.40 * causal_score) + (0.30 * tradeoff_score)
        calibrated_score = max(0.0, min(100.0, raw_composite - fallacy_deductions))

        return LogicalReasoningBreakdown(
            premise_identification_score=round(premise_score, 1),
            causal_inference_score=round(causal_score, 1),
            tradeoff_depth_score=round(tradeoff_score, 1),
            fallacy_deductions=round(fallacy_deductions, 1),
            detected_fallacies=detected_fallacies,
            calibrated_logic_score=round(calibrated_score, 1),
        )

    def _score_premise_identification(
        self,
        resp_lower: str,
        word_count: int,
        target_context: Optional[Any],
    ) -> float:
        """Evaluate how thoroughly candidate identified boundary premises."""
        base_score = 40.0  # Baseline presence

        # Check explicit premise markers
        marker_hits = sum(1 for marker in self.PREMISE_MARKERS if marker in resp_lower)
        base_score += min(35.0, marker_hits * 12.0)

        # Check domain-specific premise cues from question/scenario if present
        if target_context:
            premises = getattr(target_context, "target_premises", [])
            if not premises and hasattr(target_context, "constraints"):
                premises = target_context.constraints

            if premises:
                matched_premises = 0
                for prem in premises:
                    prem_words = [w.lower() for w in re.findall(r"\b\w{4,}\b", prem)]
                    if any(pw in resp_lower for pw in prem_words):
                        matched_premises += 1
                premise_match_ratio = matched_premises / max(1, len(premises))
                base_score += min(25.0, premise_match_ratio * 25.0)
            else:
                base_score += 15.0
        else:
            base_score += 15.0

        # Brevity penalty for shallow assertions (<25 words)
        if word_count < 25:
            base_score *= (word_count / 25.0)

        return min(100.0, max(10.0, base_score))

    def _score_causal_chains(self, resp_lower: str, word_count: int) -> float:
        """Evaluate frequency and density of causal deduction connectors."""
        if word_count == 0:
            return 0.0

        connector_count = 0
        for conn in self.CAUSAL_CONNECTORS:
            connector_count += len(re.findall(r"\b" + re.escape(conn) + r"\b", resp_lower))

        # Density per 100 words
        density = (connector_count / max(1, word_count)) * 100.0

        # Benchmark: 3.0 to 6.0 connectors per 100 words represents methodical deduction
        if density >= 4.0:
            score = 90.0 + min(10.0, (density - 4.0) * 3.0)
        elif density >= 2.5:
            score = 75.0 + (density - 2.5) * 10.0
        elif density >= 1.0:
            score = 55.0 + (density - 1.0) * 13.0
        else:
            score = 30.0 + (density * 25.0)

        # Reward presence of multi-step sequence signposts (e.g. "if ... then ... therefore")
        has_conditional = bool(re.search(r"\bif\b.*\bthen\b", resp_lower))
        if has_conditional:
            score += 6.0

        return min(100.0, max(10.0, score))

    def _score_tradeoff_depth(
        self,
        resp_lower: str,
        word_count: int,
        target_context: Optional[Any],
    ) -> float:
        """Evaluate nuanced balancing of competing priorities and alternatives."""
        base_score = 35.0

        tradeoff_hits = sum(1 for marker in self.TRADEOFF_MARKERS if marker in resp_lower)
        base_score += min(45.0, tradeoff_hits * 15.0)

        # Context-specific required trade-offs check
        if target_context and hasattr(target_context, "required_tradeoffs") and target_context.required_tradeoffs:
            req_hits = 0
            for req in target_context.required_tradeoffs:
                req_words = [w.lower() for w in re.findall(r"\b\w{4,}\b", req)]
                if any(rw in resp_lower for rw in req_words):
                    req_hits += 1
            base_score += min(20.0, (req_hits / len(target_context.required_tradeoffs)) * 20.0)
        else:
            # General nuance bonus if candidate uses balanced comparative language
            if "however" in resp_lower or "whereas" in resp_lower or "while" in resp_lower:
                base_score += 15.0

        return min(100.0, max(10.0, base_score))

    def _detect_fallacies(self, resp_lower: str) -> Tuple[float, List[str]]:
        """Identify logical fallacies and compute deduction penalties."""
        deductions = 0.0
        detected = []

        for name, regex, penalty, desc in self.FALLACY_RULES:
            if regex.search(resp_lower):
                deductions += penalty
                detected.append(f"{name}: {desc}")

        return min(50.0, deductions), detected
