"""
Day 29: AI Call Flow Engine & Decision Tree
===========================================
Integrates the Conversation State Machine, Error Handling Flow,
Fallback Question Bank, and multi-turn session tracking into an
adaptive recruitment screening call manager.
"""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone

from screening_ai.flow_models import (
    CallPhase,
    ConversationState,
    DisruptionType,
    ActionType,
    NudgeLevel,
    RetryPolicyAction,
    CallFlowAction,
    ConversationTurn,
    CallSessionState,
    CallSessionSummary,
)
from screening_ai.state_machine import ConversationStateMachine
from screening_ai.error_handling_flow import ErrorHandlingFlowManager
from screening_ai.fallback_bank import (
    FALLBACK_QUESTIONS,
    get_fallback_for_question,
    get_simplified_question,
    get_paraphrase,
    get_scenario,
    POLITE_SKIP_BRIDGES,
    DISCONNECT_WRAPUP,
)


class AICallFlowEngine:
    """
    Master conversational coordinator executing the AI Call Decision Tree.
    Manages active screening sessions, state machines, error recovery, and next-step actions.
    """

    DEFAULT_TECHNICAL_QUESTIONS = [
        "sys_design_scalability",
        "microservices_communication",
        "database_optimization",
        "concurrency_async"
    ]

    DEFAULT_OPERATIONAL_QUESTIONS = [
        "salary_expectation",
        "notice_period_availability"
    ]

    def __init__(self):
        self._sessions: Dict[str, CallSessionState] = {}
        self._state_machines: Dict[str, ConversationStateMachine] = {}
        self._error_manager = ErrorHandlingFlowManager()

    # -------------------------------------------------------------------------
    # Session Management
    # -------------------------------------------------------------------------
    def start_session(
        self,
        candidate_id: str,
        candidate_name: str,
        role_name: str,
        question_ids: Optional[List[str]] = None
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """
        Initialize a new screening call session, start state machine, and emit greeting.
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        all_questions = list(question_ids or self.DEFAULT_TECHNICAL_QUESTIONS) + self.DEFAULT_OPERATIONAL_QUESTIONS

        fsm = ConversationStateMachine(initial_state=ConversationState.INITIALIZING)
        self._state_machines[session_id] = fsm

        greeting_text = (
            f"Hello {candidate_name}! I'm the Zecpath-AI technical screening assistant calling regarding "
            f"your application for the {role_name} position. Can you hear me clearly, and are you ready to begin?"
        )

        fsm.transition_to(ConversationState.GREETING, reason="Emitting call greeting")

        action = CallFlowAction(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            action_type=ActionType.SPEAK_PRIMARY,
            text_to_speak=greeting_text,
            next_state=ConversationState.AWAITING_INPUT,
            current_phase=CallPhase.GREETING_CONSENT,
            should_listen=True,
            metadata={"greeting_type": "initial_welcome"}
        )

        session = CallSessionState(
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role_name=role_name,
            current_phase=CallPhase.GREETING_CONSENT,
            current_state=ConversationState.AWAITING_INPUT,
            current_question_index=0,
            question_ids=all_questions,
            question_retries={qid: 0 for qid in all_questions},
            turn_history=[
                ConversationTurn(
                    turn_id=1,
                    speaker="AI",
                    text=greeting_text,
                    state_before=ConversationState.INITIALIZING,
                    state_after=ConversationState.AWAITING_INPUT,
                    metadata={"phase": CallPhase.GREETING_CONSENT.value}
                )
            ]
        )

        fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Waiting for candidate consent")
        self._sessions[session_id] = session
        return session, action

    def get_session(self, session_id: str) -> Optional[CallSessionState]:
        """Retrieve active session state by session ID."""
        return self._sessions.get(session_id)

    # -------------------------------------------------------------------------
    # Decision Tree Step Processing
    # -------------------------------------------------------------------------
    def process_turn(
        self,
        session_id: str,
        candidate_utterance: Optional[str] = None,
        silence_ms: int = 0
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """
        Advance one conversational turn through the decision tree based on candidate speech or silence.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        fsm = self._state_machines.get(session_id)
        if not fsm:
            raise KeyError(f"State machine for session '{session_id}' not found.")

        if not session.is_active or fsm.is_terminal:
            # Session already completed or terminated
            action = CallFlowAction(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.TERMINATE_CALL,
                text_to_speak="Thank you. The screening call has concluded.",
                next_state=session.current_state,
                current_phase=session.current_phase,
                should_listen=False
            )
            return session, action

        # ---------------------------------------------------------------------
        # Decision Branch A: Silence Handling
        # ---------------------------------------------------------------------
        if silence_ms >= self._error_manager.SILENCE_GENTLE_THRESHOLD_MS and (not candidate_utterance or not candidate_utterance.strip()):
            session.total_silence_count += 1
            consecutive = session.total_silence_count
            silence_event = self._error_manager.evaluate_silence(silence_ms, consecutive)

            fsm.transition_to(ConversationState.HANDLING_SILENCE, reason=f"Silence detected: {silence_ms}ms")

            if silence_event.is_timeout:
                # Max silence reached -> advance to next question
                session.consecutive_failures += 1
                fsm.transition_to(ConversationState.TRANSITIONING_NEXT, reason="Silence timeout advancing question")
                return self._advance_to_next_question(session, fsm, prefix=silence_event.nudge_prompt)
            else:
                # Gentle or assist nudge
                fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Nudge emitted, awaiting input")
                action = CallFlowAction(
                    action_id=f"act_{uuid.uuid4().hex[:8]}",
                    action_type=ActionType.NUDGE_SILENCE,
                    text_to_speak=silence_event.nudge_prompt,
                    next_state=ConversationState.AWAITING_INPUT,
                    current_phase=session.current_phase,
                    should_listen=True,
                    metadata={"silence_duration_ms": silence_ms, "nudge_level": silence_event.nudge_level.value}
                )
                self._record_turn(session, "AI", silence_event.nudge_prompt, DisruptionType.SILENCE_TIMEOUT)
                return session, action

        # Candidate spoke: reset silence counters
        utterance = (candidate_utterance or "").strip()
        turn_id = len(session.turn_history) + 1
        self._record_turn(session, "CANDIDATE", utterance, DisruptionType.NONE)
        session.consecutive_failures = 0

        # Advance to PROCESSING_INPUT
        fsm.transition_to(ConversationState.PROCESSING_INPUT, reason="Processing candidate speech")

        # ---------------------------------------------------------------------
        # Decision Branch B: Greeting / Consent Handling
        # ---------------------------------------------------------------------
        if session.current_phase == CallPhase.GREETING_CONSENT:
            affirmatives = ["yes", "yeah", "sure", "ready", "fine", "hello", "hi", "i can hear", "i am ready"]
            is_ready = any(word in utterance.lower() for word in affirmatives)

            if is_ready:
                session.current_phase = CallPhase.CORE_TECHNICAL
                fsm.transition_to(ConversationState.TRANSITIONING_NEXT, reason="Candidate confirmed ready")
                return self._ask_current_question(session, fsm, intro="Excellent! Let's dive into our technical discussion.")
            else:
                # Candidate indicated not ready
                defer_text = (
                    "No problem at all. Would you prefer to take a minute to prepare, or would you like "
                    "our talent team to reschedule for a more convenient time?"
                )
                fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Candidate hesitant in greeting")
                action = CallFlowAction(
                    action_id=f"act_{uuid.uuid4().hex[:8]}",
                    action_type=ActionType.SPEAK_PRIMARY,
                    text_to_speak=defer_text,
                    next_state=ConversationState.AWAITING_INPUT,
                    current_phase=CallPhase.GREETING_CONSENT,
                    should_listen=True
                )
                self._record_turn(session, "AI", defer_text, DisruptionType.NONE)
                return session, action

        # Current question ID
        current_qid = session.question_ids[session.current_question_index] if session.current_question_index < len(session.question_ids) else None

        # ---------------------------------------------------------------------
        # Decision Branch C: Confusion Detection & Dynamic Simplification
        # ---------------------------------------------------------------------
        confusion_event = self._error_manager.detect_confusion(utterance, question_id=current_qid)
        if confusion_event:
            session.total_confusion_count += 1
            session.question_retries[current_qid] = session.question_retries.get(current_qid, 0) + 1

            retry_action, retry_prompt = self._error_manager.evaluate_retry_policy(
                question_id=current_qid,
                current_retries=session.question_retries[current_qid],
                consecutive_failures=session.consecutive_failures
            )

            if retry_action == RetryPolicyAction.SKIP_QUESTION:
                fsm.transition_to(ConversationState.TRANSITIONING_NEXT, reason="Max retries exceeded on confusion")
                return self._advance_to_next_question(session, fsm, prefix=retry_prompt)

            fsm.transition_to(ConversationState.HANDLING_CONFUSION, reason="Candidate confusion detected")
            fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Clarification delivered")

            action = CallFlowAction(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.CLARIFY_CONFUSION,
                text_to_speak=confusion_event.suggested_clarification,
                next_state=ConversationState.AWAITING_INPUT,
                current_phase=session.current_phase,
                question_id=current_qid,
                should_listen=True,
                metadata={"confusion_cue": confusion_event.trigger_phrase}
            )
            self._record_turn(session, "AI", confusion_event.suggested_clarification, DisruptionType.CANDIDATE_CONFUSION)
            return session, action

        # ---------------------------------------------------------------------
        # Decision Branch D: Repeated Answer Detection & Pivot
        # ---------------------------------------------------------------------
        prev_candidate_turns = [t.text for t in session.turn_history if t.speaker == "CANDIDATE"][:-1]
        repetition_event = self._error_manager.detect_repetition(utterance, prev_candidate_turns)
        if repetition_event:
            session.total_repetition_count += 1
            fsm.transition_to(ConversationState.HANDLING_REPETITION, reason="Repeated answer detected")

            # Progressive probe to move beyond repetition
            probe_text = f"{repetition_event.pivot_prompt} In that context, what was the most complex technical hurdle you solved?"
            fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Pivoting beyond repetition")

            action = CallFlowAction(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.ACKNOWLEDGE_REPETITION,
                text_to_speak=probe_text,
                next_state=ConversationState.AWAITING_INPUT,
                current_phase=session.current_phase,
                question_id=current_qid,
                should_listen=True,
                metadata={"similarity": repetition_event.similarity_score}
            )
            self._record_turn(session, "AI", probe_text, DisruptionType.REPEATED_ANSWER)
            return session, action

        # ---------------------------------------------------------------------
        # Decision Branch E: Shallow Answer -> Dynamic Follow-up Trigger
        # ---------------------------------------------------------------------
        word_count = len(utterance.split())
        if word_count < 10 and session.question_retries.get(current_qid, 0) == 0:
            session.question_retries[current_qid] = 1
            fsm.transition_to(ConversationState.FOLLOW_UP_PROBING, reason="Shallow answer triggered probe")
            probe = "Could you walk me through a brief real-world example or practical project where you implemented that?"
            fsm.transition_to(ConversationState.AWAITING_INPUT, reason="Probe issued")

            action = CallFlowAction(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.SPEAK_PROBE,
                text_to_speak=probe,
                next_state=ConversationState.AWAITING_INPUT,
                current_phase=session.current_phase,
                question_id=current_qid,
                should_listen=True,
                metadata={"shallow_word_count": word_count}
            )
            self._record_turn(session, "AI", probe, DisruptionType.NONE)
            return session, action

        # ---------------------------------------------------------------------
        # Decision Branch F: Substantive Answer -> Advance to Next Question
        # ---------------------------------------------------------------------
        fsm.transition_to(ConversationState.TRANSITIONING_NEXT, reason="Answer accepted, advancing")
        return self._advance_to_next_question(session, fsm)

    # -------------------------------------------------------------------------
    # Navigation & Question Stepping
    # -------------------------------------------------------------------------
    def _ask_current_question(
        self,
        session: CallSessionState,
        fsm: ConversationStateMachine,
        intro: str = ""
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """Ask the question at the current index."""
        qid = session.question_ids[session.current_question_index]
        q_record = get_fallback_for_question(qid)
        q_text = q_record.primary_text if q_record else "Could you elaborate on your experience in this domain?"

        full_prompt = f"{intro} {q_text}".strip()
        fsm.transition_to(ConversationState.AWAITING_INPUT, reason=f"Asked question '{qid}'")

        action = CallFlowAction(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            action_type=ActionType.SPEAK_PRIMARY,
            text_to_speak=full_prompt,
            next_state=ConversationState.AWAITING_INPUT,
            current_phase=session.current_phase,
            question_id=qid,
            should_listen=True,
            metadata={"question_index": session.current_question_index}
        )
        self._record_turn(session, "AI", full_prompt, DisruptionType.NONE)
        return session, action

    def _advance_to_next_question(
        self,
        session: CallSessionState,
        fsm: ConversationStateMachine,
        prefix: str = ""
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """Increment question index and transition to next question or wrap-up."""
        session.current_question_index += 1

        # Check if we moved into operational questions
        if session.current_question_index >= len(self.DEFAULT_TECHNICAL_QUESTIONS):
            session.current_phase = CallPhase.OPERATIONAL_CONSTRAINTS

        # Check if all questions completed
        if session.current_question_index >= len(session.question_ids):
            return self._perform_wrapup(session, fsm, prefix=prefix)

        bridge = prefix or "Thanks for sharing that."
        return self._ask_current_question(session, fsm, intro=bridge)

    def _perform_wrapup(
        self,
        session: CallSessionState,
        fsm: ConversationStateMachine,
        prefix: str = ""
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """Perform courteous wrap-up and finalize conversation."""
        session.current_phase = CallPhase.CLOSING_WRAPUP
        fsm.transition_to(ConversationState.WRAPUP, reason="All screening phases completed")

        wrapup_text = (
            f"{prefix} That covers all our screening questions for today, {session.candidate_name}! "
            f"Our recruitment engineering team will review the detailed synthesis within two to three business days "
            f"to discuss next steps for the {session.role_name} position. Thank you for your time, and have a wonderful day!"
        ).strip()

        fsm.transition_to(ConversationState.COMPLETED, reason="Call completed successfully")
        session.is_active = False
        session.is_completed = True
        session.current_state = ConversationState.COMPLETED

        action = CallFlowAction(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            action_type=ActionType.WRAPUP_CALL,
            text_to_speak=wrapup_text,
            next_state=ConversationState.COMPLETED,
            current_phase=CallPhase.CLOSING_WRAPUP,
            should_listen=False,
            metadata={"status": "screening_complete"}
        )
        self._record_turn(session, "AI", wrapup_text, DisruptionType.NONE)
        return session, action

    # -------------------------------------------------------------------------
    # Explicit Disruption Event Handlers (for Testing & Telephony Webhooks)
    # -------------------------------------------------------------------------
    def handle_explicit_event(
        self,
        session_id: str,
        disruption_type: DisruptionType,
        payload: Optional[Dict[str, Any]] = None
    ) -> Tuple[CallSessionState, CallFlowAction]:
        """
        Manually trigger and test a specific conversational event (Silence, Confusion, Repetition, Disconnect).
        """
        payload = payload or {}
        if disruption_type == DisruptionType.SILENCE_TIMEOUT:
            silence_ms = payload.get("silence_ms", 12000)
            return self.process_turn(session_id, candidate_utterance="", silence_ms=silence_ms)
        elif disruption_type == DisruptionType.CANDIDATE_CONFUSION:
            text = payload.get("utterance", "I'm sorry, I don't understand that question.")
            return self.process_turn(session_id, candidate_utterance=text, silence_ms=0)
        elif disruption_type == DisruptionType.REPEATED_ANSWER:
            text = payload.get("utterance", "As I mentioned earlier, we used Redis and queues.")
            return self.process_turn(session_id, candidate_utterance=text, silence_ms=0)
        elif disruption_type == DisruptionType.TECHNICAL_GLITCH:
            session = self._sessions[session_id]
            fsm = self._state_machines[session_id]
            fsm.transition_to(ConversationState.CALL_TERMINATED, reason="Technical glitch disconnect")
            session.is_active = False
            session.termination_reason = "Connection glitch"
            action = CallFlowAction(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.TERMINATE_CALL,
                text_to_speak=DISCONNECT_WRAPUP,
                next_state=ConversationState.CALL_TERMINATED,
                current_phase=session.current_phase,
                should_listen=False
            )
            return session, action
        else:
            raise ValueError(f"Unsupported explicit event type: {disruption_type}")

    # -------------------------------------------------------------------------
    # Recruiter Summary
    # -------------------------------------------------------------------------
    def get_summary(self, session_id: str) -> CallSessionSummary:
        """Generate executive summary of conversation flow performance."""
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        disruptions = (
            session.total_silence_count +
            session.total_confusion_count +
            session.total_repetition_count
        )

        phases_reached = list({turn.metadata.get("phase") for turn in session.turn_history if turn.metadata.get("phase")})
        call_phases = [CallPhase(p) for p in phases_reached if p in CallPhase.__members__]

        return CallSessionSummary(
            session_id=session.session_id,
            candidate_name=session.candidate_name,
            role_name=session.role_name,
            total_turns=len(session.turn_history),
            completion_status="COMPLETED" if session.is_completed else ("TERMINATED" if not session.is_active else "IN_PROGRESS"),
            total_disruptions_handled=disruptions,
            silence_events_count=session.total_silence_count,
            confusion_events_count=session.total_confusion_count,
            repetition_events_count=session.total_repetition_count,
            phases_completed=call_phases,
            final_state=session.current_state,
            termination_reason=session.termination_reason
        )

    def _record_turn(
        self,
        session: CallSessionState,
        speaker: str,
        text: str,
        disruption: DisruptionType
    ):
        """Append an auditable dialogue turn."""
        session.turn_history.append(
            ConversationTurn(
                turn_id=len(session.turn_history) + 1,
                speaker=speaker,
                text=text,
                state_before=session.current_state,
                state_after=session.current_state,
                disruption_type=disruption,
                metadata={"phase": session.current_phase.value}
            )
        )
        session.updated_at = datetime.now(timezone.utc).isoformat()
