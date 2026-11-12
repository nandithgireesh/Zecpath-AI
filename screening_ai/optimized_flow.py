"""
Day 30 - Optimized Conversation Flow Logic
==========================================
Provides adaptive conversational behavior including empathy-driven reassurance for
nervous candidates, precision micro-probing for terse high-value responses, and
dynamic pacing adjustments.
"""

from typing import Dict, Any, Optional, Tuple

from screening_ai.flow_models import (
    CallFlowAction,
    ActionType,
    ConversationState,
    CallSessionState,
)
from screening_ai.call_flow_engine import AICallFlowEngine


class OptimizedCallFlowController:
    """
    Day 30 - Orchestrator for optimized real-world conversation dynamics.
    Enriches AI call behavior to eliminate conversational friction.
    """

    def __init__(self, engine: Optional[AICallFlowEngine] = None):
        self.engine = engine or AICallFlowEngine()

    def process_candidate_utterance_with_optimization(
        self,
        session_id: str,
        candidate_utterance: str,
        silence_ms: int = 0,
        hesitation_count: int = 0,
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """
        Processes candidate response with adaptive micro-probing and empathy reassurance.
        """
        session = self.engine.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found")

        words = candidate_utterance.strip().split()
        word_count = len(words)

        # 1. Check Terse High-Skill Micro-Probe
        is_terse = (5 <= word_count < 15)
        has_tech = any(kw.lower() in candidate_utterance.lower() for kw in [
            "kafka", "redis", "kubernetes", "docker", "postgres", "raft", "celery", "aws"
        ])

        # 2. Check Nervous Hesitation Adaptation
        is_hesitant = (hesitation_count >= 3)

        # Process through core engine
        session, action = self.engine.process_turn(
            session_id=session_id,
            candidate_utterance=candidate_utterance,
            silence_ms=silence_ms,
        )

        # Apply adaptive conversational enhancements
        if is_terse and has_tech and action.action_type in [ActionType.SPEAK_PRIMARY, ActionType.SPEAK_PROBE]:
            action.text_to_speak = (
                f"Got it. To go just a bit deeper, could you share one specific challenge "
                f"or implementation detail with that? Also: {action.text_to_speak}"
            )
            action.metadata["adaptive_probe"] = "terse_domain_deepen"

        elif is_hesitant and action.action_type in [ActionType.SPEAK_PRIMARY, ActionType.SPEAK_PROBE]:
            action.text_to_speak = (
                f"Thank you, that was very clear. Take your time, there's no rush at all. "
                f"{action.text_to_speak}"
            )
            action.metadata["adaptive_reassurance"] = "nervous_pacing_cushion"

        return session, action
