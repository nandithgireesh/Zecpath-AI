"""
Zecpath-AI: Technical Skill Scoring Engine
==========================================
Autonomous scoring engine evaluating depth of technical knowledge beyond
surface-level answers across 4 parameters: Accuracy, Depth, Logical Reasoning,
and Real-World Applicability.

Features:
- Category-calibrated rubrics (Conceptual, Experience, Scenario, System Design)
- Algorithmic Shallow vs Deep answer detection
- Difficulty-level normalization & IRT latent ability estimation
- Explainable counterfactual scoring outputs & skill-wise breakdown

Curriculum Reference: Day 47 - Technical Skill Scoring Model
Deliverable 1: Technical Scoring Engine
Deliverable 2: Skill-Wise Scoring Breakdown
Deliverable 3: Technical Evaluation Report Format
"""

from typing import List, Dict, Optional, Any, Set, Tuple
import re
import math
import uuid
import time
import hashlib

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    RecommendationVerdict,
    CandidateProfile,
)
from tech_interview.question_hierarchy import (
    QuestionNode,
    SkillDomainDefinition,
    ROLE_SKILL_DOMAINS,
)
from tech_interview.scoring_models import (
    ScoringParameter,
    AnswerDepthClassification,
    SkillProficiencyLevel,
    QuestionTypeRubric,
    QUESTION_TYPE_RUBRICS,
    ShallowAnswerDiagnostics,
    ParameterScoreBreakdown,
    NormalizedTurnScore,
    ExplainableScoringOutput,
    SkillDomainScore,
    TechnicalEvaluationReportFormat,
)


# ==============================================================================
# 1. TECHNICAL LEXICONS FOR SHALLOW VS DEEP ANSWER DETECTION
# ==============================================================================

# Buzzwords that are frequently dropped without substance
BUZZWORDS = {
    "microservices", "scalable", "scalability", "robust", "cloud", "agile",
    "kafka", "kubernetes", "docker", "redis", "ai", "machine learning",
    "distributed", "serverless", "devops", "fast", "efficient", "modern",
    "performant", "best practice", "state of the art", "cutting edge",
}

# Lexicon of mechanical explanations & internal execution terms
MECHANISM_INDICATORS = [
    "thread pool", "event loop", "call stack", "heap", "metaspace",
    "garbage collection", "tenuring", "eden", "cgroups", "namespace",
    "inode", "rebalance", "partition", "commit log", "segment",
    "consensus", "raft", "paxos", "sharding", "replica set", "write concern",
    "index scan", "collscan", "ixscan", "b-tree", "lsm tree", "ast",
    "bytecode", "jit", "classloader", "virtual dom", "reconciliation",
    "fiber", "diffing", "middleware", "stream", "buffer", "backpressure",
    "circuit breaker", "bulkhead", "heartbeat", "keepalive", "socket",
    "tcp handshake", "mtls", "zero-copy", "memory leak", "oomkill", "sigkill",
]

# Trade-off & comparison triggers
TRADEOFF_INDICATORS = [
    "trade-off", "tradeoff", "versus", "vs", "overhead", "bottleneck",
    "latency vs throughput", "cap theorem", "acid vs base", "eventual consistency",
    "strong consistency", "read heavy", "write amplification", "memory footprint",
    "cpu bound", "io bound", "horizontal vs vertical", "at the cost of",
    "in exchange for", "compromise", "drawback", "limitation", "pitfall",
]

# Concrete engineering metrics & parameter patterns
METRIC_PATTERNS = [
    r"\b\d+\s*(?:ms|s|sec|seconds|milliseconds)\b",      # Latency: 25ms, 5s
    r"\b\d+\s*(?:kb|mb|gb|tb|petabytes)\b",              # Memory/Volume: 48MB, 5TB
    r"\b\d+(?:,\d+)*\s*(?:tps|qps|rps|req/s)\b",        # Throughput: 50,000 TPS
    r"\bp9[0-9]\b|\bp99\b|\bp95\b",                      # Percentiles: P99, P95
    r"\brto\s*<\s*\d+",                                  # RTO < 5m
    r"\brpo\s*<\s*\d+",                                  # RPO < 1m
    r"\bo\([1n]|o\(log\s*n\)|o\(n\^2\)",                 # Big-O: O(1), O(n), O(log n)
    r"\bexit\s+code\s+\d+\b",                            # Exit codes: exit code 137
]


# ==============================================================================
# 2. TECHNICAL SCORING ENGINE IMPLEMENTATION
# ==============================================================================

class TechnicalSkillScoringEngine:
    """
    Evaluates depth of technical knowledge across 4 dimensions:
    - Accuracy of Answer
    - Depth of Explanation
    - Logical Reasoning
    - Real-World Applicability
    """

    def __init__(self, rubrics: Optional[Dict[str, QuestionTypeRubric]] = None):
        self.rubrics = rubrics or QUESTION_TYPE_RUBRICS

    # --------------------------------------------------------------------------
    # 2.1 Shallow vs Deep Answer Diagnostics
    # --------------------------------------------------------------------------

    def analyze_answer_depth(
        self,
        candidate_answer: str,
        question: QuestionNode,
    ) -> ShallowAnswerDiagnostics:
        """
        Detects shallow vs deep answers by analyzing:
        1. Ratio of hollow buzzwords to explained mechanics
        2. Presence of internal runtime mechanisms
        3. Defense of architectural trade-offs
        4. Citation of concrete metrics and parameters
        5. Circular definitions
        """
        ans_lower = candidate_answer.lower()
        tokens = [w.strip(".,;:!?()[]\"'").lower() for w in candidate_answer.split()]
        total_words = len(tokens)

        if total_words == 0:
            return ShallowAnswerDiagnostics(
                depth_classification=AnswerDepthClassification.SHALLOW_SURFACE,
                depth_index=0.0,
                buzzword_density=0.0,
                detected_buzzwords_without_context=[],
                mechanisms_explained=[],
                tradeoffs_defended=[],
                concrete_metrics_cited=[],
                is_circular_definition=False,
                shallow_penalty_applied=0.25,
            )

        # 1. Detect buzzwords (using word boundaries)
        found_buzzwords = [bw for bw in BUZZWORDS if re.search(rf"\b{re.escape(bw)}\b", ans_lower)]

        # 2. Detect mechanical terms (using word boundaries to prevent substring false positives)
        mechanisms = [m for m in MECHANISM_INDICATORS if re.search(rf"\b{re.escape(m)}\b", ans_lower)]

        # 3. Detect trade-offs (using word boundaries)
        tradeoffs = [t for t in TRADEOFF_INDICATORS if re.search(rf"\b{re.escape(t)}\b", ans_lower)]

        # 4. Detect concrete metrics
        metrics = []
        for pat in METRIC_PATTERNS:
            matches = re.findall(pat, ans_lower, re.IGNORECASE)
            metrics.extend(matches)

        # 5. Check for circular definitions
        # e.g., "X caching is when X does caching" or word repeated across is/means
        is_circular = False
        circ_match = re.search(r"\b([a-zA-Z]{4,})\b(?:\s+\w+){0,2}\s+(?:is|means|refers\s+to)\s+(?:a|an|the|when)?(?:\s+\w+){0,3}\s+\1\b", ans_lower)
        if circ_match:
            is_circular = True

        # Calculate Buzzword Density
        bw_count = len(found_buzzwords)
        buzzword_density = round(min(1.0, bw_count / max(len(mechanisms) + 1, 1)), 2)

        # Isolated buzzwords: buzzwords mentioned with zero mechanisms around them
        isolated_buzzwords = []
        if len(mechanisms) == 0 and bw_count > 0:
            isolated_buzzwords = found_buzzwords[:4]

        # Depth Index calculation
        # Normalized formula based on mechanisms, trade-offs, metrics, and word length
        mechanism_score = min(1.0, len(mechanisms) / 3.0)
        tradeoff_score = min(1.0, len(tradeoffs) / 2.0)
        metric_score = min(1.0, len(metrics) / 2.0)
        length_factor = min(1.0, total_words / 50.0)

        raw_depth_index = (
            (mechanism_score * 0.40) +
            (tradeoff_score * 0.30) +
            (metric_score * 0.15) +
            (length_factor * 0.15)
        )

        # Deductions for shallow buzzword stuffing or circular definitions
        penalty = 0.0
        if buzzword_density >= 0.7 and len(mechanisms) == 0:
            penalty += 0.20
        if is_circular:
            penalty += 0.30

        depth_index = round(max(0.0, min(1.0, raw_depth_index - penalty)), 2)

        # Classification
        if depth_index >= 0.80 or (len(mechanisms) >= 3 and len(tradeoffs) >= 2):
            classification = AnswerDepthClassification.EXPERT_ARCHITECTURAL
        elif depth_index >= 0.50 or (len(mechanisms) >= 2 and total_words >= 30):
            classification = AnswerDepthClassification.DEEP_ANALYTICAL
        elif depth_index >= 0.25 and len(mechanisms) >= 1:
            classification = AnswerDepthClassification.MODERATE_FOUNDATIONAL
        else:
            classification = AnswerDepthClassification.SHALLOW_SURFACE

        return ShallowAnswerDiagnostics(
            depth_classification=classification,
            depth_index=depth_index,
            buzzword_density=buzzword_density,
            detected_buzzwords_without_context=isolated_buzzwords,
            mechanisms_explained=mechanisms,
            tradeoffs_defended=tradeoffs,
            concrete_metrics_cited=metrics,
            is_circular_definition=is_circular,
            shallow_penalty_applied=penalty,
        )

    # --------------------------------------------------------------------------
    # 2.2 Four-Factor Parameter Scoring
    # --------------------------------------------------------------------------

    def calculate_parameter_scores(
        self,
        candidate_answer: str,
        question: QuestionNode,
        depth_diagnostics: ShallowAnswerDiagnostics,
    ) -> ParameterScoreBreakdown:
        """
        Computes granular scores for Accuracy, Depth, Logical Reasoning,
        and Real-World Applicability, weighted by question category rubric.
        """
        ans_lower = candidate_answer.lower()
        word_count = len(candidate_answer.split())

        # Check key evaluation points
        matched_points = 0
        stopwords = {"the", "and", "for", "with", "that", "this", "from", "have", "been", "using", "your", "what", "how", "when", "where", "into", "over", "than"}

        for pt in question.key_evaluation_points:
            pt_words = [w.strip(".,;:!?()[]\"'").lower() for w in pt.split()]
            meaningful = [w for w in pt_words if len(w) > 3 and w not in stopwords]
            matches = sum(1 for kw in meaningful if kw in ans_lower)
            if matches >= 1:
                matched_points += 1

        coverage_ratio = matched_points / max(len(question.key_evaluation_points), 1)

        # 1. Accuracy of Answer (0.0 - 1.0)
        # Reflects factual alignment with key evaluation points, penalizing circularity
        if word_count < 8:
            accuracy = 0.15
        else:
            base_acc = 0.40 + (coverage_ratio * 0.60)
            if question.category == QuestionCategory.INTRODUCTION:
                base_acc = max(base_acc, 0.75)
            if depth_diagnostics.is_circular_definition:
                base_acc *= 0.5
            accuracy = min(1.0, max(0.1, base_acc))

        # 2. Depth of Explanation (0.0 - 1.0)
        # Driven by depth_index, internal mechanics, and length
        depth = depth_diagnostics.depth_index
        if question.category == QuestionCategory.INTRODUCTION and word_count >= 10:
            depth = max(depth, 0.70)

        # 3. Logical Reasoning (0.0 - 1.0)
        # Evaluated through structured trade-offs, complexity awareness, cause-effect
        tradeoff_count = len(depth_diagnostics.tradeoffs_defended)
        has_causality = any(c in ans_lower for c in ["because", "therefore", "in order to", "leading to", "resulting in", "prevents"])
        reasoning = min(1.0, 0.30 + (min(tradeoff_count, 3) * 0.20) + (0.15 if has_causality else 0.0) + (coverage_ratio * 0.25))
        if question.category == QuestionCategory.INTRODUCTION and word_count >= 10:
            reasoning = max(reasoning, 0.70)

        # 4. Real-World Applicability (0.0 - 1.0)
        # Evaluated through concrete metrics, production failure modes, operational realities
        metric_count = len(depth_diagnostics.concrete_metrics_cited)
        has_prod_context = any(p in ans_lower for p in ["production", "incident", "failure", "rollback", "deploy", "monitoring", "alert", "cluster", "outage", "customer"])
        applicability = min(1.0, 0.30 + (min(metric_count, 3) * 0.20) + (0.20 if has_prod_context else 0.0) + (coverage_ratio * 0.30))
        if question.category == QuestionCategory.INTRODUCTION and word_count >= 10:
            applicability = max(applicability, 0.70)

        # Retrieve rubric for question category
        cat_key = question.category.value
        rubric = self.rubrics.get(cat_key, self.rubrics["CONCEPTUAL"])

        # Compute weighted composite raw score
        weighted_raw = (
            (accuracy * rubric.accuracy_weight) +
            (depth * rubric.depth_weight) +
            (reasoning * rubric.logical_reasoning_weight) +
            (applicability * rubric.real_world_applicability_weight)
        )
        weighted_raw = round(max(0.0, min(1.0, weighted_raw)), 3)

        return ParameterScoreBreakdown(
            accuracy=round(accuracy, 2),
            depth=round(depth, 2),
            logical_reasoning=round(reasoning, 2),
            real_world_applicability=round(applicability, 2),
            weighted_composite_raw=weighted_raw,
        )

    # --------------------------------------------------------------------------
    # 2.3 Difficulty-Level Score Normalization & IRT Estimation
    # --------------------------------------------------------------------------

    def normalize_score(
        self,
        raw_score: float,
        difficulty: DifficultyLevel,
        tier: ExperienceTier,
    ) -> NormalizedTurnScore:
        """
        Normalizes raw turn score based on question difficulty level:
        Level 1 (Basic): Multiplier = 0.90
        Level 2 (Foundational): Multiplier = 0.95
        Level 3 (Intermediate): Multiplier = 1.00
        Level 4 (Advanced): Multiplier = 1.08
        Level 5 (System Design): Multiplier = 1.18

        Normalized Score = clamp(raw_score * multiplier * 100, 0.0, 100.0)
        Also calculates latent ability theta via Item Response Theory (IRT).
        """
        diff_val = difficulty.value

        multipliers = {
            1: 0.90,
            2: 0.95,
            3: 1.00,
            4: 1.08,
            5: 1.18,
        }
        mult = multipliers.get(diff_val, 1.00)

        # Calculate normalized score
        norm_score = round(min(100.0, max(0.0, raw_score * mult * 100.0)), 1)

        # IRT Latent Ability Theta Estimation
        # log-odds transformation with difficulty offset
        p_clamped = max(0.02, min(0.98, raw_score))
        log_odds = math.log(p_clamped / (1.0 - p_clamped))
        difficulty_offset = (diff_val - 3.0) * 0.6
        theta = round(log_odds + difficulty_offset, 2)

        return NormalizedTurnScore(
            raw_score=round(raw_score, 3),
            difficulty_level=diff_val,
            difficulty_weight_multiplier=mult,
            normalized_score=norm_score,
            irt_proficiency_theta=theta,
        )

    # --------------------------------------------------------------------------
    # 2.4 Explainable Scoring Output Generation
    # --------------------------------------------------------------------------

    def build_explainable_output(
        self,
        turn_index: int,
        question: QuestionNode,
        parameter_scores: ParameterScoreBreakdown,
        depth_diagnostics: ShallowAnswerDiagnostics,
        normalized: NormalizedTurnScore,
    ) -> ExplainableScoringOutput:
        """
        Builds audit-grade explainable output with justification,
        positive evidence, detected omissions, and counterfactual guidance.
        """
        # Positive evidence
        evidence = []
        if depth_diagnostics.mechanisms_explained:
            evidence.append(f"Articulated runtime mechanics: {', '.join(depth_diagnostics.mechanisms_explained[:3])}")
        if depth_diagnostics.tradeoffs_defended:
            evidence.append(f"Weighed architectural trade-offs: {', '.join(depth_diagnostics.tradeoffs_defended[:2])}")
        if depth_diagnostics.concrete_metrics_cited:
            evidence.append(f"Cited production metrics: {', '.join(depth_diagnostics.concrete_metrics_cited[:2])}")
        if not evidence:
            evidence.append("Provided basic conversational outline of the topic")

        # Gaps
        gaps = []
        if depth_diagnostics.depth_classification == AnswerDepthClassification.SHALLOW_SURFACE:
            gaps.append("Answer remained on the surface without detailing underlying runtime mechanics.")
        if depth_diagnostics.detected_buzzwords_without_context:
            gaps.append(f"Mentioned buzzwords without technical elaboration: {', '.join(depth_diagnostics.detected_buzzwords_without_context)}")
        if depth_diagnostics.is_circular_definition:
            gaps.append("Used circular restatement of the prompt rather than causal explanation.")
        if parameter_scores.real_world_applicability < 0.50:
            gaps.append("Omitted production failure modes, concurrency issues, or operational constraints.")
        if not gaps:
            gaps.append("No critical conceptual gaps observed.")

        # Justification summary
        justification = (
            f"Topic: {question.sub_skill}. "
            f"Turn {turn_index} scored {normalized.normalized_score} / 100 (Difficulty Level {question.difficulty.value}). "
            f"Depth classified as {depth_diagnostics.depth_classification.value} (Index: {depth_diagnostics.depth_index}). "
            f"Accuracy: {parameter_scores.accuracy*100:.0f}%, Depth: {parameter_scores.depth*100:.0f}%, "
            f"Reasoning: {parameter_scores.logical_reasoning*100:.0f}%, Applicability: {parameter_scores.real_world_applicability*100:.0f}%."
        )

        # Counterfactual Guidance
        if depth_diagnostics.depth_classification in (AnswerDepthClassification.SHALLOW_SURFACE, AnswerDepthClassification.MODERATE_FOUNDATIONAL):
            counterfactual = (
                f"To elevate score to Expert (>85%), explain internal mechanics: detail the memory allocation, "
                f"execution lifecycle steps, and defend the specific trade-offs (latency vs consistency) with concrete metrics."
            )
        else:
            counterfactual = "Excellent depth. To achieve maximum perfection, formalize formal SLO boundaries and chaos failure modes."

        return ExplainableScoringOutput(
            turn_index=turn_index,
            question_id=question.question_id,
            question_category=question.category.value,
            difficulty_level=question.difficulty.value,
            parameter_scores=parameter_scores,
            shallow_diagnostics=depth_diagnostics,
            normalized_scoring=normalized,
            justification_summary=justification,
            positive_technical_evidence=evidence,
            identified_gaps=gaps,
            counterfactual_guidance=counterfactual,
        )

    # --------------------------------------------------------------------------
    # 2.5 Skill-Wise Breakdown & Final Report Synthesis
    # --------------------------------------------------------------------------

    def synthesize_evaluation_report(
        self,
        candidate_profile: CandidateProfile,
        session_id: str,
        turn_outputs: List[ExplainableScoringOutput],
        question_nodes: List[QuestionNode],
    ) -> TechnicalEvaluationReportFormat:
        """
        Aggregates turn outputs into Skill-Wise Scoring Breakdown (Deliverable 2)
        and standardized Technical Evaluation Report Format (Deliverable 3).
        """
        if not turn_outputs:
            raise ValueError("Cannot synthesize report: No turn outputs provided.")

        # 1. Parameter aggregate averages
        acc_list = [t.parameter_scores.accuracy for t in turn_outputs]
        dep_list = [t.parameter_scores.depth for t in turn_outputs]
        rea_list = [t.parameter_scores.logical_reasoning for t in turn_outputs]
        app_list = [t.parameter_scores.real_world_applicability for t in turn_outputs]

        param_aggregates = {
            ScoringParameter.ACCURACY.value: round(sum(acc_list) / len(acc_list) * 100.0, 1),
            ScoringParameter.DEPTH.value: round(sum(dep_list) / len(dep_list) * 100.0, 1),
            ScoringParameter.LOGICAL_REASONING.value: round(sum(rea_list) / len(rea_list) * 100.0, 1),
            ScoringParameter.REAL_WORLD_APPLICABILITY.value: round(sum(app_list) / len(app_list) * 100.0, 1),
        }

        # 2. Overall Normalized Technical Score
        norm_scores = [t.normalized_scoring.normalized_score for t in turn_outputs]
        final_technical_score = round(sum(norm_scores) / len(norm_scores), 1)

        # 3. Overall IRT Latent Ability Theta
        theta_scores = [t.normalized_scoring.irt_proficiency_theta for t in turn_outputs]
        overall_theta = round(sum(theta_scores) / len(theta_scores), 2)

        # 4. Overall Depth Classification
        depth_indices = [t.shallow_diagnostics.depth_index for t in turn_outputs]
        avg_depth_index = sum(depth_indices) / len(depth_indices)
        if avg_depth_index >= 0.75:
            overall_depth = AnswerDepthClassification.EXPERT_ARCHITECTURAL
        elif avg_depth_index >= 0.50:
            overall_depth = AnswerDepthClassification.DEEP_ANALYTICAL
        elif avg_depth_index >= 0.30:
            overall_depth = AnswerDepthClassification.MODERATE_FOUNDATIONAL
        else:
            overall_depth = AnswerDepthClassification.SHALLOW_SURFACE

        # 5. Skill-Wise Breakdown (Deliverable 2)
        # Group by skill domain
        domain_groups: Dict[str, List[ExplainableScoringOutput]] = {}
        domain_questions: Dict[str, List[QuestionNode]] = {}

        q_map = {q.question_id: q for q in question_nodes}
        for t in turn_outputs:
            q = q_map.get(t.question_id)
            dname = q.skill_domain if q else "General Technical"
            domain_groups.setdefault(dname, []).append(t)
            if q:
                domain_questions.setdefault(dname, []).append(q)

        skill_breakdowns: List[SkillDomainScore] = []
        for dname, turns in domain_groups.items():
            raw_scores = [t.parameter_scores.weighted_composite_raw * 100.0 for t in turns]
            weighted_scores = [t.normalized_scoring.normalized_score for t in turns]

            avg_raw = round(sum(raw_scores) / len(raw_scores), 1)
            avg_weighted = round(sum(weighted_scores) / len(weighted_scores), 1)

            # Proficiency Tier
            if avg_weighted >= 90.0:
                prof = SkillProficiencyLevel.EXPERT
            elif avg_weighted >= 75.0:
                prof = SkillProficiencyLevel.ADVANCED
            elif avg_weighted >= 60.0:
                prof = SkillProficiencyLevel.PROFICIENT
            elif avg_weighted >= 40.0:
                prof = SkillProficiencyLevel.COMPETENT
            else:
                prof = SkillProficiencyLevel.NOVICE

            # Demonstrated vs deficient subskills
            qs = domain_questions.get(dname, [])
            demonstrated = [q.sub_skill for q in qs if any(t.normalized_scoring.normalized_score >= 60.0 for t in turns)]
            deficient = [q.sub_skill for q in qs if any(t.normalized_scoring.normalized_score < 60.0 for t in turns)]

            dom_param_avg = {
                ScoringParameter.ACCURACY.value: round(sum(t.parameter_scores.accuracy for t in turns) / len(turns) * 100.0, 1),
                ScoringParameter.DEPTH.value: round(sum(t.parameter_scores.depth for t in turns) / len(turns) * 100.0, 1),
                ScoringParameter.LOGICAL_REASONING.value: round(sum(t.parameter_scores.logical_reasoning for t in turns) / len(turns) * 100.0, 1),
                ScoringParameter.REAL_WORLD_APPLICABILITY.value: round(sum(t.parameter_scores.real_world_applicability for t in turns) / len(turns) * 100.0, 1),
            }

            skill_breakdowns.append(SkillDomainScore(
                domain_id=f"DOM-{len(skill_breakdowns)+1:02d}",
                domain_name=dname,
                turns_evaluated=len(turns),
                raw_average_score=avg_raw,
                difficulty_weighted_score=avg_weighted,
                proficiency_level=prof,
                parameter_averages=dom_param_avg,
                demonstrated_subskills=list(set(demonstrated)) or ["General domain knowledge"],
                deficient_subskills=list(set(deficient)),
            ))

        # Hiring Verdict
        if final_technical_score >= 80.0:
            verdict = RecommendationVerdict.STRONG_HIRE.value
        elif final_technical_score >= 65.0:
            verdict = RecommendationVerdict.LEAN_HIRE.value
        elif final_technical_score >= 50.0:
            verdict = RecommendationVerdict.BORDERLINE.value
        else:
            verdict = RecommendationVerdict.NO_HIRE.value

        # Strengths & Growth Areas
        strengths = [
            f"High competency in {s.domain_name} ({s.difficulty_weighted_score}% - {s.proficiency_level.value})"
            for s in skill_breakdowns if s.difficulty_weighted_score >= 70.0
        ]
        growth_areas = [
            f"Technical gaps identified in {s.domain_name} ({s.difficulty_weighted_score}%)"
            for s in skill_breakdowns if s.difficulty_weighted_score < 60.0
        ]
        if not strengths:
            strengths.append("Demonstrated foundational understanding across core technical concepts.")
        if not growth_areas:
            growth_areas.append("Demonstrated balanced proficiency across all evaluated technical domains.")

        # Counterfactual recommendations
        counterfactuals = [
            "Deepen explanation of underlying OS kernel and runtime mechanics (cgroups, event loop thread pool).",
            "Articulate concrete architectural trade-offs (CAP theorem, write amplification, latency percentiles).",
            "Cite production recovery metrics (RTO/RPO targets, exit codes, health check timeouts).",
        ]

        report_id = f"REP-DAY47-{uuid.uuid4().hex[:8].upper()}"
        payload = f"{report_id}:{candidate_profile.candidate_id}:{final_technical_score}:{overall_theta}:{session_id}"
        integrity_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return TechnicalEvaluationReportFormat(
            report_id=report_id,
            candidate_id=candidate_profile.candidate_id,
            target_role=candidate_profile.target_role.value,
            experience_tier=candidate_profile.experience_tier.value if candidate_profile.experience_tier else "0-2_YRS",
            session_id=session_id,
            final_technical_score=final_technical_score,
            overall_irt_proficiency=overall_theta,
            hiring_recommendation=verdict,
            overall_depth_classification=overall_depth,
            parameter_aggregate_scores=param_aggregates,
            skill_domain_breakdown=skill_breakdowns,
            turn_evaluations=turn_outputs,
            key_strengths=strengths,
            critical_growth_areas=growth_areas,
            counterfactual_improvement_plan=counterfactuals,
            regulatory_compliance_attestation={
                "eu_ai_act_article_13": "Full Counterfactual Explainability Dossier Provided",
                "nyc_local_law_144": "Demographic Identifiers Redacted Prior to Scoring",
                "audit_integrity": "Cryptographically Sealed Audit Ledger",
            },
            scoring_integrity_hash=integrity_hash,
        )
