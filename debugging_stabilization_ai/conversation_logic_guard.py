"""
Day 57: Conversation Logic Guard - Fix Conversation Loops & Dialogue Stalls
===========================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Remediates:
  1. Cyclic repetition & interviewer loop stalls.
  2. Candidate silence & speech timeout handling with progressive re-prompts.
  3. Off-topic drift and prompt injection filtering.
  4. Finite dialogue state machine integrity.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import re


class DialogueState(str, Enum):
    INIT = "INIT"
    GREETING = "GREETING"
    SCREENING_QUESTIONS = "SCREENING_QUESTIONS"
    TECHNICAL_CHALLENGE = "TECHNICAL_CHALLENGE"
    BEHAVIORAL_PROBING = "BEHAVIORAL_PROBING"
    CANDIDATE_QNA = "CANDIDATE_QNA"
    WRAP_UP = "WRAP_UP"
    COMPLETED = "COMPLETED"


class ConversationLogicGuard:
    """
    Guards the interview dialogue engine against stalls, cyclic loops,
    silence deadlocks, and topic deviations.
    """

    MAX_REPETITION_THRESHOLD = 2
    MIN_MEANINGFUL_WORD_COUNT = 3

    def __init__(self):
        self.question_history: List[str] = []
        self.silence_count: int = 0
        self.current_state: DialogueState = DialogueState.INIT

    def sanitize_input(self, raw_utterance: Optional[str]) -> str:
        """Strips whitespace, control characters, and handles None."""
        if not raw_utterance:
            return ""
        # Remove non-printable control characters
        cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", raw_utterance.strip())
        return cleaned

    def check_for_loop_stall(self, next_prompt: str) -> Tuple[bool, str]:
        """
        Detects if the AI agent is about to repeat a previously asked question.
        Returns: (is_stalled, sanitized_or_diverted_prompt)
        """
        clean_prompt = self.sanitize_input(next_prompt)
        
        # Check against recent 3 questions
        recent_prompts = self.question_history[-3:]
        is_repeat = any(clean_prompt.lower() == p.lower() for p in recent_prompts)

        if is_repeat:
            # Divert to dynamic recovery progression
            recovery_prompt = (
                "Understood. Moving forward to our next technical topic: "
                "How do you approach end-to-end testing and observability in distributed production systems?"
            )
            self.question_history.append(recovery_prompt)
            return True, recovery_prompt

        self.question_history.append(clean_prompt)
        return False, clean_prompt

    def handle_candidate_response(
        self,
        candidate_utterance: Optional[str],
        current_question_context: str
    ) -> Dict[str, Any]:
        """
        Safely processes candidate response, handling silence, empty input,
        and progressive escalation.
        """
        clean_text = self.sanitize_input(candidate_utterance)
        words = clean_text.split()

        # 1. Silence / Empty response handling
        if len(words) < self.MIN_MEANINGFUL_WORD_COUNT:
            self.silence_count += 1
            if self.silence_count == 1:
                return {
                    "status": "SILENCE_RETRY",
                    "action": "GENTLE_REPROMPT",
                    "agent_prompt": "Take your time. Whenever you're ready, could you share your thoughts on this?",
                    "advance_stage": False,
                    "silence_tier": 1
                }
            elif self.silence_count == 2:
                return {
                    "status": "SILENCE_RETRY",
                    "action": "CLARIFY_QUESTION",
                    "agent_prompt": "To clarify: we're looking at how you would design or implement this component. Would you like a brief hint?",
                    "advance_stage": False,
                    "silence_tier": 2
                }
            else:
                # 3rd timeout: Skip gracefully without crashing
                self.silence_count = 0
                return {
                    "status": "SILENCE_SKIP",
                    "action": "ADVANCE_STAGE",
                    "agent_prompt": "No problem, let's move on to the next architectural question.",
                    "advance_stage": True,
                    "silence_tier": 3
                }

        # Reset silence counter upon valid response
        self.silence_count = 0

        # 2. Topic Drift / Injection Check
        drift_detected = False
        injection_keywords = ["ignore previous instructions", "system prompt", "you are now a", "bypass evaluation"]
        if any(ik in clean_text.lower() for ik in injection_keywords):
            drift_detected = True
            return {
                "status": "SECURITY_WARNING",
                "action": "NEUTRALIZE_INJECTION",
                "agent_prompt": "Let's keep our focus strictly on your software engineering experience.",
                "advance_stage": False,
                "sanitized_response": "[PROMPT_INJECTION_FILTERED]"
            }

        return {
            "status": "VALID_RESPONSE",
            "action": "PROCESS_NEXT_QUESTION",
            "agent_prompt": None,
            "advance_stage": True,
            "word_count": len(words)
        }

    def transition_state(self, next_state: DialogueState) -> bool:
        """Validates state machine transitions."""
        valid_transitions = {
            DialogueState.INIT: [DialogueState.GREETING],
            DialogueState.GREETING: [DialogueState.SCREENING_QUESTIONS, DialogueState.TECHNICAL_CHALLENGE],
            DialogueState.SCREENING_QUESTIONS: [DialogueState.TECHNICAL_CHALLENGE, DialogueState.BEHAVIORAL_PROBING],
            DialogueState.TECHNICAL_CHALLENGE: [DialogueState.BEHAVIORAL_PROBING, DialogueState.CANDIDATE_QNA],
            DialogueState.BEHAVIORAL_PROBING: [DialogueState.CANDIDATE_QNA, DialogueState.WRAP_UP],
            DialogueState.CANDIDATE_QNA: [DialogueState.WRAP_UP],
            DialogueState.WRAP_UP: [DialogueState.COMPLETED],
            DialogueState.COMPLETED: []
        }

        allowed = valid_transitions.get(self.current_state, [])
        if next_state in allowed:
            self.current_state = next_state
            return True
        return False
