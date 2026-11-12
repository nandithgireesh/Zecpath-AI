import re
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime

from screening_ai.scoring_models import (
    ScoringDimension,
    RecommendationTier,
    ScoreGrade,
    DimensionScore,
    QuestionScoreBreakdown,
    CategoryScoreSummary,
    ExplainableReport,
    FinalScreeningScoreObject,
)
from screening_ai.intent_models import (
    StructuredAnswerObject,
    CandidateIntent,
    ProficiencyLevel,
)
from screening_ai.answer_understanding import AnswerUnderstandingEngine
from screening_ai.stt_cleaner import CleanTranscriptProcessor


# Default Weights for Per-Question Dimension Scoring
DEFAULT_DIMENSION_WEIGHTS = {
    ScoringDimension.CLARITY: 0.25,
    ScoringDimension.RELEVANCE: 0.25,
    ScoringDimension.COMPLETENESS: 0.30,
    ScoringDimension.CONSISTENCY: 0.20,
}

# Default Category Weights for Overall Interview Session Aggregation
DEFAULT_CATEGORY_WEIGHTS = {
    "Technical Skills": 0.35,
    "Experience": 0.25,
    "Salary Expectation": 0.10,
    "Notice Period": 0.10,
    "General": 0.20,
}


class ScreeningScoringEngine:
    """
    Day 26 - Screening Scoring Engine
    Objectively evaluates candidate screening responses across:
    - Clarity: Linguistic articulation, directness, lack of ambiguity or vagueness.
    - Relevance: Alignment with asked question category, penalizing off-topic drift.
    - Completeness: Verification that all required information slots were provided.
    - Consistency: Cross-turn factual consistency across claimed skills, experience, and notice periods.
    Provides score normalization, category aggregation, recommendation tiers, and explainable recruiter insights.
    """

    def __init__(
        self,
        dimension_weights: Optional[Dict[ScoringDimension, float]] = None,
        category_weights: Optional[Dict[str, float]] = None,
    ):
        self.dimension_weights = dimension_weights or DEFAULT_DIMENSION_WEIGHTS
        self.category_weights = category_weights or DEFAULT_CATEGORY_WEIGHTS
        self.answer_engine = AnswerUnderstandingEngine()
        self.cleaner = CleanTranscriptProcessor()

    # =========================================================================
    # 1. PER-QUESTION SCORING LOGIC
    # =========================================================================

    def score_question_answer(
        self,
        raw_text: str,
        question_category: Optional[str] = None,
        question_text: Optional[str] = None,
        question_id: Optional[str] = None,
        structured_answer: Optional[StructuredAnswerObject] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> QuestionScoreBreakdown:
        """
        Evaluate a single candidate question answer across Clarity, Relevance,
        Completeness, and Consistency.
        """
        # Ensure we have a structured answer object
        if structured_answer is None:
            structured_answer = self.answer_engine.understand_answer(
                raw_text=raw_text,
                question_category=question_category,
                question_prompt=question_text,
                question_id=question_id,
            )

        cat = question_category or structured_answer.question_category or "General"
        cleaned_text = structured_answer.cleaned_text
        penalties: List[str] = []
        strengths: List[str] = []
        weaknesses: List[str] = []

        # -------------------------------------------------------------
        # A. Evaluate Clarity (0 - 100)
        # -------------------------------------------------------------
        clarity_score = 100.0
        clarity_penalties: List[str] = []

        if structured_answer.quality.is_vague:
            clarity_score -= 35.0
            clarity_penalties.append("Vague or non-committal answer detected (-35)")
            weaknesses.append("Answer was vague or non-specific")

        # Check verbal fillers from cleaner
        clean_res = self.cleaner.process_transcript(raw_text, category=cat)
        if len(clean_res.removed_fillers) >= 3:
            filler_penalty = min(15.0, len(clean_res.removed_fillers) * 3.0)
            clarity_score -= filler_penalty
            clarity_penalties.append(f"Excessive verbal fillers ({len(clean_res.removed_fillers)}) impacted fluency (-{filler_penalty:.0f})")

        # Interrupted speech check
        if getattr(clean_res.edge_case_analysis, "is_interrupted", False):
            clarity_score -= 15.0
            clarity_penalties.append("Conversational cutoff or trailing speech (-15)")

        if clarity_score >= 90.0:
            strengths.append("Articulate and direct communication")

        clarity_score = self._clamp_score(clarity_score)
        dim_clarity = DimensionScore(
            dimension=ScoringDimension.CLARITY,
            score=clarity_score,
            weight=self.dimension_weights.get(ScoringDimension.CLARITY, 0.25),
            weighted_score=round(clarity_score * self.dimension_weights.get(ScoringDimension.CLARITY, 0.25), 2),
            explanation="Evaluates clarity, directness, and absence of verbal fillers or vagueness.",
            penalties_applied=clarity_penalties,
        )

        # -------------------------------------------------------------
        # B. Evaluate Relevance (0 - 100)
        # -------------------------------------------------------------
        relevance_score = 100.0
        relevance_penalties: List[str] = []

        if structured_answer.quality.is_off_topic or structured_answer.primary_intent == CandidateIntent.OFF_TOPIC:
            relevance_score -= 75.0
            relevance_penalties.append("Severe off-topic digression detected (-75)")
            weaknesses.append("Response was off-topic and unrelated to the question asked")
        elif structured_answer.primary_intent == CandidateIntent.ASKING_CLARIFICATION:
            relevance_score = 80.0
            relevance_penalties.append("Candidate asked for clarification rather than answering directly (-20)")
        else:
            # Check intent alignment against category
            intent_mismatch = self._check_intent_category_mismatch(structured_answer.primary_intent, cat)
            if intent_mismatch:
                relevance_score -= 30.0
                relevance_penalties.append(f"Mismatched intent: {intent_mismatch} (-30)")
                weaknesses.append(f"Intent mismatched question category: {intent_mismatch}")
            else:
                strengths.append(f"Directly addressed {cat} topic")

        relevance_score = self._clamp_score(relevance_score)
        dim_relevance = DimensionScore(
            dimension=ScoringDimension.RELEVANCE,
            score=relevance_score,
            weight=self.dimension_weights.get(ScoringDimension.RELEVANCE, 0.25),
            weighted_score=round(relevance_score * self.dimension_weights.get(ScoringDimension.RELEVANCE, 0.25), 2),
            explanation="Evaluates alignment with the question prompt and penalizes off-topic digression.",
            penalties_applied=relevance_penalties,
        )

        # -------------------------------------------------------------
        # C. Evaluate Completeness (0 - 100)
        # -------------------------------------------------------------
        completeness_score = 100.0
        completeness_penalties: List[str] = []

        missing_slots = structured_answer.quality.missing_slots
        if missing_slots:
            slot_penalty = min(60.0, len(missing_slots) * 30.0)
            completeness_score -= slot_penalty
            completeness_penalties.append(f"Missing required data slots: {', '.join(missing_slots)} (-{slot_penalty:.0f})")
            weaknesses.append(f"Incomplete response: missing {', '.join(missing_slots)}")

        # Category-specific completeness checks
        if "Salary" in cat:
            if not structured_answer.salary or structured_answer.salary.expected_ctc_lpa is None:
                if "Missing required data slots" not in str(completeness_penalties):
                    completeness_score -= 40.0
                    completeness_penalties.append("Did not specify expected CTC number (-40)")
            else:
                strengths.append(f"Provided clear compensation target ({structured_answer.salary.expected_ctc_lpa} LPA)")

        elif "Notice" in cat or "Availability" in cat:
            if not structured_answer.availability or (
                structured_answer.availability.notice_period_days is None and not structured_answer.availability.is_immediate_joiner
            ):
                completeness_score -= 40.0
                completeness_penalties.append("Notice period days or immediate joining date not specified (-40)")
            else:
                if structured_answer.availability.is_immediate_joiner:
                    strengths.append("Available to join immediately")
                elif structured_answer.availability.notice_period_days is not None:
                    strengths.append(f"Specified clear notice period ({structured_answer.availability.notice_period_days} days)")

        elif "Technical" in cat or "Skill" in cat:
            confirmed_skills = [s for s in structured_answer.extracted_skills if s.is_confirmed]
            declined_skills = [s for s in structured_answer.extracted_skills if not s.is_confirmed]
            if not confirmed_skills and not declined_skills:
                completeness_score -= 35.0
                completeness_penalties.append("No technical tools or frameworks identified in answer (-35)")
            else:
                if confirmed_skills:
                    skill_names = [s.skill for s in confirmed_skills]
                    strengths.append(f"Confirmed technical skills: {', '.join(skill_names[:3])}")
                if declined_skills:
                    decl_names = [s.skill for s in declined_skills]
                    weaknesses.append(f"Declined familiarity with: {', '.join(decl_names)}")

        elif "Experience" in cat:
            if not structured_answer.experience or structured_answer.experience.total_years is None:
                completeness_score -= 35.0
                completeness_penalties.append("Total years of experience was not quantified (-35)")
            else:
                strengths.append(f"Quantified career tenure: {structured_answer.experience.total_years} years")

        completeness_score = self._clamp_score(completeness_score)
        dim_completeness = DimensionScore(
            dimension=ScoringDimension.COMPLETENESS,
            score=completeness_score,
            weight=self.dimension_weights.get(ScoringDimension.COMPLETENESS, 0.30),
            weighted_score=round(completeness_score * self.dimension_weights.get(ScoringDimension.COMPLETENESS, 0.30), 2),
            explanation="Evaluates presence of required information entities and numerical parameters.",
            penalties_applied=completeness_penalties,
        )

        # -------------------------------------------------------------
        # D. Evaluate Consistency (0 - 100)
        # -------------------------------------------------------------
        consistency_score = 100.0
        consistency_penalties: List[str] = []

        # Internal turn contradiction check (e.g. expert but never worked)
        text_lower = raw_text.lower()
        if ("expert" in text_lower or "proficient" in text_lower) and ("never" in text_lower or "haven't" in text_lower):
            # Check if applied to the same skill
            for s in structured_answer.extracted_skills:
                if s.proficiency == ProficiencyLevel.ADVANCED and not s.is_confirmed:
                    consistency_score -= 40.0
                    consistency_penalties.append(f"Contradiction: Skill '{s.skill}' claimed as advanced but declined (-40)")
                    weaknesses.append(f"Self-contradiction on skill {s.skill}")

        # Check session context for cross-turn contradictions if provided
        if session_context:
            cross_penalties, cross_weaknesses = self._audit_single_turn_against_session(structured_answer, session_context)
            if cross_penalties:
                consistency_score -= len(cross_penalties) * 25.0
                consistency_penalties.extend(cross_penalties)
                weaknesses.extend(cross_weaknesses)

        if consistency_score >= 95.0:
            strengths.append("Internally consistent answer")

        consistency_score = self._clamp_score(consistency_score)
        dim_consistency = DimensionScore(
            dimension=ScoringDimension.CONSISTENCY,
            score=consistency_score,
            weight=self.dimension_weights.get(ScoringDimension.CONSISTENCY, 0.20),
            weighted_score=round(consistency_score * self.dimension_weights.get(ScoringDimension.CONSISTENCY, 0.20), 2),
            explanation="Evaluates internal logical coherence and absence of self-contradictions.",
            penalties_applied=consistency_penalties,
        )

        # -------------------------------------------------------------
        # Aggregate Weighted Question Score
        # -------------------------------------------------------------
        weighted_score = (
            dim_clarity.weighted_score
            + dim_relevance.weighted_score
            + dim_completeness.weighted_score
            + dim_consistency.weighted_score
        )
        weighted_score = self._clamp_score(round(weighted_score, 2))
        grade = self._derive_score_grade(weighted_score)

        all_penalties = clarity_penalties + relevance_penalties + completeness_penalties + consistency_penalties
        explanation = self._synthesize_question_explanation(
            cat, weighted_score, grade, strengths, weaknesses, all_penalties
        )

        return QuestionScoreBreakdown(
            question_id=question_id,
            question_text=question_text,
            question_category=cat,
            raw_answer=raw_text,
            cleaned_answer=cleaned_text,
            clarity_score=clarity_score,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            weighted_question_score=weighted_score,
            grade=grade,
            strengths=strengths,
            weaknesses=weaknesses,
            penalties=all_penalties,
            explanation=explanation,
            dimension_scores={
                ScoringDimension.CLARITY.value: dim_clarity,
                ScoringDimension.RELEVANCE.value: dim_relevance,
                ScoringDimension.COMPLETENESS.value: dim_completeness,
                ScoringDimension.CONSISTENCY.value: dim_consistency,
            },
        )

    # =========================================================================
    # 2. CROSS-TURN CONSISTENCY AUDITOR
    # =========================================================================

    def audit_session_consistency(
        self,
        structured_answers: List[StructuredAnswerObject],
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Audit factual consistency across an entire multi-turn screening conversation:
        - Confirmed vs. declined skills across turns.
        - Experience tenure timeline drift.
        - Notice period and joining availability contradictions.
        """
        contradictions: List[str] = []
        confirmed_skills_map: Dict[str, int] = {}  # skill -> turn_idx
        declined_skills_map: Dict[str, int] = {}   # skill -> turn_idx
        experience_claims: List[Tuple[float, int]] = [] # (years, turn_idx)
        notice_claims: List[Tuple[Optional[int], bool, int]] = [] # (notice_days, is_immediate, turn_idx)

        for idx, ans in enumerate(structured_answers):
            turn_num = idx + 1
            # 1. Track skills
            for s in ans.extracted_skills:
                skill_name = s.skill.lower()
                if s.is_confirmed:
                    confirmed_skills_map[skill_name] = turn_num
                else:
                    declined_skills_map[skill_name] = turn_num

            # 2. Track experience
            if ans.experience and ans.experience.total_years is not None:
                experience_claims.append((ans.experience.total_years, turn_num))

            # 3. Track availability
            if ans.availability:
                notice_claims.append((
                    ans.availability.notice_period_days,
                    ans.availability.is_immediate_joiner,
                    turn_num
                ))

        # Check Skill Contradictions (Confirmed in Turn A, Declined in Turn B)
        for skill, turn_conf in confirmed_skills_map.items():
            if skill in declined_skills_map:
                turn_decl = declined_skills_map[skill]
                contradictions.append(
                    f"Skill Contradiction: '{skill}' was confirmed in Turn {turn_conf} but declined in Turn {turn_decl}."
                )

        # Check Experience Drift (> 1.5 years discrepancy across turns)
        if len(experience_claims) >= 2:
            years_list = [y for y, _ in experience_claims]
            min_y, max_y = min(years_list), max(years_list)
            if (max_y - min_y) > 1.5:
                t1 = [t for y, t in experience_claims if y == min_y][0]
                t2 = [t for y, t in experience_claims if y == max_y][0]
                contradictions.append(
                    f"Experience Tenure Inconsistency: Candidate stated {min_y} years in Turn {t1}, but claimed {max_y} years in Turn {t2}."
                )

        # Check Notice Period Contradictions (Immediate vs Long Notice)
        if len(notice_claims) >= 2:
            has_immediate = any(imm for _, imm, _ in notice_claims)
            has_long_notice = any(nd is not None and nd > 30 for nd, _, _ in notice_claims)
            if has_immediate and has_long_notice:
                contradictions.append(
                    "Availability Contradiction: Candidate claimed immediate joining in one turn, but later stated a notice period > 30 days."
                )

        # Calculate session consistency score
        base_score = 100.0
        penalty = len(contradictions) * 25.0
        final_consistency = self._clamp_score(base_score - penalty)

        audit_details = {
            "total_turns_analyzed": len(structured_answers),
            "total_contradictions_found": len(contradictions),
            "contradictions": contradictions,
            "consistency_score": final_consistency,
            "is_flawless": len(contradictions) == 0,
        }

        return final_consistency, contradictions, audit_details

    # =========================================================================
    # 3. TOTAL SCREENING SCORE AGGREGATION & REPORTING
    # =========================================================================

    def aggregate_screening_session(
        self,
        questions_breakdowns: List[QuestionScoreBreakdown],
        structured_answers: Optional[List[StructuredAnswerObject]] = None,
        candidate_id: Optional[str] = None,
        call_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> FinalScreeningScoreObject:
        """
        Aggregate per-question scores into a unified composite screening score,
        compute dimension averages, category contributions, recommendation tier,
        and generate explainable insights.
        """
        if not questions_breakdowns:
            raise ValueError("Cannot aggregate an empty screening session.")

        # 1. Audit cross-turn session consistency
        if structured_answers and len(structured_answers) >= 2:
            sess_consistency, contradictions, audit_details = self.audit_session_consistency(structured_answers)
        else:
            sess_consistency = sum(q.consistency_score for q in questions_breakdowns) / len(questions_breakdowns)
            contradictions = []
            audit_details = {"total_contradictions_found": 0, "contradictions": []}

        # 2. Group by category and compute category averages
        category_groups: Dict[str, List[QuestionScoreBreakdown]] = {}
        for q in questions_breakdowns:
            cat = q.question_category or "General"
            category_groups.setdefault(cat, []).append(q)

        # Normalize category weights across present categories
        present_categories = list(category_groups.keys())
        raw_weights = {cat: self.category_weights.get(cat, 0.20) for cat in present_categories}
        total_weight = sum(raw_weights.values()) or 1.0
        normalized_weights = {cat: round(w / total_weight, 4) for cat, w in raw_weights.items()}

        category_summaries: Dict[str, CategoryScoreSummary] = {}
        weighted_category_total = 0.0

        for cat, q_list in category_groups.items():
            avg_cat_score = sum(q.weighted_question_score for q in q_list) / len(q_list)
            cat_weight = normalized_weights[cat]
            weighted_contrib = avg_cat_score * cat_weight
            weighted_category_total += weighted_contrib

            category_summaries[cat] = CategoryScoreSummary(
                category=cat,
                average_score=round(avg_cat_score, 2),
                weight=cat_weight,
                weighted_contribution=round(weighted_contrib, 2),
                question_count=len(q_list),
            )

        # 3. Overall composite score (clamped between 0 and 100)
        overall_score = self._clamp_score(round(weighted_category_total, 2))
        normalized_score = round(overall_score / 100.0, 4)
        overall_grade = self._derive_score_grade(overall_score)
        recommendation_tier = self._derive_recommendation_tier(overall_score, sess_consistency, contradictions)

        # 4. Dimension averages
        dim_averages = {
            ScoringDimension.CLARITY.value: round(sum(q.clarity_score for q in questions_breakdowns) / len(questions_breakdowns), 2),
            ScoringDimension.RELEVANCE.value: round(sum(q.relevance_score for q in questions_breakdowns) / len(questions_breakdowns), 2),
            ScoringDimension.COMPLETENESS.value: round(sum(q.completeness_score for q in questions_breakdowns) / len(questions_breakdowns), 2),
            ScoringDimension.CONSISTENCY.value: round(sess_consistency, 2),
        }

        # 5. Generate Explainable Recruiter Report
        explainability = self._generate_explainable_report(
            overall_score=overall_score,
            overall_grade=overall_grade,
            recommendation_tier=recommendation_tier,
            questions_breakdowns=questions_breakdowns,
            contradictions=contradictions,
            audit_details=audit_details,
            category_summaries=category_summaries,
        )

        return FinalScreeningScoreObject(
            candidate_id=candidate_id,
            call_id=call_id,
            job_id=job_id,
            overall_score=overall_score,
            normalized_score=normalized_score,
            recommendation_tier=recommendation_tier,
            grade=overall_grade,
            dimension_averages=dim_averages,
            category_breakdowns=category_summaries,
            per_question_breakdowns=questions_breakdowns,
            explainability=explainability,
            evaluated_at=datetime.now().isoformat(),
        )

    # =========================================================================
    # 4. HELPER UTILITIES
    # =========================================================================

    def _clamp_score(self, score: float) -> float:
        """Clamp score within [0.0, 100.0]."""
        return max(0.0, min(100.0, round(score, 2)))

    def _derive_score_grade(self, score: float) -> ScoreGrade:
        """Derive standard letter grade from numeric score."""
        if score >= 85.0:
            return ScoreGrade.EXCELLENT
        elif score >= 70.0:
            return ScoreGrade.STRONG
        elif score >= 55.0:
            return ScoreGrade.MODERATE
        elif score >= 40.0:
            return ScoreGrade.POOR
        else:
            return ScoreGrade.UNSATISFACTORY

    def _derive_recommendation_tier(
        self,
        overall_score: float,
        consistency_score: float,
        contradictions: List[str],
    ) -> RecommendationTier:
        """Determine recommendation tier based on score thresholds and red flags."""
        if overall_score >= 82.0 and consistency_score >= 80.0 and not contradictions:
            return RecommendationTier.STRONGLY_RECOMMENDED
        elif overall_score >= 68.0 and consistency_score >= 65.0:
            return RecommendationTier.RECOMMENDED
        elif overall_score >= 50.0:
            return RecommendationTier.RECOMMENDED_WITH_RESERVATIONS
        else:
            return RecommendationTier.NOT_RECOMMENDED

    def _check_intent_category_mismatch(self, intent: CandidateIntent, category: str) -> Optional[str]:
        """Verify if intent aligns with expected question category."""
        cat_lower = category.lower()
        if "salary" in cat_lower and intent in [CandidateIntent.PROVIDING_EXPERIENCE, CandidateIntent.OFF_TOPIC]:
            return f"Answered with {intent.value} on salary question"
        if "skill" in cat_lower and intent in [CandidateIntent.STATING_SALARY, CandidateIntent.STATING_AVAILABILITY]:
            return f"Answered with {intent.value} on technical skill question"
        if "notice" in cat_lower and intent in [CandidateIntent.CONFIRMING_SKILL, CandidateIntent.DECLINING_SKILL]:
            return f"Answered with {intent.value} on notice period question"
        return None

    def _audit_single_turn_against_session(
        self,
        structured_answer: StructuredAnswerObject,
        session_context: Dict[str, Any],
    ) -> Tuple[List[str], List[str]]:
        """Audit single turn against existing session context history."""
        penalties: List[str] = []
        weaknesses: List[str] = []
        prior_skills = session_context.get("confirmed_skills", set())
        for s in structured_answer.extracted_skills:
            if not s.is_confirmed and s.skill.lower() in prior_skills:
                penalties.append(f"Contradiction: Skill '{s.skill}' was previously confirmed (-25)")
                weaknesses.append(f"Inconsistent claim on {s.skill}")
        return penalties, weaknesses

    def _synthesize_question_explanation(
        self,
        category: str,
        score: float,
        grade: ScoreGrade,
        strengths: List[str],
        weaknesses: List[str],
        penalties: List[str],
    ) -> str:
        """Synthesize a human-readable explanation for a single question evaluation."""
        parts = [f"Awarded {score:.1f}/100 ({grade.value}) for {category}."]
        if strengths:
            parts.append(f"Strengths: {'; '.join(strengths[:2])}.")
        if weaknesses:
            parts.append(f"Areas of improvement: {'; '.join(weaknesses[:2])}.")
        if penalties:
            parts.append(f"Penalties applied: {'; '.join(penalties[:2])}.")
        return " ".join(parts)

    def _generate_explainable_report(
        self,
        overall_score: float,
        overall_grade: ScoreGrade,
        recommendation_tier: RecommendationTier,
        questions_breakdowns: List[QuestionScoreBreakdown],
        contradictions: List[str],
        audit_details: Dict[str, Any],
        category_summaries: Dict[str, CategoryScoreSummary],
    ) -> ExplainableReport:
        """Compile recruiter-grade explainability narrative, key strengths, risk factors, and interview probes."""
        # 1. Collect all strengths and weaknesses
        all_strengths: List[str] = []
        all_risks: List[str] = []

        for q in questions_breakdowns:
            for s in q.strengths:
                if s not in all_strengths:
                    all_strengths.append(s)
            for w in q.weaknesses:
                if w not in all_risks:
                    all_risks.append(f"[{q.question_category}] {w}")

        # Add contradictions to risk factors
        for c in contradictions:
            all_risks.append(f"[Consistency] {c}")

        # 2. Executive summary narrative
        tier_phrasing = {
            RecommendationTier.STRONGLY_RECOMMENDED: "demonstrates strong candidate qualification with high articulation and complete answers",
            RecommendationTier.RECOMMENDED: "meets core screening benchmarks and is suitable for next-stage technical evaluation",
            RecommendationTier.RECOMMENDED_WITH_RESERVATIONS: "presents viable attributes but requires probing due to identified gaps or vagueness",
            RecommendationTier.NOT_RECOMMENDED: "did not meet minimal screening criteria due to significant deficiencies, off-topic deflection, or contradictions",
        }
        summary_text = (
            f"Candidate achieved an overall screening score of {overall_score:.1f}/100 ({overall_grade.value}) "
            f"and is categorized as {recommendation_tier.value}. The candidate {tier_phrasing[recommendation_tier]}."
        )

        # 3. Targeted Next-Round Technical & Behavioral Probes
        interview_probes: List[str] = []
        if contradictions:
            interview_probes.append("Probe discrepancy between claimed skill background and later stated tenure.")
        for risk in all_risks[:3]:
            if "Salary" in risk or "expected_ctc_lpa" in risk:
                interview_probes.append("Clarify explicit compensation expectations (fixed vs. variable CTC expectations).")
            elif "Notice" in risk:
                interview_probes.append("Verify exact official notice period duration and buyout feasibility.")
            elif "Declined" in risk:
                interview_probes.append(f"Verify willingness and learning agility regarding declined technologies: {risk}.")
            elif "vague" in risk.lower():
                interview_probes.append("Ask for specific architectural and project implementation examples.")

        if not interview_probes:
            interview_probes.append("Proceed to standard in-depth architectural and coding assessment.")

        return ExplainableReport(
            executive_summary=summary_text,
            key_strengths=all_strengths[:5],
            risk_factors=all_risks[:5],
            consistency_audit=audit_details,
            recommended_interview_probes=interview_probes[:4],
        )
