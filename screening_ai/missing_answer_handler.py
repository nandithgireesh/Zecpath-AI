"""
Day 31: Missing Answer & Non-Response Handler
=============================================
Manages silence, acoustic fillers, explicit passes, and evasive non-answers:
- Evaluates candidate utterances for informational vacuum vs genuine engagement.
- Classifies non-responses into COMPLETE_SILENCE, EMPTY_FILLER, EXPLICIT_PASS, or EVASIVE_DEFLECTION.
- Implements a 4-Tier Progressive Recovery Ladder.
- Bridges skipped questions politely without crashing the conversational state machine.
- Protects candidate audit trails by distinguishing between audio failure and knowledge gap.
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from screening_ai.failure_models import (
    MissingAnswerType,
    MissingAnswerAssessment,
    ClarificationAction,
)


class MissingAnswerHandler:
    """
    Coordinates detection, classification, and progressive multi-tier recovery
    for missing, silent, empty, and evasive candidate responses.
    """

    # Pure filler acoustic tokens indicating line check or stall
    FILLER_LINE_CHECKS = [
        r"\b(hello|hey|hi)\b.*\b(hear me|there|audible)\b",
        r"\bam i audible\b",
        r"\bcan you hear me\b",
        r"\bis anyone there\b",
        r"^(uh+|um+|hmm+|er+|ah+)\.?$",
        r"^(hello|hi)\??$",
    ]

    # Explicit refusal / pass phrases
    EXPLICIT_PASS_PATTERNS = [
        r"\b(don't|do not) know\b",
        r"\bno idea\b",
        r"\b(pass|skip)\b.*?\b(question|this)?\b",
        r"\bnot sure\b",
        r"\bhaven't used\b",
        r"\bnever worked with\b",
        r"\bcan we (skip|move on)\b",
        r"\bnext question\b",
    ]

    # Evasive deflections
    EVASIVE_PATTERNS = [
        r"\bwhy (are you asking|do you need to know)\b",
        r"\bnot relevant\b",
        r"\blet's talk about (cricket|stocks|market|weather)\b",
        r"\bi won't answer\b",
        r"\bwho is this\b",
    ]

    @classmethod
    def assess_response(
        cls,
        text: str,
        duration_ms: int = 0,
        consecutive_missing_count: int = 0,
        topic: str = "this topic",
        next_topic: str = "the next area",
    ) -> MissingAnswerAssessment:
        """
        Assesses if an answer is missing, silent, empty, or evasive, and
        determines the appropriate recovery tier and dialogue prompt.
        """
        cleaned = text.strip() if text else ""
        t_lower = cleaned.lower()
        words = re.findall(r"\b\w+\b", t_lower)
        word_count = len(words)

        # 1. Complete Silence
        if word_count == 0:
            tier = min(4, consecutive_missing_count + 1)
            prompt = cls._get_recovery_prompt(MissingAnswerType.COMPLETE_SILENCE, tier, topic, next_topic)
            return MissingAnswerAssessment(
                duration_ms=duration_ms,
                word_count=0,
                filler_token_ratio=1.0,
                is_silence=True,
                is_empty_filler=False,
                is_explicit_pass=False,
                is_evasive=False,
                category=MissingAnswerType.COMPLETE_SILENCE,
                recovery_tier=tier,
                recovery_prompt=prompt,
            )

        # 2. Empty Filler (e.g. "uh... hello? can you hear me? am I audible?")
        is_empty_filler = any(re.search(pat, t_lower) for pat in cls.FILLER_LINE_CHECKS)
        if is_empty_filler and (word_count <= 12 or "hear me" in t_lower or "audible" in t_lower):
            tier = min(4, consecutive_missing_count + 1)
            prompt = cls._get_recovery_prompt(MissingAnswerType.EMPTY_FILLER, tier, topic, next_topic)
            return MissingAnswerAssessment(
                duration_ms=duration_ms,
                word_count=word_count,
                filler_token_ratio=0.85,
                is_silence=False,
                is_empty_filler=True,
                is_explicit_pass=False,
                is_evasive=False,
                category=MissingAnswerType.EMPTY_FILLER,
                recovery_tier=tier,
                recovery_prompt=prompt,
            )

        # 3. Explicit Pass (e.g. "I don't know, pass", "can we skip this question?")
        is_explicit_pass = any(re.search(pat, t_lower) for pat in cls.EXPLICIT_PASS_PATTERNS)
        if is_explicit_pass and (word_count <= 15 or "pass" in t_lower or "skip" in t_lower):
            # For explicit passes, we can immediately bridge to next topic
            tier = 3
            prompt = cls._get_recovery_prompt(MissingAnswerType.EXPLICIT_PASS, tier, topic, next_topic)
            return MissingAnswerAssessment(
                duration_ms=duration_ms,
                word_count=word_count,
                filler_token_ratio=0.10,
                is_silence=False,
                is_empty_filler=False,
                is_explicit_pass=True,
                is_evasive=False,
                category=MissingAnswerType.EXPLICIT_PASS,
                recovery_tier=tier,
                recovery_prompt=prompt,
            )

        # 4. Evasive Deflection (e.g. "Why are you asking this?")
        is_evasive = any(re.search(pat, t_lower) for pat in cls.EVASIVE_PATTERNS)
        if is_evasive:
            tier = 2
            prompt = cls._get_recovery_prompt(MissingAnswerType.EVASIVE_DEFLECTION, tier, topic, next_topic)
            return MissingAnswerAssessment(
                duration_ms=duration_ms,
                word_count=word_count,
                filler_token_ratio=0.0,
                is_silence=False,
                is_empty_filler=False,
                is_explicit_pass=False,
                is_evasive=True,
                category=MissingAnswerType.EVASIVE_DEFLECTION,
                recovery_tier=tier,
                recovery_prompt=prompt,
            )

        # 5. Normal Informative Answer
        return MissingAnswerAssessment(
            duration_ms=duration_ms,
            word_count=word_count,
            filler_token_ratio=0.0,
            is_silence=False,
            is_empty_filler=False,
            is_explicit_pass=False,
            is_evasive=False,
            category=MissingAnswerType.COMPLETE_SILENCE,
            recovery_tier=1,
            recovery_prompt=None,
        )

    @classmethod
    def _get_recovery_prompt(
        cls,
        category: MissingAnswerType,
        tier: int,
        topic: str,
        next_topic: str,
    ) -> str:
        """Generates progressive recovery prompts based on tier."""
        if category == MissingAnswerType.EMPTY_FILLER:
            if tier == 1:
                return "Yes, I can hear you loud and clear! Could you please share your experience regarding " + topic + "?"
            elif tier == 2:
                return "I'm still right here with you. Whenever you're ready, please tell me about your work with " + topic + "."
            else:
                return f"No worries at all. Let's move ahead to {next_topic}."

        if category == MissingAnswerType.EXPLICIT_PASS:
            return f"Understood, thank you for letting me know. Let's move forward and discuss {next_topic}."

        if category == MissingAnswerType.EVASIVE_DEFLECTION:
            return f"This question helps us understand your hands-on technical background for the role. Could you share any direct experience with {topic}?"

        # Default Silence Ladder
        if tier == 1:
            return f"I didn't catch your response. Could you please tell me about your experience with {topic}?"
        elif tier == 2:
            return f"Let's look at it from another angle: have you worked with {topic} or any related framework in production?"
        elif tier == 3:
            return f"No problem at all! Let's bridge forward and focus on {next_topic} instead."
        else:
            return "It seems we are having trouble connecting on this section. Let's wrap up this part and proceed to the next phase."
