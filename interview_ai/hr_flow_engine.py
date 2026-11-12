"""
Day 33: HR Interview Flow Engine & State Controller
====================================================
Orchestrates the 4 conversation phases:
  Phase 1: INTRODUCTION (Greeting, rapport, self-introduction)
  Phase 2: CORE_HR (Strengths/weaknesses, teamwork, culture fit)
  Phase 3: ROLE_BASED_EVALUATION (Career journey & role scenarios)
  Phase 4: CLOSING (Career goals, availability, candidate Q&A)

Maintains real-time state with Question ID tracking, response capture,
and adaptive follow-up probing triggers.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List

from interview_ai.hr_models import (
    HRCategory,
    InterviewPhase,
    HRInterviewConfig,
    HRInterviewSession,
    InterviewTurnState,
    FollowUpTriggerReason,
    FollowUpProbeCategory,
    AdaptationTier,
    HRQuestionTemplate,
)
from interview_ai.hr_question_generator import HRQuestionGenerator
from interview_ai.dynamic_followup_engine import DynamicFollowUpEngine
from interview_ai.communication_evaluator import CommunicationEvaluator
from interview_ai.confidence_analyzer import ConfidenceAnalyzer
from interview_ai.hr_scoring_engine import HRInterviewScoringEngine
from interview_ai.hr_scoring_models import CandidateHRScoreReport
from interview_ai.weight_config import WeightConfigurationSystem


class HRInterviewFlowEngine:
    """
    State machine controller and conversation orchestrator for AI HR interviews.
    Enforces deterministic phase progression while supporting adaptive follow-up probing.
    """

    def __init__(
        self,
        generator: Optional[HRQuestionGenerator] = None,
        followup_engine: Optional[DynamicFollowUpEngine] = None,
        comm_evaluator: Optional[CommunicationEvaluator] = None,
        confidence_analyzer: Optional[ConfidenceAnalyzer] = None,
        scoring_engine: Optional[HRInterviewScoringEngine] = None,
    ):
        self.generator = generator or HRQuestionGenerator()
        self.followup_engine = followup_engine or DynamicFollowUpEngine()
        self.comm_evaluator = comm_evaluator or CommunicationEvaluator()
        self.confidence_analyzer = confidence_analyzer or ConfidenceAnalyzer()
        self.scoring_engine = scoring_engine or HRInterviewScoringEngine()
        self._sessions: Dict[str, HRInterviewSession] = {}
        self._session_plans: Dict[str, List[HRQuestionTemplate]] = {}

    def start_session(self, config: HRInterviewConfig) -> HRInterviewSession:
        """
        Initializes an adaptive HR interview session, plans the question route,
        and provisions the initial opening greeting turn.
        """
        session_id = f"sess_hr_{uuid.uuid4().hex[:12]}"
        question_plan = self.generator.generate_interview_plan(config)

        if not question_plan:
            raise ValueError(f"Failed to generate question plan for config: {config.model_dump()}")

        self._session_plans[session_id] = question_plan

        first_q = question_plan[0]
        initial_turn = InterviewTurnState(
            turn_index=1,
            phase=first_q.phase,
            category=first_q.category,
            question_id=first_q.question_id,
            ai_prompt=first_q.prompt_text,
        )

        session = HRInterviewSession(
            session_id=session_id,
            config=config,
            current_phase=first_q.phase,
            current_question_index=0,
            turns=[initial_turn],
            is_completed=False,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        self._sessions[session_id] = session
        return session

    def process_turn(
        self,
        session_id: str,
        candidate_response: str,
        response_time_seconds: float = 1.5,
    ) -> InterviewTurnState:
        """
        Ingests the candidate's spoken response, captures state & telemetry,
        evaluates follow-up eligibility, and advances the conversational phase.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"HR Interview session '{session_id}' not found.")

        if session.is_completed:
            raise RuntimeError(f"Session '{session_id}' is already completed.")

        question_plan = self._session_plans[session_id]
        current_idx = session.current_question_index
        current_q = question_plan[current_idx]
        current_turn = session.turns[-1]

        # 1. Capture candidate response & telemetry
        words = candidate_response.strip().split()
        word_count = len(words)
        now_utc = datetime.now(timezone.utc).isoformat()

        current_turn.candidate_response = candidate_response
        current_turn.response_timestamp = now_utc
        current_turn.word_count = word_count
        current_turn.response_time_seconds = response_time_seconds

        # Extract basic behavioral themes
        themes = self._extract_themes(candidate_response, current_q.category)
        current_turn.extracted_themes = themes

        # 2. Evaluate follow-up eligibility using DynamicFollowUpEngine
        is_follow_up_turn = current_turn.follow_up_triggered
        current_depth = 1 if is_follow_up_turn else 0

        needs_follow_up, reason, probe_cat, adapt_tier, probe_prompt, diag = (
            self.followup_engine.evaluate_and_generate_followup(
                current_question=current_q,
                candidate_response=candidate_response,
                current_depth=current_depth,
                session_history=session.turns,
                job_role=session.config.job_role,
            )
        )

        current_turn.follow_up_eligible = needs_follow_up
        current_turn.follow_up_reason = reason
        current_turn.ambiguity_score = diag.get("vagueness_score", 0.0)
        current_turn.confidence_score = diag.get("confidence_score", 0.0)
        current_turn.adaptation_tier = adapt_tier
        current_turn.probe_category = probe_cat

        # 3. Evaluate Communication Skills (Day 35 Objective Evaluation)
        comm_breakdown = self.comm_evaluator.evaluate(
            text=candidate_response,
            category=current_q.category,
            role_track=session.config.role_track,
        )
        current_turn.communication_score = comm_breakdown

        # Update session-wide communication metrics
        completed_comms = [t.communication_score for t in session.turns if t.communication_score is not None]
        if completed_comms:
            session.average_communication_score = round(sum(c.normalized_score for c in completed_comms) / len(completed_comms), 1)
            session.overall_fluency = round(sum(c.fluency_score for c in completed_comms) / len(completed_comms), 1)
            session.overall_grammar = round(sum(c.grammar_score for c in completed_comms) / len(completed_comms), 1)
            session.overall_vocabulary = round(sum(c.vocabulary_score for c in completed_comms) / len(completed_comms), 1)
            session.overall_clarity = round(sum(c.clarity_score for c in completed_comms) / len(completed_comms), 1)
            session.overall_structure = round(sum(c.structure_score for c in completed_comms) / len(completed_comms), 1)
            session.total_fillers_detected = sum(c.filler_count for c in completed_comms)

            avg_score = session.average_communication_score
            if avg_score >= 88.0:
                session.communication_tier = "Exceptional"
            elif avg_score >= 75.0:
                session.communication_tier = "Proficient"
            elif avg_score >= 60.0:
                session.communication_tier = "Developing"
            else:
                session.communication_tier = "Needs Coaching"

        # 4. Evaluate Confidence & Stress Indicators (Day 36 Objective Evaluation)
        conf_breakdown = self.confidence_analyzer.evaluate_turn(
            turn_index=len(session.turns),
            text=candidate_response,
            response_time_seconds=response_time_seconds,
            session_id=session.session_id,
        )
        current_turn.confidence_evaluation = conf_breakdown
        current_turn.confidence_score = round(conf_breakdown.confidence_score / 100.0, 2)

        # Update session-wide confidence & stress metrics
        completed_confidences = [t.confidence_evaluation for t in session.turns if t.confidence_evaluation is not None]
        if completed_confidences:
            session_conf_summary = self.confidence_analyzer.aggregate_session(completed_confidences)
            session.average_confidence_score = session_conf_summary.average_confidence_score
            session.overall_confidence_tier = session_conf_summary.overall_confidence_tier.value
            session.average_stress_index = session_conf_summary.average_stress_index
            session.overall_stress_level = session_conf_summary.overall_stress_level.value
            session.total_hesitations_detected = session_conf_summary.total_hesitations_detected
            session.total_contradictions_detected = session_conf_summary.total_contradictions_detected
            session.dominant_emotional_tone = session_conf_summary.dominant_emotional_tone.value

        # 3. Adaptive Probing Logic: If eligible and not already probed on this question
        if (
            needs_follow_up
            and not is_follow_up_turn
            and session.config.enable_adaptive_probing
        ):
            # Update session follow-up analytics
            if probe_cat == FollowUpProbeCategory.CLARIFICATION:
                session.total_clarifications += 1
            elif probe_cat == FollowUpProbeCategory.DEEPENING:
                session.total_deepenings += 1
            elif probe_cat == FollowUpProbeCategory.EXAMPLE_BASED:
                session.total_examples_requested += 1
            elif probe_cat == FollowUpProbeCategory.SCENARIO_CHALLENGE:
                session.total_scenarios_triggered += 1

            probe_log = {
                "turn": len(session.turns) + 1,
                "question_id": current_q.question_id,
                "category": probe_cat.value,
                "tier": adapt_tier.value,
                "reason": reason.value,
                "prompt": probe_prompt or current_q.follow_up_prompt,
            }
            session.probes_dispatched_history.append(probe_log)

            # Dispatch follow-up question for deeper context
            follow_up_turn = InterviewTurnState(
                turn_index=len(session.turns) + 1,
                phase=current_q.phase,
                category=current_q.category,
                question_id=f"{current_q.question_id}-PROBE",
                ai_prompt=probe_prompt or current_q.follow_up_prompt,
                follow_up_triggered=True,
                follow_up_reason=reason,
                follow_up_depth=1,
                adaptation_tier=adapt_tier,
                probe_category=probe_cat,
            )
            session.turns.append(follow_up_turn)
            return follow_up_turn

        # 4. Advance to Next Question / Next Phase
        current_turn.phase_completed = True
        next_idx = current_idx + 1

        if next_idx >= len(question_plan):
            # All planned questions completed -> Transition to terminal state
            session.is_completed = True
            session.completed_at = now_utc
            session.current_phase = InterviewPhase.CLOSING

            closing_turn = InterviewTurnState(
                turn_index=len(session.turns) + 1,
                phase=InterviewPhase.CLOSING,
                category=HRCategory.AVAILABILITY_AND_COMMITMENT,
                question_id="HR-WRAPUP-FINAL",
                ai_prompt="Thank you very much for sharing your journey and insights with us today. That concludes our HR interview discussion. Our talent acquisition team will review your profile and contact you regarding the next steps within 48 hours. Have a great day!",
                phase_completed=True,
            )
            session.turns.append(closing_turn)
            return closing_turn

        # Advance question pointer
        session.current_question_index = next_idx
        next_q = question_plan[next_idx]
        session.current_phase = next_q.phase

        next_turn = InterviewTurnState(
            turn_index=len(session.turns) + 1,
            phase=next_q.phase,
            category=next_q.category,
            question_id=next_q.question_id,
            ai_prompt=next_q.prompt_text,
        )
        session.turns.append(next_turn)
        return next_turn

    def get_session(self, session_id: str) -> Optional[HRInterviewSession]:
        """Retrieves session state record by ID."""
        return self._sessions.get(session_id)

    def export_session_dossier(self, session_id: str) -> Dict[str, Any]:
        """Synthesizes structured HR interview dossier for ATS and recruiter review."""
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        total_words = sum(t.word_count for t in session.turns if t.candidate_response)
        follow_up_count = sum(1 for t in session.turns if t.follow_up_triggered)
        completed_turns = [t for t in session.turns if t.candidate_response]

        category_coverage = list({t.category.value for t in session.turns})
        all_themes = list({th for t in session.turns for th in t.extracted_themes})

        return {
            "session_id": session.session_id,
            "candidate_id": session.config.candidate_id,
            "candidate_name": session.config.candidate_name,
            "job_role": session.config.job_role,
            "experience_tier": session.config.experience_tier.value,
            "role_track": session.config.role_track.value,
            "interview_status": "COMPLETED" if session.is_completed else "IN_PROGRESS",
            "current_phase": session.current_phase.value,
            "total_turns_conducted": len(completed_turns),
            "follow_ups_triggered": follow_up_count,
            "total_clarifications": session.total_clarifications,
            "total_deepenings": session.total_deepenings,
            "total_examples_requested": session.total_examples_requested,
            "total_scenarios_triggered": session.total_scenarios_triggered,
            "probes_dispatched_history": session.probes_dispatched_history,
            "average_response_words": round(total_words / max(1, len(completed_turns)), 1),
            "categories_assessed": category_coverage,
            "identified_themes": all_themes,
            "communication_summary": {
                "average_score": session.average_communication_score,
                "proficiency_tier": session.communication_tier,
                "overall_fluency": session.overall_fluency,
                "overall_grammar": session.overall_grammar,
                "overall_vocabulary": session.overall_vocabulary,
                "overall_clarity": session.overall_clarity,
                "overall_structure": session.overall_structure,
                "total_fillers_detected": session.total_fillers_detected,
            },
            "behavioral_confidence_summary": {
                "average_score": session.average_confidence_score,
                "confidence_tier": session.overall_confidence_tier,
                "average_stress_index": session.average_stress_index,
                "overall_stress_level": session.overall_stress_level,
                "dominant_emotional_tone": session.dominant_emotional_tone,
                "total_hesitations_detected": session.total_hesitations_detected,
                "total_contradictions_detected": session.total_contradictions_detected,
            },
            "hr_score_report": self.scoring_engine.evaluate_session(session).model_dump(),
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "turn_details": [
                {
                    "turn_index": t.turn_index,
                    "phase": t.phase.value,
                    "category": t.category.value,
                    "question_id": t.question_id,
                    "prompt": t.ai_prompt,
                    "response": t.candidate_response,
                    "words": t.word_count,
                    "ambiguity_score": t.ambiguity_score,
                    "confidence_score": t.confidence_score,
                    "adaptation_tier": t.adaptation_tier.value,
                    "probe_category": t.probe_category.value,
                    "follow_up_eligible": t.follow_up_eligible,
                    "follow_up_reason": t.follow_up_reason.value,
                    "communication_score": t.communication_score.model_dump() if t.communication_score else None,
                    "confidence_evaluation": t.confidence_evaluation.model_dump() if t.confidence_evaluation else None,
                }
                for t in session.turns
            ],
        }

    def generate_candidate_score_report(
        self,
        session_id: str,
        custom_weights: Optional[Any] = None
    ) -> CandidateHRScoreReport:
        """Generates the standardized Day 37 Candidate HR Score Report for an interview session."""
        session = self.get_session(session_id)
        return self.scoring_engine.evaluate_session(session, custom_weight_profile=custom_weights)

    def _extract_themes(self, text: str, category: HRCategory) -> List[str]:
        """Lightweight behavioral keyword and theme extraction."""
        lower = text.lower()
        themes = []

        theme_patterns = {
            "Leadership": ["lead", "led", "mentored", "spearheaded", "directed", "managed"],
            "Collaboration": ["team", "pair", "cross-functional", "partnered", "together"],
            "Conflict Resolution": ["resolved", "compromise", "consensus", "aligned", "discussed"],
            "Problem Solving": ["debugged", "analyzed", "researched", "investigated", "fixed"],
            "Continuous Learning": ["learned", "course", "certif", "upskill", "explored"],
            "Ownership": ["owned", "ownership", "responsibility", "delivered", "accountable", "shipped", "architected", "built", "designed"],
            "Ambition": ["growth", "architect", "lead", "aspire", "future", "scale"],
        }

        for theme, keywords in theme_patterns.items():
            if any(k in lower for k in keywords):
                themes.append(theme)

        return themes
