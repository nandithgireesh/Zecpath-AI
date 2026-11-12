"""
Day 38: Scenario Evaluation Framework (Deliverable 3)
====================================================
Evaluates Situational Judgment Test (SJT) scenarios:
- Problem-Solving Clarity Analyzer (signposting, causal density, depth, decisiveness)
- Multi-criteria situational scoring (Effectiveness, Risk Mitigation, Stakeholder Empathy)
- Cognitive framework alignment verification (IDEA / CARL)
- Composite Aptitude Score synthesis & Cognitive Maturity Tier classification
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from interview_ai.aptitude_models import (
    SituationalScenario,
    ScenarioEvaluationResult,
    ProblemSolvingClarityBreakdown,
    CognitiveMaturityLevel,
    FrameworkType,
)
from interview_ai.logical_reasoning_scorer import LogicalReasoningScorer


class ProblemSolvingClarityAnalyzer:
    """
    Evaluates the structural articulation, communication hygiene,
    and cognitive transparency of problem-solving responses.
    """

    SIGNPOST_MARKERS = [
        "first", "firstly", "step 1", "initially", "phase 1",
        "second", "secondly", "step 2", "subsequently", "phase 2",
        "third", "thirdly", "step 3", "furthermore", "next",
        "finally", "lastly", "in conclusion", "to summarize",
    ]

    DECISIVE_ACTION_VERBS = [
        "isolate", "rollback", "deploy", "instrument", "communicate",
        "prioritize", "execute", "resolve", "implement", "coordinate",
        "audit", "stabilize", "reconfigure", "revert", "escalate",
    ]

    def analyze(self, response: str) -> ProblemSolvingClarityBreakdown:
        if not response or not response.strip():
            return ProblemSolvingClarityBreakdown(
                structural_signposting_score=0.0,
                causal_linkage_density_score=0.0,
                depth_to_breadth_ratio=0.0,
                decisiveness_score=0.0,
                calibrated_clarity_score=0.0,
            )

        resp_lower = response.lower()
        words = re.findall(r"\b\w+\b", resp_lower)
        word_count = len(words)
        sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
        sentence_count = max(1, len(sentences))

        # 1. Structural Signposting (0 - 100)
        signposts_found = sum(1 for marker in self.SIGNPOST_MARKERS if marker in resp_lower)
        if signposts_found >= 3:
            signpost_score = 90.0 + min(10.0, (signposts_found - 3) * 5.0)
        elif signposts_found == 2:
            signpost_score = 80.0
        elif signposts_found == 1:
            signpost_score = 65.0
        else:
            # Check paragraph / bullet formatting
            has_bullets = bool(re.search(r"(\n\s*[-*•\d]\.?\s+)", response))
            signpost_score = 55.0 if has_bullets else 35.0

        # 2. Causal Linkage Density
        causal_tokens = ["because", "since", "therefore", "thus", "consequently", "resulting in", "due to", "so that", "in order to"]
        causal_count = sum(len(re.findall(r"\b" + ct + r"\b", resp_lower)) for ct in causal_tokens)
        causal_density = (causal_count / sentence_count)
        if causal_density >= 0.75:
            causal_score = 92.0
        elif causal_density >= 0.40:
            causal_score = 80.0
        elif causal_density >= 0.20 or causal_count >= 1:
            causal_score = 70.0
        else:
            causal_score = 45.0

        # 3. Depth-to-Breadth Ratio
        avg_sentence_len = word_count / sentence_count
        # Well-reasoned technical responses typically average 10-30 words per sentence
        if 9.0 <= avg_sentence_len <= 32.0 and word_count >= 40:
            depth_ratio = 1.0
        elif word_count < 25:
            depth_ratio = 0.6
        else:
            depth_ratio = 0.85

        # 4. Decisiveness Score (0 - 100)
        action_hits = sum(1 for verb in self.DECISIVE_ACTION_VERBS if re.search(r"\b" + verb + r"\w*\b", resp_lower))
        if action_hits >= 4:
            decisiveness = 95.0
        elif action_hits >= 2:
            decisiveness = 80.0
        elif action_hits == 1:
            decisiveness = 65.0
        else:
            decisiveness = 45.0

        # Penalize chronic hedging or passive avoidance
        hedges = len(re.findall(r"\b(maybe|i guess|possibly|might work|not sure|dunno)\b", resp_lower))
        decisiveness = max(10.0, decisiveness - (hedges * 8.0))

        # Calibrated Clarity Score
        calibrated = (
            (0.35 * signpost_score) +
            (0.30 * causal_score) +
            (0.35 * decisiveness)
        ) * depth_ratio

        calibrated = min(100.0, max(10.0, calibrated))

        return ProblemSolvingClarityBreakdown(
            structural_signposting_score=round(signpost_score, 1),
            causal_linkage_density_score=round(causal_score, 1),
            depth_to_breadth_ratio=round(depth_ratio, 2),
            decisiveness_score=round(decisiveness, 1),
            calibrated_clarity_score=round(calibrated, 1),
        )


class ScenarioEvaluator:
    """
    Master evaluator for Situational Judgment Test (SJT) scenarios.
    Combines logical reasoning, problem-solving clarity, situational effectiveness,
    risk mitigation, and stakeholder management into an explainable assessment.
    """

    RISK_MITIGATION_KEYWORDS = [
        "rollback", "circuit breaker", "feature flag", "monitoring", "alert",
        "telemetry", "backup", "failover", "post-mortem", "canary", "revert",
        "sandbox", "gradual rollout", "contingency", "audit trail", "safeguard",
    ]

    STAKEHOLDER_AWARENESS_KEYWORDS = [
        "communicate", "stakeholder", "client", "customer", "transparent",
        "update", "align", "leadership", "expectation", "status page",
        "team", "collaborate", "inform", "retrospective", "debrief",
    ]

    def __init__(self, logic_scorer: Optional[LogicalReasoningScorer] = None):
        self.logic_scorer = logic_scorer or LogicalReasoningScorer()
        self.clarity_analyzer = ProblemSolvingClarityAnalyzer()

    def evaluate_scenario(
        self,
        scenario: SituationalScenario,
        candidate_response: str,
    ) -> ScenarioEvaluationResult:
        """
        Evaluate candidate situational judgment response against scenario constraints and framework.
        """
        resp_lower = candidate_response.lower()

        # 1. Logical Reasoning Breakdown
        logic_breakdown = self.logic_scorer.evaluate(candidate_response, scenario)

        # 2. Problem-Solving Clarity Breakdown
        clarity_breakdown = self.clarity_analyzer.analyze(candidate_response)

        # 3. Situational Effectiveness Scoring (0 - 100)
        effectiveness_score, matched_optimal, matched_risks = self._score_effectiveness(
            resp_lower, scenario
        )

        # 4. Risk Mitigation Score (0 - 100)
        risk_mitigation_score = self._score_risk_mitigation(resp_lower)

        # 5. Stakeholder Awareness Score (0 - 100)
        stakeholder_score = self._score_stakeholder_awareness(resp_lower)

        # 6. Framework Adherence Check (IDEA / CARL)
        framework_adherence = self._evaluate_framework_adherence(resp_lower, scenario)

        # 7. Composite Cognitive Aptitude Score Synthesis
        # Weightage: Logic 35%, Clarity 25%, Effectiveness 25%, Risk Mitigation 15%
        composite = (
            (0.35 * logic_breakdown.calibrated_logic_score) +
            (0.25 * clarity_breakdown.calibrated_clarity_score) +
            (0.25 * effectiveness_score) +
            (0.15 * risk_mitigation_score)
        )
        composite = round(min(100.0, max(0.0, composite)), 1)

        # 8. Cognitive Maturity Level Classification
        maturity = self._classify_maturity(composite)

        # 9. Strengths, Flags & Coaching
        strengths, flags, coaching = self._generate_diagnostics(
            logic_breakdown, clarity_breakdown, effectiveness_score,
            risk_mitigation_score, stakeholder_score, matched_optimal, matched_risks
        )

        return ScenarioEvaluationResult(
            scenario_id=scenario.scenario_id,
            scenario_title=scenario.title,
            category=scenario.category,
            candidate_response=candidate_response,
            logical_reasoning=logic_breakdown,
            problem_solving_clarity=clarity_breakdown,
            situational_effectiveness_score=round(effectiveness_score, 1),
            risk_mitigation_score=round(risk_mitigation_score, 1),
            stakeholder_awareness_score=round(stakeholder_score, 1),
            composite_aptitude_score=composite,
            cognitive_maturity=maturity,
            framework_adherence_percent=round(framework_adherence, 1),
            observed_strengths=strengths,
            cognitive_flags=flags,
            recruiter_coaching_notes=coaching,
            evaluated_at=datetime.now(timezone.utc),
        )

    def _score_effectiveness(
        self,
        resp_lower: str,
        scenario: SituationalScenario,
    ) -> (float, List[str], List[str]):
        """Match response against scenario-specific optimal and high-risk action cues."""
        base_score = 60.0
        matched_optimal = []
        matched_risks = []

        # Optimal Actions (+8 to +15 pts each)
        for cue in scenario.optimal_action_cues:
            cue_words = [w.lower() for w in re.findall(r"\b\w{4,}\b", cue)]
            if sum(1 for cw in cue_words if cw in resp_lower) >= max(1, len(cue_words) // 2):
                matched_optimal.append(cue)
                base_score += 10.0

        # High-Risk Anti-Patterns (-15 to -30 pts each)
        for risk in scenario.high_risk_action_cues:
            risk_words = [w.lower() for w in re.findall(r"\b\w{4,}\b", risk)]
            if not risk_words:
                continue
            primary_trigger = risk_words[0]
            context_matches = sum(1 for rw in risk_words[1:] if rw in resp_lower)
            if primary_trigger in resp_lower and (context_matches >= max(1, len(risk_words[1:]) // 2)):
                matched_risks.append(risk)
                base_score -= 20.0

        return min(100.0, max(10.0, base_score)), matched_optimal, matched_risks

    def _score_risk_mitigation(self, resp_lower: str) -> float:
        """Evaluate safeguards, telemetry, and rollback awareness."""
        hits = sum(1 for kw in self.RISK_MITIGATION_KEYWORDS if kw in resp_lower)
        if hits >= 4:
            return 95.0
        elif hits >= 2:
            return 82.0
        elif hits == 1:
            return 65.0
        else:
            return 40.0

    def _score_stakeholder_awareness(self, resp_lower: str) -> float:
        """Evaluate communication, transparency, and empathy with affected parties."""
        hits = sum(1 for kw in self.STAKEHOLDER_AWARENESS_KEYWORDS if kw in resp_lower)
        if hits >= 4:
            return 95.0
        elif hits >= 2:
            return 80.0
        elif hits == 1:
            return 65.0
        else:
            return 45.0

    def _evaluate_framework_adherence(
        self,
        resp_lower: str,
        scenario: SituationalScenario,
    ) -> float:
        """Calculate percentage completion of prescribed IDEA / CARL framework milestones."""
        ideal = scenario.ideal_structure
        milestones = [
            ideal.stage_1_identify,
            ideal.stage_2_constraints,
            ideal.stage_3_evaluation,
            ideal.stage_4_action_plan,
        ]

        hits = 0
        for stage in milestones:
            stage_words = [w.lower() for w in re.findall(r"\b\w{4,}\b", stage)]
            if any(sw in resp_lower for sw in stage_words):
                hits += 1

        return (hits / len(milestones)) * 100.0

    def _classify_maturity(self, score: float) -> CognitiveMaturityLevel:
        if score >= 85.0:
            return CognitiveMaturityLevel.EXEMPLARY
        elif score >= 70.0:
            return CognitiveMaturityLevel.PROFICIENT
        elif score >= 55.0:
            return CognitiveMaturityLevel.COMPETENT
        elif score >= 40.0:
            return CognitiveMaturityLevel.SUPERFICIAL
        else:
            return CognitiveMaturityLevel.DEFICIENT

    def _generate_diagnostics(
        self,
        logic: Any,
        clarity: Any,
        effectiveness: float,
        risk: float,
        stakeholder: float,
        matched_optimal: List[str],
        matched_risks: List[str],
    ) -> (List[str], List[str], List[str]):
        strengths = []
        flags = []
        coaching = []

        if logic.calibrated_logic_score >= 80.0:
            strengths.append("High cognitive rigor: Structured deductive reasoning and clear cause-and-effect linkages.")
        if logic.tradeoff_depth_score >= 75.0:
            strengths.append("Nuanced trade-off awareness: Thoroughly weighs alternatives before committing to an approach.")
        if clarity.structural_signposting_score >= 80.0:
            strengths.append("Exceptional structural signposting: Clearly demarcated problem-solving sequence.")
        if risk >= 80.0:
            strengths.append("Proactive risk containment: Integrates telemetry, rollback plans, and safeguards.")
        if stakeholder >= 80.0:
            strengths.append("Mature stakeholder alignment: Emphasizes transparent communications and customer trust.")

        for f in logic.detected_fallacies:
            flags.append(f)
        for r in matched_risks:
            flags.append(f"Anti-pattern identified: Demonstrated risky behavior ({r}).")

        if logic.tradeoff_depth_score < 50.0:
            flags.append("Superficial analysis: Overlooked secondary trade-offs or long-term operational costs.")
            coaching.append("Probe candidate on edge cases and failure modes under extreme scale.")
        if risk < 50.0:
            flags.append("Limited risk containment: Proposed execution steps without explicit rollback procedures.")
            coaching.append("Ask how candidate would mitigate partial failure during high-concurrency rollout.")
        if clarity.decisiveness_score < 50.0:
            flags.append("Ambiguity paralysis: Excessive hesitation or non-committal language.")
            coaching.append("Assess candidate's ability to make high-conviction decisions with incomplete data.")

        return strengths, flags, coaching
