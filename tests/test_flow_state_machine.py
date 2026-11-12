"""
Unit Tests: Day 29 Conversation State Machine
============================================
Tests formal finite state machine transitions, guards, illegal transitions,
terminal state behavior, and transition history auditability.
"""

import unittest
from screening_ai.flow_models import ConversationState
from screening_ai.state_machine import (
    ConversationStateMachine,
    InvalidStateTransitionError,
    ALLOWED_TRANSITIONS,
)


class TestConversationStateMachine(unittest.TestCase):
    """Test suite for ConversationStateMachine."""

    def setUp(self):
        self.fsm = ConversationStateMachine(initial_state=ConversationState.INITIALIZING)

    def test_initial_state(self):
        """Verify initial state and history initialization."""
        self.assertEqual(self.fsm.current_state, ConversationState.INITIALIZING)
        self.assertFalse(self.fsm.is_terminal)
        history = self.fsm.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["to_state"], ConversationState.INITIALIZING.value)

    def test_valid_transitions_happy_path(self):
        """Test a complete happy-path sequence of valid state transitions."""
        # INITIALIZING -> GREETING
        self.assertTrue(self.fsm.can_transition(ConversationState.GREETING))
        self.fsm.transition_to(ConversationState.GREETING, reason="Greeting started")
        self.assertEqual(self.fsm.current_state, ConversationState.GREETING)

        # GREETING -> AWAITING_INPUT
        self.assertTrue(self.fsm.can_transition(ConversationState.AWAITING_INPUT))
        self.fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Waiting for candidate")
        self.assertEqual(self.fsm.current_state, ConversationState.AWAITING_INPUT)

        # AWAITING_INPUT -> PROCESSING_INPUT
        self.assertTrue(self.fsm.can_transition(ConversationState.PROCESSING_INPUT))
        self.fsm.transition_to(ConversationState.PROCESSING_INPUT, reason="Candidate responded")
        self.assertEqual(self.fsm.current_state, ConversationState.PROCESSING_INPUT)

        # PROCESSING_INPUT -> FOLLOW_UP_PROBING
        self.assertTrue(self.fsm.can_transition(ConversationState.FOLLOW_UP_PROBING))
        self.fsm.transition_to(ConversationState.FOLLOW_UP_PROBING, reason="Probing deeper")
        self.assertEqual(self.fsm.current_state, ConversationState.FOLLOW_UP_PROBING)

        # FOLLOW_UP_PROBING -> AWAITING_INPUT
        self.fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Waiting for probe response")
        self.assertEqual(self.fsm.current_state, ConversationState.AWAITING_INPUT)

        # AWAITING_INPUT -> PROCESSING_INPUT
        self.fsm.transition_to(ConversationState.PROCESSING_INPUT, reason="Probe answered")
        self.assertEqual(self.fsm.current_state, ConversationState.PROCESSING_INPUT)

        # PROCESSING_INPUT -> TRANSITIONING_NEXT
        self.fsm.transition_to(ConversationState.TRANSITIONING_NEXT, reason="Moving to next question")
        self.assertEqual(self.fsm.current_state, ConversationState.TRANSITIONING_NEXT)

        # TRANSITIONING_NEXT -> WRAPUP
        self.fsm.transition_to(ConversationState.WRAPUP, reason="All questions complete")
        self.assertEqual(self.fsm.current_state, ConversationState.WRAPUP)

        # WRAPUP -> COMPLETED
        self.fsm.transition_to(ConversationState.COMPLETED, reason="Call completed")
        self.assertEqual(self.fsm.current_state, ConversationState.COMPLETED)
        self.assertTrue(self.fsm.is_terminal)

    def test_illegal_transition_raises_error(self):
        """Verify attempting an illegal jump raises InvalidStateTransitionError."""
        # INITIALIZING directly to COMPLETED is illegal
        self.assertFalse(self.fsm.can_transition(ConversationState.COMPLETED))
        with self.assertRaises(InvalidStateTransitionError):
            self.fsm.transition_to(ConversationState.COMPLETED)

        # INITIALIZING directly to PROCESSING_INPUT is illegal
        with self.assertRaises(InvalidStateTransitionError):
            self.fsm.transition_to(ConversationState.PROCESSING_INPUT)

    def test_terminal_states_disallow_further_transitions(self):
        """Verify terminal states disallow any subsequent state transitions."""
        self.fsm.transition_to(ConversationState.CALL_TERMINATED, reason="Forced disconnect")
        self.assertTrue(self.fsm.is_terminal)
        self.assertFalse(self.fsm.can_transition(ConversationState.GREETING))
        with self.assertRaises(InvalidStateTransitionError):
            self.fsm.transition_to(ConversationState.GREETING)

    def test_disruption_state_transitions(self):
        """Test transitions into disruption handlers (silence, confusion, repetition)."""
        self.fsm.transition_to(ConversationState.GREETING)
        self.fsm.transition_to(ConversationState.AWAITING_INPUT)

        # Silence disruption
        self.fsm.transition_to(ConversationState.HANDLING_SILENCE, reason="Silence detected")
        self.assertEqual(self.fsm.current_state, ConversationState.HANDLING_SILENCE)
        self.fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Nudge delivered")

        # Speech -> Confusion disruption
        self.fsm.transition_to(ConversationState.PROCESSING_INPUT)
        self.fsm.transition_to(ConversationState.HANDLING_CONFUSION, reason="Candidate confused")
        self.assertEqual(self.fsm.current_state, ConversationState.HANDLING_CONFUSION)
        self.fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Clarification delivered")

        # Speech -> Repetition disruption
        self.fsm.transition_to(ConversationState.PROCESSING_INPUT)
        self.fsm.transition_to(ConversationState.HANDLING_REPETITION, reason="Repeated answer")
        self.assertEqual(self.fsm.current_state, ConversationState.HANDLING_REPETITION)
        self.fsm.transition_to(ConversationState.FOLLOW_UP_PROBING, reason="Pivoting to probe")

    def test_self_transition_permitted(self):
        """Verify transitioning to current state is a no-op that succeeds."""
        self.fsm.transition_to(ConversationState.GREETING)
        same_state = self.fsm.transition_to(ConversationState.GREETING)
        self.assertEqual(same_state, ConversationState.GREETING)

    def test_force_state_override(self):
        """Test administrative force_state method overrides normal validation."""
        self.fsm.force_state(ConversationState.REPHRASING_FALLBACK, reason="Manual intervention")
        self.assertEqual(self.fsm.current_state, ConversationState.REPHRASING_FALLBACK)
        history = self.fsm.get_history()
        self.assertTrue(any("FORCED" in h["reason"] for h in history))

    def test_reset_functionality(self):
        """Verify reset returns state machine to initial state."""
        self.fsm.transition_to(ConversationState.GREETING)
        self.fsm.reset(initial_state=ConversationState.INITIALIZING)
        self.assertEqual(self.fsm.current_state, ConversationState.INITIALIZING)
        self.assertEqual(len(self.fsm.get_history()), 1)

    def test_transition_summary(self):
        """Verify formatted transition summary trace."""
        self.fsm.transition_to(ConversationState.GREETING)
        self.fsm.transition_to(ConversationState.AWAITING_INPUT)
        summary = self.fsm.get_transition_summary()
        self.assertEqual(summary, "INITIALIZING -> GREETING -> AWAITING_INPUT")


if __name__ == "__main__":
    unittest.main()
