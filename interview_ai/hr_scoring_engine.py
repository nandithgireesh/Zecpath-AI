"""
Day 37: HR Interview Scoring Engine (Deliverable 1)
===================================================
Combines HR responses, communication signals, confidence metrics, and narrative
consistency into an objective, explainable, and length-normalized composite score.

Four Core Parameters:
1. Answer Relevance (Semantic intent alignment, domain depth, substantive coverage)
2. Communication Score (Day 35 6-dimension evaluation)
3. Confidence Score (Day 36 behavioral composure & stress index)
4. Consistency (Cross-turn factual stability & within-turn narrative coherence)
"""

import math
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

from .hr_models import HRInterviewSession, InterviewTurnState, HRCategory
from .hr_scoring_models import (
    ScoringParameter,
    HiringRecommendation,
    WeightProfile,
    ParameterContribution,
    TurnRelevanceEvaluation,
    LengthNormalizationMetadata,
    CandidateHRScoreReport,
)
from .weight_config import WeightConfigurationSystem


class AnswerRelevanceAnalyzer:
    """Evaluates how directly and substantively a candidate's answer addresses the interview prompt."""

    # Intent keywords mapped by question category
    CATEGORY_INTENT_MAP = {
        HRCategory.SELF_INTRODUCTION.value: {
            "core": ["background", "experience", "journey", "role", "years", "career", "graduated", "started", "worked", "built"],
            "depth": ["specialize", "domain", "skills", "passion", "projects", "stack", "focus", "lead"]
        },
        HRCategory.CAREER_JOURNEY.value: {
            "core": ["architecture", "scale", "system", "database", "latency", "throughput", "concurrency", "cache", "service", "api", "pipeline", "sharding", "distributed"],
            "depth": ["bottleneck", "optimization", "trade-off", "benchmark", "qps", "milliseconds", "replica", "index", "failure", "resilient"]
        },
        HRCategory.STRENGTHS_AND_WEAKNESSES.value: {
            "core": ["strength", "weakness", "improve", "learning", "growth", "challenge", "skill", "adapt", "feedback"],
            "depth": ["critical thinking", "perseverance", "collaboration", "upskill", "initiative", "ownership"]
        },
        HRCategory.TEAMWORK_AND_CULTURE_FIT.value: {
            "core": ["situation", "task", "action", "result", "team", "conflict", "disagreement", "collaborated", "aligned", "discussed"],
            "depth": ["stakeholder", "compromise", "outcome", "feedback", "impact", "delivered", "learned", "growth", "mentored"]
        },
        HRCategory.CAREER_GOALS.value: {
            "core": ["goal", "future", "aspire", "architect", "lead", "learn", "grow", "milestone", "impact"],
            "depth": ["technical excellence", "leadership", "mentorship", "product vision", "innovation"]
        },
        HRCategory.AVAILABILITY_AND_COMMITMENT.value: {
            "core": ["notice", "availability", "join", "weeks", "relocate", "hybrid", "remote", "committed", "excited"],
            "depth": ["immediate", "handover", "transition", "relocation", "schedule", "work authorization"]
        },
        # Compatibility aliases for technical & behavioral tags
        "technical_depth": {
            "core": ["architecture", "scale", "system", "database", "latency", "throughput", "concurrency", "cache", "service", "api"],
            "depth": ["bottleneck", "optimization", "trade-off", "benchmark", "qps", "replica", "failure"]
        },
        "behavioral_star": {
            "core": ["situation", "task", "action", "result", "team", "conflict", "disagreement", "collaborated", "aligned"],
            "depth": ["stakeholder", "compromise", "outcome", "feedback", "impact", "mentored"]
        }
    }

    EVASION_PATTERNS = [
        re.compile(r"\b(i\s+don'?t\s+know|no\s+idea|cannot\s+recall|haven'?t\s+done\s+this|skip\s+this)\b", re.IGNORECASE),
        re.compile(r"\b(pass|not\s+sure\s+about\s+that|whatever|anything\s+is\s+fine)\b", re.IGNORECASE),
        re.compile(r"\b(none\s+of\s+your\s+business|why\s+are\s+you\s+asking)\b", re.IGNORECASE),
    ]

    def evaluate_turn_relevance(
        self,
        turn_index: int,
        prompt: str,
        response: Optional[str],
        category: str
    ) -> TurnRelevanceEvaluation:
        """Evaluates semantic relevance, intent match, and substantive depth of an answer."""
        text = (response or "").strip()
        word_count = len(text.split())

        if word_count < 5:
            return TurnRelevanceEvaluation(
                turn_index=turn_index,
                raw_relevance_score=15.0,
                intent_match_score=10.0,
                keyword_coverage_score=10.0,
                substantive_depth_score=15.0,
                detected_intent_themes=[],
                missing_aspects=["Answer is excessively short or monosyllabic"]
            )

        # Check for evasion
        is_evasive = any(p.search(text) for p in self.EVASION_PATTERNS)
        evasion_penalty = 40.0 if is_evasive else 0.0

        # Extract prompt tokens for direct lexical/semantic overlap
        prompt_words = set(re.findall(r"\b\w{4,}\b", prompt.lower()))
        # Filter common prompt stop words
        prompt_stops = {"could", "would", "about", "please", "describe", "explain", "share", "today", "using", "which"}
        prompt_keywords = prompt_words - prompt_stops

        response_words = set(re.findall(r"\b\w{4,}\b", text.lower()))
        overlap = prompt_keywords.intersection(response_words)
        prompt_stems = {w[:4] for w in prompt_keywords}
        response_stems = {w[:4] for w in response_words}
        stem_overlap = prompt_stems.intersection(response_stems)
        overlap_ratio = max(len(overlap) / max(1, len(prompt_keywords)), len(stem_overlap) / max(1, len(prompt_stems)))

        # Category Intent Match
        default_cat = self.CATEGORY_INTENT_MAP[HRCategory.CAREER_JOURNEY.value]
        cat_data = self.CATEGORY_INTENT_MAP.get(category, default_cat)
        core_cues = cat_data["core"]
        depth_cues = cat_data["depth"]

        matched_core = [cue for cue in core_cues if cue in text.lower()]
        matched_depth = [cue for cue in depth_cues if cue in text.lower()]
        detected_themes = list(set(matched_core + matched_depth))

        # Intent Match Score (0 - 100)
        # Combines prompt overlap + category thematic match + concrete resolution/action terms
        has_resolution = any(w in text.lower() for w in ["resolved", "fixed", "optimized", "reduced", "improved", "restored", "mitigated", "deployed", "scaled", "designed", "architected"])
        resolution_bonus = 10.0 if has_resolution else 0.0
        intent_match = min(100.0, 36.0 + (overlap_ratio * 40.0) + (len(matched_core) * 8.0) + resolution_bonus)

        # Keyword / Domain Coverage Score (0 - 100)
        keyword_coverage = min(100.0, 25.0 + (len(detected_themes) * 9.0) + (overlap_ratio * 30.0))

        # Substantive Depth Score (0 - 100)
        # Length-based curve (sweet spot: 45 - 180 words) + presence of metrics and specific technical details
        has_metrics = bool(re.search(r"\b\d+([%kKmMxX]|ms|seconds|minutes|users|qps|rps|hours)?\b", text))
        metric_bonus = 15.0 if has_metrics else 0.0

        if word_count < 20:
            length_factor = 40.0
        elif 20 <= word_count <= 40:
            length_factor = 65.0
        elif 41 <= word_count <= 220:
            length_factor = 85.0
        else:
            length_factor = 75.0  # slight penalty for excessive rambling

        substantive_depth = min(100.0, length_factor + metric_bonus + (len(matched_depth) * 6.0))

        # Composite Raw Relevance Score
        raw_relevance = (0.40 * intent_match) + (0.35 * keyword_coverage) + (0.25 * substantive_depth)
        raw_relevance = max(10.0, min(100.0, raw_relevance - evasion_penalty))

        missing = []
        if len(detected_themes) == 0:
            missing.append("Lacks category-specific technical or behavioral terminology")
        if not has_metrics and category in [HRCategory.CAREER_JOURNEY.value, "technical_depth", "problem_solving"]:
            missing.append("Lacks quantifiable metrics or concrete resolution outcomes")
        if is_evasive:
            missing.append("Candidate displayed evasive or non-committal response patterns")

        return TurnRelevanceEvaluation(
            turn_index=turn_index,
            raw_relevance_score=round(raw_relevance, 2),
            intent_match_score=round(intent_match, 2),
            keyword_coverage_score=round(keyword_coverage, 2),
            substantive_depth_score=round(substantive_depth, 2),
            detected_intent_themes=detected_themes[:6],
            missing_aspects=missing
        )


class LengthNormalizationEngine:
    """Normalizes score aggregation across varying interview lengths (e.g. 2, 3, 5, or 8+ turns)."""

    def __init__(self, prior_mean: float = 70.0, prior_weight_m: float = 2.0, standard_turns: int = 5):
        self.prior_mean = prior_mean
        self.prior_weight_m = prior_weight_m
        self.standard_turns = standard_turns

    def normalize_turn_scores(
        self,
        scores: List[float],
        is_completed: bool = True
    ) -> Tuple[float, LengthNormalizationMetadata]:
        """Applies Bayesian prior smoothing, recency weighting, and interview completeness normalization."""
        if not scores:
            meta = LengthNormalizationMetadata(
                total_turns_evaluated=0,
                expected_standard_turns=self.standard_turns,
                raw_average_score=0.0,
                normalized_score=0.0,
                prior_mean=self.prior_mean,
                prior_weight_m=self.prior_weight_m,
                recency_weighted_average=0.0,
                session_completeness_factor=0.5,
                normalization_adjustment=0.0
            )
            return 0.0, meta

        n = len(scores)
        raw_avg = sum(scores) / n

        # 1. Bayesian Smoothing: Damps small-sample volatility
        # Formula: (m * prior_mean + sum(scores)) / (m + N)
        bayes_avg = (self.prior_weight_m * self.prior_mean + sum(scores)) / (self.prior_weight_m + n)

        # 2. Recency / Progression Weighting: Rewards candidates warming up in later deep-dive turns
        if n == 1:
            recency_avg = scores[0]
        else:
            weights = [0.85 + 0.30 * (i / (n - 1)) for i in range(n)]
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            recency_avg = weighted_sum / sum(weights)

        # Blended Base Score
        blended = (0.60 * recency_avg) + (0.40 * bayes_avg)

        # 3. Completeness Scaling
        # If an interview is terminated after only 1 or 2 turns without finishing core phases, apply completeness damp
        if not is_completed or n < 3:
            completeness_factor = max(0.65, min(1.0, 0.65 + (0.10 * n)))
        else:
            completeness_factor = 1.0

        normalized = max(10.0, min(100.0, blended * completeness_factor))
        adjustment = normalized - raw_avg

        meta = LengthNormalizationMetadata(
            total_turns_evaluated=n,
            expected_standard_turns=self.standard_turns,
            raw_average_score=round(raw_avg, 2),
            normalized_score=round(normalized, 2),
            prior_mean=self.prior_mean,
            prior_weight_m=self.prior_weight_m,
            recency_weighted_average=round(recency_avg, 2),
            session_completeness_factor=round(completeness_factor, 2),
            normalization_adjustment=round(adjustment, 2)
        )

        return round(normalized, 2), meta


class HRInterviewScoringEngine:
    """Master HR Interview Scoring Engine combining all 4 parameters into an explainable score report."""

    def __init__(self, weight_system: Optional[WeightConfigurationSystem] = None):
        self.relevance_analyzer = AnswerRelevanceAnalyzer()
        self.length_normalizer = LengthNormalizationEngine()
        self.weight_system = weight_system or WeightConfigurationSystem()

    def evaluate_session(
        self,
        session: HRInterviewSession,
        custom_weight_profile: Optional[WeightProfile] = None
    ) -> CandidateHRScoreReport:
        """Evaluates an entire HR interview session and produces the standardized Candidate HR Score Report."""
        # 1. Determine Weight Profile
        if custom_weight_profile:
            profile = custom_weight_profile
        else:
            profile = self.weight_system.get_profile(session.config.job_role)

        # Only evaluate completed turns that contain a candidate response
        completed_turns = [t for t in session.turns if t.candidate_response is not None]
        turns = completed_turns if completed_turns else session.turns
        turn_count = len(turns)

        # 2. Extract Turn-by-Turn Scores across the 4 Parameters
        relevance_scores: List[float] = []
        communication_scores: List[float] = []
        confidence_scores: List[float] = []
        consistency_scores: List[float] = []

        trajectory_records: List[Dict[str, Any]] = []

        for idx, t in enumerate(turns):
            # A. Answer Relevance
            rel_eval = self.relevance_analyzer.evaluate_turn_relevance(
                turn_index=idx,
                prompt=t.ai_prompt,
                response=t.candidate_response,
                category=t.category.value
            )
            relevance_scores.append(rel_eval.raw_relevance_score)

            # B. Communication Score
            if t.communication_score:
                comm_score = (
                    getattr(t.communication_score, "normalized_score", None) or
                    getattr(t.communication_score, "raw_composite_score", None) or
                    getattr(t.communication_score, "overall_score", 75.0)
                )
            else:
                # Fallback heuristic based on length and clarity
                comm_score = max(40.0, min(95.0, 50.0 + (t.word_count * 0.4)))
            communication_scores.append(comm_score)

            # C. Confidence Score
            if t.confidence_evaluation:
                conf_score = t.confidence_evaluation.confidence_score
                cons_score = t.confidence_evaluation.consistency_score
            else:
                conf_score = max(50.0, min(95.0, t.confidence_score * 100.0 if t.confidence_score <= 1.0 else t.confidence_score))
                cons_score = 90.0  # default clean
            confidence_scores.append(conf_score)
            consistency_scores.append(cons_score)

            trajectory_records.append({
                "turn_index": idx + 1,
                "phase": t.phase.value,
                "category": t.category.value,
                "relevance": rel_eval.raw_relevance_score,
                "communication": round(comm_score, 1),
                "confidence": round(conf_score, 1),
                "consistency": round(cons_score, 1),
                "composite_turn": round(
                    profile.answer_relevance * rel_eval.raw_relevance_score +
                    profile.communication * comm_score +
                    profile.confidence * conf_score +
                    profile.consistency * cons_score,
                    1
                )
            })

        # 3. Apply Length Normalization across all 4 parameters
        norm_rel, rel_meta = self.length_normalizer.normalize_turn_scores(relevance_scores, session.is_completed)
        norm_comm, comm_meta = self.length_normalizer.normalize_turn_scores(communication_scores, session.is_completed)
        norm_conf, conf_meta = self.length_normalizer.normalize_turn_scores(confidence_scores, session.is_completed)
        norm_cons, cons_meta = self.length_normalizer.normalize_turn_scores(consistency_scores, session.is_completed)

        # 4. Calculate Final Weighted Composite Score
        composite = (
            profile.answer_relevance * norm_rel +
            profile.communication * norm_comm +
            profile.confidence * norm_conf +
            profile.consistency * norm_cons
        )
        composite = round(max(0.0, min(100.0, composite)), 2)

        # 5. Explainable Parameter Contributions
        breakdown: Dict[str, ParameterContribution] = {
            ScoringParameter.ANSWER_RELEVANCE.value: ParameterContribution(
                parameter=ScoringParameter.ANSWER_RELEVANCE,
                display_name="Answer Relevance & Depth",
                raw_score=rel_meta.raw_average_score,
                normalized_score=norm_rel,
                weight=profile.answer_relevance,
                weighted_contribution=round(norm_rel * profile.answer_relevance, 2),
                percentage_of_total=round((norm_rel * profile.answer_relevance / max(0.1, composite)) * 100.0, 1),
                diagnostic_summary=f"Candidate addressed prompt intent with {norm_rel:.1f}/100 normalized depth."
            ),
            ScoringParameter.COMMUNICATION.value: ParameterContribution(
                parameter=ScoringParameter.COMMUNICATION,
                display_name="Communication & Structure",
                raw_score=comm_meta.raw_average_score,
                normalized_score=norm_comm,
                weight=profile.communication,
                weighted_contribution=round(norm_comm * profile.communication, 2),
                percentage_of_total=round((norm_comm * profile.communication / max(0.1, composite)) * 100.0, 1),
                diagnostic_summary=f"Articulated ideas with {norm_comm:.1f}/100 structural fluency and grammar hygiene."
            ),
            ScoringParameter.CONFIDENCE.value: ParameterContribution(
                parameter=ScoringParameter.CONFIDENCE,
                display_name="Behavioral Confidence & Poise",
                raw_score=conf_meta.raw_average_score,
                normalized_score=norm_conf,
                weight=profile.confidence,
                weighted_contribution=round(norm_conf * profile.confidence, 2),
                percentage_of_total=round((norm_conf * profile.confidence / max(0.1, composite)) * 100.0, 1),
                diagnostic_summary=f"Exhibited composure of {norm_conf:.1f}/100 with low hesitation latency."
            ),
            ScoringParameter.CONSISTENCY.value: ParameterContribution(
                parameter=ScoringParameter.CONSISTENCY,
                display_name="Factual & Narrative Consistency",
                raw_score=cons_meta.raw_average_score,
                normalized_score=norm_cons,
                weight=profile.consistency,
                weighted_contribution=round(norm_cons * profile.consistency, 2),
                percentage_of_total=round((norm_cons * profile.consistency / max(0.1, composite)) * 100.0, 1),
                diagnostic_summary=f"Maintained narrative alignment at {norm_cons:.1f}/100 without factual clashes."
            ),
        }

        # 6. Recommendation Tier Mapping
        if composite >= 88.0:
            recommendation = HiringRecommendation.STRONG_HIRE
        elif composite >= 76.0:
            recommendation = HiringRecommendation.HIRE
        elif composite >= 65.0:
            recommendation = HiringRecommendation.LEAN_HIRE
        elif composite >= 50.0:
            recommendation = HiringRecommendation.LEAN_NO_HIRE
        else:
            recommendation = HiringRecommendation.NO_HIRE

        # 7. Synthesize Strengths, Risk Flags & Action Items
        strengths = []
        flags = []
        next_steps = []

        if norm_rel >= 85.0:
            strengths.append("High contextual relevance and concrete problem-solving depth with quantifiable metrics.")
        elif norm_rel < 60.0:
            flags.append("Vague or surface-level technical answers lacking architectural specifics.")

        if norm_comm >= 85.0:
            strengths.append("Clear executive articulation using structured STAR/PREP delivery with zero filler crutches.")
        elif norm_comm < 60.0:
            flags.append("Disorganized communication flow with heavy reliance on conversational filler words.")

        if norm_conf >= 85.0:
            strengths.append("Authoritative technical presence and composed demeanor under challenging scenarios.")
        elif norm_conf < 60.0:
            flags.append("Noticeable hesitation pauses, high vocal stress markers, or defensive posturing.")

        if norm_cons >= 90.0:
            strengths.append("Impeccable narrative honesty and seamless cross-turn factual consistency.")
        elif norm_cons < 75.0:
            flags.append("Identified narrative inconsistency or factual divergence across interview turns.")

        if not strengths:
            strengths.append("Steady conversational participation throughout the interview session.")

        if recommendation in [HiringRecommendation.STRONG_HIRE, HiringRecommendation.HIRE]:
            next_steps.append("Advance candidate to final technical bar-raiser or hiring manager round.")
            next_steps.append("Validate system architecture depth on large-scale distributed consensus.")
        elif recommendation == HiringRecommendation.LEAN_HIRE:
            next_steps.append("Schedule focused follow-up round on identified growth areas (e.g. system design trade-offs).")
        else:
            next_steps.append("Do not advance candidate at this time based on behavioral and technical benchmark gaps.")

        # 8. Granular Sub-Dimension Ratings
        comm_sub = {
            "fluency": session.overall_fluency or norm_comm,
            "grammar": session.overall_grammar or norm_comm,
            "vocabulary": session.overall_vocabulary or norm_comm,
            "clarity": session.overall_clarity or norm_comm,
            "filler_control": max(0.0, 100.0 - (session.total_fillers_detected * 5.0)),
            "structure": session.overall_structure or norm_comm,
        }

        conf_sub = {
            "hesitation_control": session.average_confidence_score or norm_conf,
            "sentiment_composure": 85.0 if session.dominant_emotional_tone in ["ENTHUSIASTIC", "MATTER_OF_FACT"] else 55.0,
            "narrative_consistency": norm_cons,
            "stress_resilience": max(0.0, 100.0 - (session.average_stress_index or 15.0)),
        }

        # Executive Summary Paragraph
        summary_text = (
            f"Candidate {session.config.candidate_name} achieved a length-normalized composite score of "
            f"{composite:.1f}/100 ({recommendation.value.replace('_', ' ')}), evaluated across {turn_count} turns "
            f"under the {profile.profile_name} matrix. Parameter breakdown shows Answer Relevance at {norm_rel:.1f}/100 "
            f"({breakdown['answer_relevance'].percentage_of_total}%), Communication at {norm_comm:.1f}/100 "
            f"({breakdown['communication_score'].percentage_of_total}%), Behavioral Confidence at {norm_conf:.1f}/100 "
            f"({breakdown['confidence_score'].percentage_of_total}%), and Consistency at {norm_cons:.1f}/100 "
            f"({breakdown['consistency'].percentage_of_total}%)."
        )

        return CandidateHRScoreReport(
            candidate_id=session.config.candidate_id,
            candidate_name=session.config.candidate_name,
            job_role=session.config.job_role,
            experience_years=session.config.experience_years,
            session_id=session.session_id,
            evaluation_date=datetime.now(timezone.utc).isoformat(),
            weight_profile_used=profile.profile_name,
            composite_score=composite,
            recommendation=recommendation,
            executive_summary=summary_text,
            parameter_breakdown=breakdown,
            length_normalization=rel_meta,
            communication_subdimensions=comm_sub,
            behavioral_subdimensions=conf_sub,
            turn_score_trajectory=trajectory_records,
            key_strengths=strengths,
            risk_flags=flags,
            recommended_next_steps=next_steps
        )
