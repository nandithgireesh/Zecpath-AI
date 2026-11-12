"""
Zecpath-AI: Technical Interview Flow Engine & Finite State Machine
==================================================================
Production stateful conversational flow engine orchestrating technical
interview stages, state transitions, dynamic probing, scaffolding, and
session evaluation.

Curriculum Reference: Day 46 - Technical Interview System Design
Deliverable 3: Interview Flow Design & State Transitions
"""

from typing import List, Dict, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field
import time
import uuid

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    InterviewFlowState,
    SubTurnAction,
    RecommendationVerdict,
    CandidateProfile,
    TechnicalInterviewConfig,
    TechnicalEvaluationRubric,
)
from tech_interview.question_hierarchy import (
    QuestionNode,
    DynamicDifficultyProgressionEngine,
    QuestionHierarchyRepository,
)


# ==============================================================================
# 1. STATE MACHINE TRANSITION SPECIFICATION & GUARDS
# ==============================================================================

# Explicit valid state transition matrix
LEGAL_STATE_TRANSITIONS: Dict[InterviewFlowState, Set[InterviewFlowState]] = {
    InterviewFlowState.INITIALIZED: {InterviewFlowState.INTRODUCTION, InterviewFlowState.ABORTED},
    InterviewFlowState.INTRODUCTION: {InterviewFlowState.EXPERIENCE_PROBING, InterviewFlowState.PAUSED, InterviewFlowState.ABORTED},
    InterviewFlowState.EXPERIENCE_PROBING: {InterviewFlowState.CONCEPTUAL_EVALUATION, InterviewFlowState.PAUSED, InterviewFlowState.ABORTED},
    InterviewFlowState.CONCEPTUAL_EVALUATION: {InterviewFlowState.SCENARIO_ANALYSIS, InterviewFlowState.PAUSED, InterviewFlowState.ABORTED},
    InterviewFlowState.SCENARIO_ANALYSIS: {InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE, InterviewFlowState.WRAP_UP, InterviewFlowState.PAUSED, InterviewFlowState.ABORTED},
    InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE: {InterviewFlowState.WRAP_UP, InterviewFlowState.PAUSED, InterviewFlowState.ABORTED},
    InterviewFlowState.WRAP_UP: {InterviewFlowState.COMPLETED, InterviewFlowState.ABORTED},
    InterviewFlowState.PAUSED: {
        InterviewFlowState.INTRODUCTION,
        InterviewFlowState.EXPERIENCE_PROBING,
        InterviewFlowState.CONCEPTUAL_EVALUATION,
        InterviewFlowState.SCENARIO_ANALYSIS,
        InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE,
        InterviewFlowState.WRAP_UP,
        InterviewFlowState.ABORTED,
    },
    InterviewFlowState.COMPLETED: set(),  # Terminal state
    InterviewFlowState.ABORTED: set(),    # Terminal state
}


# ==============================================================================
# 2. TURN DATA MODELS & SESSION STATE
# ==============================================================================

class InterviewTurnRecord(BaseModel):
    """Record of a single conversational turn in the interview."""
    turn_index: int
    flow_state: InterviewFlowState
    question: QuestionNode
    target_difficulty: float
    candidate_answer: str
    evaluation: TechnicalEvaluationRubric
    sub_turn_action: SubTurnAction
    probing_depth: int
    difficulty_after_turn: float
    adaptation_rationale: str
    timestamp: float = Field(default_factory=time.time)


class StateTransitionEvent(BaseModel):
    """Audit event for state machine transitions."""
    from_state: InterviewFlowState
    to_state: InterviewFlowState
    trigger_reason: str
    turn_index: int
    timestamp: float = Field(default_factory=time.time)


class TechnicalInterviewReport(BaseModel):
    """Final comprehensive evaluation dossier generated upon interview completion."""
    session_id: str
    candidate_id: str
    target_role: JobRole
    experience_tier: ExperienceTier
    total_turns: int
    final_technical_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: RecommendationVerdict
    demonstrated_blooms_level: BloomsTaxonomyLevel
    category_scores: Dict[str, float]
    skill_domain_scores: Dict[str, float]
    state_transitions_count: int
    total_probes_asked: int
    total_hints_provided: int
    key_strengths: List[str]
    identified_growth_areas: List[str]
    detailed_turns: List[InterviewTurnRecord]
    audit_trail: List[StateTransitionEvent]


# ==============================================================================
# 3. INTERVIEW FLOW STATE MACHINE ENGINE
# ==============================================================================

class TechnicalInterviewFlowEngine:
    """
    Finite State Machine (FSM) managing execution flow, dynamic difficulty
    adaptation, follow-up probing, and evaluation for technical interviews.
    """

    def __init__(
        self,
        candidate_profile: CandidateProfile,
        config: Optional[TechnicalInterviewConfig] = None,
        repository: Optional[QuestionHierarchyRepository] = None,
    ):
        self.profile = candidate_profile
        self.config = config or TechnicalInterviewConfig(
            session_id=f"SESS-TECH-{uuid.uuid4().hex[:8].upper()}",
            target_role=candidate_profile.target_role,
            experience_tier=candidate_profile.experience_tier or ExperienceTier.JUNIOR_0_2_YRS,
        )
        self.repo = repository or QuestionHierarchyRepository()

        # FSM State
        self.current_state = InterviewFlowState.INITIALIZED
        self.current_difficulty: float = DynamicDifficultyProgressionEngine.get_initial_difficulty(self.config.experience_tier)
        self.current_turn_index: int = 0
        self.current_probing_depth: int = 0
        self.current_question: Optional[QuestionNode] = None

        # Tracking collections
        self.used_question_ids: Set[str] = set()
        self.turn_records: List[InterviewTurnRecord] = []
        self.state_transitions: List[StateTransitionEvent] = []
        self.questions_answered_per_state: Dict[InterviewFlowState, int] = {s: 0 for s in InterviewFlowState}

    # --------------------------------------------------------------------------
    # FSM State Transitions & Validation
    # --------------------------------------------------------------------------

    def can_transition_to(self, target_state: InterviewFlowState) -> bool:
        """Validates whether transitioning to target_state is legally permitted."""
        allowed = LEGAL_STATE_TRANSITIONS.get(self.current_state, set())
        return target_state in allowed

    def transition_to(self, target_state: InterviewFlowState, reason: str = "") -> bool:
        """
        Executes a validated state transition and records an immutable audit log.
        Returns True on successful transition, False if forbidden.
        """
        if not self.can_transition_to(target_state):
            return False

        old_state = self.current_state
        self.current_state = target_state
        self.current_probing_depth = 0  # Reset probing depth upon phase shift

        event = StateTransitionEvent(
            from_state=old_state,
            to_state=target_state,
            trigger_reason=reason or f"Normal phase advancement from {old_state.value}",
            turn_index=self.current_turn_index,
        )
        self.state_transitions.append(event)
        return True

    def evaluate_state_advancement(self) -> Optional[InterviewFlowState]:
        """
        Evaluates whether the current state exit criteria are satisfied
        and returns the next logical state, or None if current state should continue.
        """
        answered_in_state = self.questions_answered_per_state[self.current_state]

        if self.current_state == InterviewFlowState.INITIALIZED:
            return InterviewFlowState.INTRODUCTION

        elif self.current_state == InterviewFlowState.INTRODUCTION:
            min_req = self.config.min_questions_per_phase.get(QuestionCategory.INTRODUCTION, 1)
            if answered_in_state >= min_req:
                return InterviewFlowState.EXPERIENCE_PROBING

        elif self.current_state == InterviewFlowState.EXPERIENCE_PROBING:
            min_req = self.config.min_questions_per_phase.get(QuestionCategory.EXPERIENCE_BASED, 2)
            if answered_in_state >= min_req:
                return InterviewFlowState.CONCEPTUAL_EVALUATION

        elif self.current_state == InterviewFlowState.CONCEPTUAL_EVALUATION:
            min_req = self.config.min_questions_per_phase.get(QuestionCategory.CONCEPTUAL, 2)
            if answered_in_state >= min_req:
                return InterviewFlowState.SCENARIO_ANALYSIS

        elif self.current_state == InterviewFlowState.SCENARIO_ANALYSIS:
            min_req = self.config.min_questions_per_phase.get(QuestionCategory.SCENARIO_BASED, 2)
            if answered_in_state >= min_req:
                # Senior tier always gets SYSTEM_DESIGN; Mid tier gets it if performing well (avg >= 0.70)
                if self.config.experience_tier == ExperienceTier.SENIOR_5_PLUS_YRS:
                    return InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE
                elif self.config.experience_tier == ExperienceTier.MID_3_5_YRS:
                    # Check recent performance
                    recent_scores = [t.evaluation.aggregate_score for t in self.turn_records[-2:]]
                    avg_recent = sum(recent_scores) / max(len(recent_scores), 1)
                    if avg_recent >= 0.70:
                        return InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE
                    else:
                        return InterviewFlowState.WRAP_UP
                else:
                    return InterviewFlowState.WRAP_UP

        elif self.current_state == InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE:
            min_req = self.config.min_questions_per_phase.get(QuestionCategory.SYSTEM_DESIGN, 1)
            if answered_in_state >= min_req:
                return InterviewFlowState.WRAP_UP

        elif self.current_state == InterviewFlowState.WRAP_UP:
            if answered_in_state >= 1:
                return InterviewFlowState.COMPLETED

        return None

    # --------------------------------------------------------------------------
    # Question Selection & Turn Initiation
    # --------------------------------------------------------------------------

    def get_current_question_category(self) -> QuestionCategory:
        """Maps active FSM state to corresponding question category."""
        mapping = {
            InterviewFlowState.INTRODUCTION: QuestionCategory.INTRODUCTION,
            InterviewFlowState.EXPERIENCE_PROBING: QuestionCategory.EXPERIENCE_BASED,
            InterviewFlowState.CONCEPTUAL_EVALUATION: QuestionCategory.CONCEPTUAL,
            InterviewFlowState.SCENARIO_ANALYSIS: QuestionCategory.SCENARIO_BASED,
            InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE: QuestionCategory.SYSTEM_DESIGN,
            InterviewFlowState.WRAP_UP: QuestionCategory.WRAP_UP,
        }
        return mapping.get(self.current_state, QuestionCategory.CONCEPTUAL)

    def prepare_next_question(self) -> Optional[QuestionNode]:
        """
        Prepares the next technical question according to state requirements,
        target difficulty, and candidate experience tier.
        """
        # If currently in an active follow-up probe or scaffolding sub-turn, retain current question
        if self.current_question is not None:
            return self.current_question

        # Check if state transition is due
        next_state = self.evaluate_state_advancement()
        if next_state:
            self.transition_to(next_state, reason=f"Phase criteria fulfilled for {self.current_state.value}")

        if self.current_state in (InterviewFlowState.COMPLETED, InterviewFlowState.ABORTED, InterviewFlowState.PAUSED):
            return None

        # Handle wrap-up phase
        if self.current_state == InterviewFlowState.WRAP_UP:
            self.current_question = QuestionNode(
                question_id="Q-SYSTEM-WRAPUP-01",
                target_role=self.config.target_role,
                skill_domain="Closing & Candidate Questions",
                sub_skill="Wrap-up Debrief",
                category=QuestionCategory.WRAP_UP,
                difficulty=DifficultyLevel.L1_BASIC,
                experience_tier=self.config.experience_tier,
                blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
                prompt_text="We have completed the technical problem scenarios. Do you have any questions for us regarding our engineering architecture, development practices, or technology stack?",
                key_evaluation_points=["Curiosity about engineering culture", "Relevant architectural questions"],
            )
            return self.current_question

        category = self.get_current_question_category()
        question = self.repo.select_best_question(
            role=self.config.target_role,
            category=category,
            target_difficulty=self.current_difficulty,
            experience_tier=self.config.experience_tier,
            used_question_ids=self.used_question_ids,
        )

        if question:
            self.used_question_ids.add(question.question_id)
            self.current_question = question
            self.current_probing_depth = 0

        return question

    # --------------------------------------------------------------------------
    # Answer Evaluation & Adaptive Response Processing
    # --------------------------------------------------------------------------

    def evaluate_candidate_answer(self, candidate_answer: str, question: QuestionNode) -> TechnicalEvaluationRubric:
        """
        Multi-dimensional rubric scoring of candidate's technical response.
        Evaluates conceptual correctness, implementation depth, architectural trade-offs,
        and technical communication clarity.
        """
        ans_lower = candidate_answer.lower()
        ans_tokens = set(w.strip(".,;:!?()[]\"'").lower() for w in candidate_answer.split())
        word_count = len(candidate_answer.split())

        # If answer is practically empty or expresses total confusion
        if word_count < 8 or any(p in ans_lower for p in ["don't know", "dont know", "no idea", "not sure", "cannot answer"]):
            coverage_ratio = 0.0
            correctness = 0.20
            depth = 0.15
            tradeoffs = 0.10
            clarity = 0.40
            detected_gaps = [f"Unaddressed: {pt}" for pt in question.key_evaluation_points]
            positive_signals = []
        else:
            # Check matching of key evaluation points
            matched_points = 0
            detected_gaps = []
            positive_signals = []
            stopwords = {"the", "and", "for", "with", "that", "this", "from", "have", "been", "using", "your", "what", "how", "when", "where", "into", "over", "than"}

            for pt in question.key_evaluation_points:
                pt_words = [w.strip(".,;:!?()[]\"'").lower() for w in pt.split()]
                meaningful = [w for w in pt_words if len(w) > 3 and w not in stopwords]
                matches = sum(1 for kw in meaningful if kw in ans_lower or any(kw in t for t in ans_tokens))
                if matches >= 1:
                    matched_points += 1
                    positive_signals.append(f"Demonstrated awareness of: {pt}")
                else:
                    detected_gaps.append(f"Omitted or incomplete coverage: {pt}")

            coverage_ratio = matched_points / max(len(question.key_evaluation_points), 1)

            # 1. Correctness (0.0 - 1.0)
            correctness = min(1.0, 0.40 + (coverage_ratio * 0.60))

            # 2. Depth (0.0 - 1.0)
            length_factor = min(1.0, word_count / 45.0)
            depth = min(1.0, 0.35 + (length_factor * 0.35) + (coverage_ratio * 0.30))

            # 3. Trade-offs (0.0 - 1.0)
            tradeoff_triggers = [
                "trade-off", "tradeoff", "latency", "memory", "overhead", "versus", "vs",
                "bottleneck", "scale", "consistency", "cost", "performance", "rollback",
                "index", "cache", "partition", "failover", "rebalance", "limits", "async"
            ]
            tradeoff_count = sum(1 for t in tradeoff_triggers if t in ans_lower)
            tradeoffs = min(1.0, 0.30 + (min(tradeoff_count, 3) * 0.20) + (coverage_ratio * 0.30))

            # 4. Clarity (0.0 - 1.0)
            clarity = 0.85 if word_count >= 15 else 0.60

            # Special boost for Introduction and Wrap-up where candidate articulates well
            if question.category in (QuestionCategory.INTRODUCTION, QuestionCategory.WRAP_UP) and word_count >= 20:
                coverage_ratio = max(coverage_ratio, 0.80)
                correctness = max(correctness, 0.85)
                depth = max(depth, 0.80)
                tradeoffs = max(tradeoffs, 0.70)
                clarity = max(clarity, 0.90)

        # Aggregate weighted score
        aggregate = (
            (correctness * 0.35) +
            (depth * 0.30) +
            (tradeoffs * 0.20) +
            (clarity * 0.15)
        )
        aggregate = round(min(1.0, max(0.0, aggregate)), 2)

        blooms = DynamicDifficultyProgressionEngine.map_score_to_blooms(aggregate, self.current_difficulty)

        return TechnicalEvaluationRubric(
            conceptual_correctness=round(correctness, 2),
            implementation_depth=round(depth, 2),
            architectural_tradeoffs=round(tradeoffs, 2),
            communication_clarity=round(clarity, 2),
            aggregate_score=aggregate,
            blooms_demonstrated=blooms,
            detected_gaps=detected_gaps,
            positive_signals=positive_signals,
        )

    def process_candidate_turn(self, candidate_answer: str) -> Tuple[SubTurnAction, str, TechnicalEvaluationRubric]:
        """
        Executes a complete interview turn:
        1. Grades candidate answer against active question rubric
        2. Adjusts dynamic difficulty level
        3. Determines sub-turn action (Probe, Scaffold Hint, or Advance Question)
        4. Logs turn record and updates state counts
        """
        if not self.current_question:
            raise RuntimeError("No active question to process. Call prepare_next_question() first.")

        self.current_turn_index += 1
        q = self.current_question

        # Evaluate response
        evaluation = self.evaluate_candidate_answer(candidate_answer, q)

        # Determine next difficulty via DDA
        new_diff, rationale = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=self.current_difficulty,
            last_score=evaluation.aggregate_score,
            tier=self.config.experience_tier,
        )

        # Sub-turn adaptive decision logic
        prompt_reply = ""
        action = SubTurnAction.ADVANCE_QUESTION

        # Case A: Candidate is struggling severely (score < 0.35) -> Provide hint if available
        if evaluation.aggregate_score < 0.35 and q.scaffolding_hints and self.config.enable_dynamic_scaffolding:
            action = SubTurnAction.PROVIDE_SCAFFOLDING_HINT
            hint_idx = min(self.current_probing_depth, len(q.scaffolding_hints) - 1)
            prompt_reply = f"[HINT / SCAFFOLDING]: {q.scaffolding_hints[hint_idx]}"
            self.current_probing_depth += 1

        # Case B: Candidate gave a partial response with detected gaps and depth limit not reached
        elif evaluation.aggregate_score < 0.70 and self.current_probing_depth < self.config.max_probing_depth and q.suggested_followups:
            action = SubTurnAction.PROBE_DEEPER
            followup_idx = min(self.current_probing_depth, len(q.suggested_followups) - 1)
            prompt_reply = f"[FOLLOW-UP PROBE]: {q.suggested_followups[followup_idx]}"
            self.current_probing_depth += 1

        # Case C: Answer is solid or max probing reached -> Advance to next question
        else:
            action = SubTurnAction.ADVANCE_QUESTION
            prompt_reply = f"[EVALUATED]: Score {evaluation.aggregate_score * 100:.1f}%. Moving to next technical topic."
            self.questions_answered_per_state[self.current_state] += 1
            self.current_difficulty = new_diff
            self.current_question = None

        # Record turn
        record = InterviewTurnRecord(
            turn_index=self.current_turn_index,
            flow_state=self.current_state,
            question=q,
            target_difficulty=self.current_difficulty,
            candidate_answer=candidate_answer,
            evaluation=evaluation,
            sub_turn_action=action,
            probing_depth=self.current_probing_depth,
            difficulty_after_turn=new_diff,
            adaptation_rationale=rationale,
        )
        self.turn_records.append(record)

        return action, prompt_reply, evaluation

    # --------------------------------------------------------------------------
    # Final Report Generation & Scoring
    # --------------------------------------------------------------------------

    def generate_final_report(self) -> TechnicalInterviewReport:
        """
        Synthesizes the complete technical interview report, computing composite
        scores, category averages, skill domain breakdowns, and hiring verdicts.
        """
        if not self.turn_records:
            raise ValueError("Cannot generate report: No interview turns have been recorded.")

        # Ensure state transitioned to COMPLETED
        if self.current_state != InterviewFlowState.COMPLETED:
            self.transition_to(InterviewFlowState.COMPLETED, reason="Interview concluded and report generated.")

        # Calculate category scores
        category_scores: Dict[str, List[float]] = {}
        domain_scores: Dict[str, List[float]] = {}
        all_scores: List[float] = []

        probes_count = 0
        hints_count = 0

        for t in self.turn_records:
            score = t.evaluation.aggregate_score * 100.0
            all_scores.append(score)

            cat_name = t.question.category.value
            category_scores.setdefault(cat_name, []).append(score)

            dom_name = t.question.skill_domain
            domain_scores.setdefault(dom_name, []).append(score)

            if t.sub_turn_action == SubTurnAction.PROBE_DEEPER:
                probes_count += 1
            elif t.sub_turn_action == SubTurnAction.PROVIDE_SCAFFOLDING_HINT:
                hints_count += 1

        avg_cat = {cat: round(sum(s) / len(s), 1) for cat, s in category_scores.items()}
        avg_dom = {dom: round(sum(s) / len(s), 1) for dom, s in domain_scores.items()}

        final_composite_score = round(sum(all_scores) / len(all_scores), 1)

        # Recommendation verdict
        if final_composite_score >= 80.0:
            verdict = RecommendationVerdict.STRONG_HIRE
        elif final_composite_score >= 65.0:
            verdict = RecommendationVerdict.LEAN_HIRE
        elif final_composite_score >= 50.0:
            verdict = RecommendationVerdict.BORDERLINE
        else:
            verdict = RecommendationVerdict.NO_HIRE

        # Highest demonstrated Bloom's level
        blooms_levels = [t.evaluation.blooms_demonstrated for t in self.turn_records]
        blooms_order = [
            BloomsTaxonomyLevel.REMEMBER,
            BloomsTaxonomyLevel.UNDERSTAND,
            BloomsTaxonomyLevel.APPLY,
            BloomsTaxonomyLevel.ANALYZE,
            BloomsTaxonomyLevel.EVALUATE,
            BloomsTaxonomyLevel.CREATE,
        ]
        highest_blooms = max(blooms_levels, key=lambda b: blooms_order.index(b))

        # Strengths and growth areas
        strengths = [
            f"Strong performance in {dom} ({score}% average)"
            for dom, score in avg_dom.items() if score >= 75.0
        ]
        growth_areas = [
            f"Needs development in {dom} ({score}% average)"
            for dom, score in avg_dom.items() if score < 60.0
        ]

        if not strengths:
            strengths.append("Foundational understanding across tested topics")
        if not growth_areas:
            growth_areas.append("Demonstrated consistent competency across all tested domains")

        return TechnicalInterviewReport(
            session_id=self.config.session_id,
            candidate_id=self.profile.candidate_id,
            target_role=self.config.target_role,
            experience_tier=self.config.experience_tier,
            total_turns=len(self.turn_records),
            final_technical_score=final_composite_score,
            recommendation=verdict,
            demonstrated_blooms_level=highest_blooms,
            category_scores=avg_cat,
            skill_domain_scores=avg_dom,
            state_transitions_count=len(self.state_transitions),
            total_probes_asked=probes_count,
            total_hints_provided=hints_count,
            key_strengths=strengths,
            identified_growth_areas=growth_areas,
            detailed_turns=self.turn_records,
            audit_trail=self.state_transitions,
        )
