"""
Day 29: Conversation State Machine
==================================
Implements an auditable Finite State Machine (FSM) enforcing legal
conversational flow transitions, guard validations, and transition breadcrumbs.
"""

from typing import Dict, Set, List, Tuple, Optional, Any
from datetime import datetime, timezone
from screening_ai.flow_models import ConversationState


# -----------------------------------------------------------------------------
# Legal Transition Graph
# -----------------------------------------------------------------------------
ALLOWED_TRANSITIONS: Dict[ConversationState, Set[ConversationState]] = {
    ConversationState.INITIALIZING: {
        ConversationState.GREETING,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.GREETING: {
        ConversationState.AWAITING_INPUT,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.AWAITING_INPUT: {
        ConversationState.PROCESSING_INPUT,
        ConversationState.HANDLING_SILENCE,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.PROCESSING_INPUT: {
        ConversationState.FOLLOW_UP_PROBING,
        ConversationState.REPHRASING_FALLBACK,
        ConversationState.HANDLING_CONFUSION,
        ConversationState.HANDLING_REPETITION,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.WRAPUP,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.FOLLOW_UP_PROBING: {
        ConversationState.AWAITING_INPUT,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.REPHRASING_FALLBACK: {
        ConversationState.AWAITING_INPUT,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.HANDLING_SILENCE: {
        ConversationState.AWAITING_INPUT,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.HANDLING_CONFUSION: {
        ConversationState.AWAITING_INPUT,
        ConversationState.REPHRASING_FALLBACK,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.HANDLING_REPETITION: {
        ConversationState.AWAITING_INPUT,
        ConversationState.FOLLOW_UP_PROBING,
        ConversationState.TRANSITIONING_NEXT,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.TRANSITIONING_NEXT: {
        ConversationState.AWAITING_INPUT,
        ConversationState.WRAPUP,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.WRAPUP: {
        ConversationState.COMPLETED,
        ConversationState.CALL_TERMINATED,
    },
    ConversationState.COMPLETED: set(),  # Terminal state
    ConversationState.CALL_TERMINATED: set(),  # Terminal state
}


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal state transition is attempted."""
    pass


class ConversationStateMachine:
    """
    State machine governing the life cycle of an AI screening conversation.
    Tracks state transitions, enforces transition rules, and maintains history.
    """

    def __init__(self, initial_state: ConversationState = ConversationState.INITIALIZING):
        self._current_state: ConversationState = initial_state
        self._history: List[Dict[str, Any]] = [
            {
                "from_state": None,
                "to_state": initial_state.value,
                "reason": "Session initialization",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

    @property
    def current_state(self) -> ConversationState:
        """Get the current conversation state."""
        return self._current_state

    @property
    def is_terminal(self) -> bool:
        """Check if current state is a terminal end state."""
        return self._current_state in (ConversationState.COMPLETED, ConversationState.CALL_TERMINATED)

    def can_transition(self, target_state: ConversationState) -> bool:
        """
        Check if transitioning from current state to target state is legally allowed.
        """
        if self.is_terminal:
            return False
        allowed = ALLOWED_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition_to(self, target_state: ConversationState, reason: str = "") -> ConversationState:
        """
        Advance the state machine to target_state if valid.
        Raises InvalidStateTransitionError if transition is illegal.
        """
        if target_state == self._current_state:
            # Self-transitions are permitted for staying in state (e.g. repeated wait)
            return self._current_state

        if not self.can_transition(target_state):
            allowed = [s.value for s in ALLOWED_TRANSITIONS.get(self._current_state, set())]
            raise InvalidStateTransitionError(
                f"Illegal state transition: Cannot transition from '{self._current_state.value}' "
                f"to '{target_state.value}'. Allowed transitions from '{self._current_state.value}': {allowed}"
            )

        from_state = self._current_state
        self._current_state = target_state
        self._history.append({
            "from_state": from_state.value,
            "to_state": target_state.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return self._current_state

    def force_state(self, state: ConversationState, reason: str = "Admin override") -> ConversationState:
        """Emergency administrative or recovery transition overriding normal checks."""
        from_state = self._current_state
        self._current_state = state
        self._history.append({
            "from_state": from_state.value,
            "to_state": state.value,
            "reason": f"FORCED: {reason}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return self._current_state

    def reset(self, initial_state: ConversationState = ConversationState.INITIALIZING):
        """Reset state machine to initial state."""
        self._current_state = initial_state
        self._history = [
            {
                "from_state": None,
                "to_state": initial_state.value,
                "reason": "Machine reset",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the immutable audit log of transitions."""
        return list(self._history)

    def get_transition_summary(self) -> str:
        """Return a human-readable trace of state transitions."""
        trace = [f"{entry['to_state']}" for entry in self._history]
        return " -> ".join(trace)
