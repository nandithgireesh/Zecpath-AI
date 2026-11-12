"""
Day 36 Deliverable 1: Confidence & Stress Indicators Analyzer Module
===================================================================
Production-grade behavioral signal engine evaluating candidate:
1. Hesitation patterns (long pauses, repeated words/stutters, uncertainty phrases)
2. Professional sentiment and emotional composure (via InterviewSentimentScorer)
3. Contradiction patterns (within-turn self-negation and cross-turn factual divergence)
4. Quantitative stress indicators & composite stress index (0-100)
5. Consolidated behavioral confidence score (0-100) & recruitment tiering
"""

import re
from typing import List, Dict, Tuple, Optional, Any, Set
from interview_ai.confidence_models import (
    HesitationType,
    HesitationSignal,
    ContradictionSeverity,
    ContradictionIncident,
    StressLevel,
    StressIndicators,
    ConfidenceTier,
    TurnConfidenceBreakdown,
    SessionConfidenceSummary,
)
from interview_ai.sentiment_scoring_engine import InterviewSentimentScorer


class HesitationPatternDetector:
    """
    Detects vocal and transcript hesitation patterns:
    - Long pauses (response latency > 2.8s or internal pause markers)
    - Repeated words, stutters, and false starts
    - Uncertainty phrases, epistemic hedging, and qualifiers
    """

    # 1. Epistemic hedging and uncertainty markers
    UNCERTAINTY_PATTERNS = [
        (r"\b(i'm not (really |entirely |100% |completely )?sure)\b", 8.0, "Direct statement of uncertainty"),
        (r"\b(not (really )?certain|hard to say)\b", 6.0, "Ambiguity qualifier"),
        (r"\b(could be wrong|might be wrong|don't quote me)\b", 10.0, "Explicit lack of confidence"),
        (r"\bi (think maybe|guess maybe|suppose)\b", 6.0, "Double-hedging phrase"),
        (r"\b(i (think|guess|suppose|assume))\b", 3.0, "Soft epistemic hedge"),
        (r"\b(maybe|perhaps|probably|possibly)\b", 2.5, "Probability qualifier"),
        (r"\b(kind of|sort of)\b", 2.5, "Diminutive qualifier"),
        (r"\b(as far as i (remember|recall|know))\b", 3.5, "Memory uncertainty"),
        (r"\b(to the best of my knowledge)\b", 2.5, "Formal hedge"),
        (r"\b(more or less|somewhat)\b", 2.0, "Vagueness hedge"),
    ]

    # 2. Repeated words and false starts (e.g. "I I", "the the", "we- we")
    REPETITION_PATTERN = re.compile(r"\b([a-zA-Z]{1,})\s+\1\b", re.IGNORECASE)
    FALSE_START_PATTERN = re.compile(r"\b([a-zA-Z]{1,4})-\s*([a-zA-Z]+)\b", re.IGNORECASE)

    # 3. Explicit transcript pause markers (e.g. "[pause 4s]", "[silence 3.5s]", "...")
    EXPLICIT_PAUSE_PATTERN = re.compile(r"\[(?:pause|silence)\s*([\d\.]+)s?\]", re.IGNORECASE)
    ELLIPSIS_PAUSE_PATTERN = re.compile(r"(\.{3,}|--{2,})")

    def __init__(self, normal_latency_threshold_s: float = 2.8):
        self.normal_latency_threshold_s = normal_latency_threshold_s
        self.uncertainty_compiled = [
            (re.compile(p, re.IGNORECASE), pen, desc) for p, pen, desc in self.UNCERTAINTY_PATTERNS
        ]

    def analyze_hesitations(
        self,
        text: str,
        response_time_seconds: float = 0.0,
    ) -> Tuple[List[HesitationSignal], float]:
        """
        Scans text and timing metadata for hesitation patterns.
        Returns detected HesitationSignals and hesitation score (0-100, 100=fluent).
        """
        signals: List[HesitationSignal] = []
        total_penalty = 0.0

        if not text or not text.strip():
            # Blank response is an acute hesitation
            signals.append(
                HesitationSignal(
                    type=HesitationType.LONG_PAUSE,
                    token_or_phrase="[SILENCE]",
                    duration_seconds=response_time_seconds,
                    penalty=50.0,
                    description="No verbal response provided.",
                )
            )
            return signals, 20.0

        lower_text = text.lower()

        # 1. Long response latency check (initial delay before answering)
        if response_time_seconds > self.normal_latency_threshold_s:
            excess = response_time_seconds - self.normal_latency_threshold_s
            # 5 pts per second of excess latency, capped at 30 pts
            latency_penalty = min(30.0, round(excess * 5.0, 1))
            total_penalty += latency_penalty
            signals.append(
                HesitationSignal(
                    type=HesitationType.LONG_PAUSE,
                    token_or_phrase=f"Initial delay {response_time_seconds:.1f}s",
                    duration_seconds=response_time_seconds,
                    penalty=latency_penalty,
                    description=f"Long initial pause of {response_time_seconds:.1f}s before speaking (excess {excess:.1f}s).",
                )
            )

        # 2. Explicit transcript internal pause markers
        for m in self.EXPLICIT_PAUSE_PATTERN.finditer(lower_text):
            try:
                sec = float(m.group(1))
            except ValueError:
                sec = 2.0
            if sec > 2.0:
                pause_penalty = min(20.0, round(sec * 4.0, 1))
                total_penalty += pause_penalty
                signals.append(
                    HesitationSignal(
                        type=HesitationType.LONG_PAUSE,
                        token_or_phrase=m.group(0),
                        char_offset=m.start(),
                        duration_seconds=sec,
                        penalty=pause_penalty,
                        description=f"Internal conversational pause of {sec:.1f} seconds.",
                    )
                )

        # Ellipsis pauses (...)
        ellipsis_matches = list(self.ELLIPSIS_PAUSE_PATTERN.finditer(lower_text))
        if ellipsis_matches:
            ell_count = len(ellipsis_matches)
            ell_penalty = min(15.0, ell_count * 3.5)
            total_penalty += ell_penalty
            signals.append(
                HesitationSignal(
                    type=HesitationType.LONG_PAUSE,
                    token_or_phrase="...",
                    char_offset=ellipsis_matches[0].start(),
                    penalty=ell_penalty,
                    description=f"Hesitation ellipses or trailing pauses detected {ell_count} time(s).",
                )
            )

        # 3. Repeated words (stutters / repetitions: "I I", "we we", "the the")
        rep_matches = list(self.REPETITION_PATTERN.finditer(lower_text))
        for rm in rep_matches:
            token = rm.group(1)
            # Filter intentional emphasis (e.g. "very very")
            if token in {"very", "really", "so"}:
                continue
            rep_pen = 4.0
            total_penalty += rep_pen
            signals.append(
                HesitationSignal(
                    type=HesitationType.REPEATED_WORD,
                    token_or_phrase=rm.group(0),
                    char_offset=rm.start(),
                    penalty=rep_pen,
                    description=f"Repeated word stutter '{rm.group(0)}' detected.",
                )
            )

        # False starts ("pro- project")
        for fsm in self.FALSE_START_PATTERN.finditer(lower_text):
            fs_pen = 4.5
            total_penalty += fs_pen
            signals.append(
                HesitationSignal(
                    type=HesitationType.FALSE_START,
                    token_or_phrase=fsm.group(0),
                    char_offset=fsm.start(),
                    penalty=fs_pen,
                    description=f"False start/phonetic stutter '{fsm.group(0)}' detected.",
                )
            )

        # 4. Uncertainty phrases & epistemic hedging
        for rx, base_pen, desc in self.uncertainty_compiled:
            for um in rx.finditer(lower_text):
                total_penalty += base_pen
                signals.append(
                    HesitationSignal(
                        type=HesitationType.UNCERTAINTY_PHRASE,
                        token_or_phrase=um.group(0),
                        char_offset=um.start(),
                        penalty=base_pen,
                        description=f"{desc}: '{um.group(0)}'.",
                    )
                )

        # Compute normalized hesitation score (0-100)
        hesitation_score = max(10.0, min(100.0, round(100.0 - total_penalty, 1)))
        return signals, hesitation_score


class ContradictionDetector:
    """
    Identifies logical contradictions, self-negations, and conflicting claims:
    1. Within-turn narrative retractions (e.g. 'we used X... actually we didn't use X')
    2. Cross-turn state memory contradictions (e.g. claiming 5 yrs exp in Turn 1, 1 yr in Turn 3)
    """

    # Self-negation and verbal retraction phrases within a single turn
    RETRACTION_PHRASES = [
        (r"\b(actually (no|wait)|no wait|wait no)\b", "Verbal self-correction / retraction"),
        (r"\b(i mean not really|not really though)\b", "Minimizing retraction of previous assertion"),
        (r"\b(on second thought no|scratch that)\b", "Explicit claim invalidation"),
        (r"\b(let me take that back)\b", "Formal retraction"),
        (r"\b(to be honest i (lied|made that up|exaggerated))\b", "Direct integrity breach"),
    ]

    # Opposing semantic pair patterns within single sentence/turn
    SEMANTIC_OPPOSITION_PAIRS = [
        (r"\b(built|designed|implemented|handled)(\s+\w+){0,6}\s+(alone|by myself|single-handedly)\b",
         r"\b(team|colleagues|leads)(\s+\w+){0,4}\s+(built|handled|did|managed)(\s+\w+){0,3}\s+(most|all|everything)\b",
         "Ownership contradiction: Claimed solo authorship then attributed to team"),
        (r"\b(zero|no|never had any)\s+(downtime|outages?|failures?)\b",
         r"\b(went down|outage lasted|crashed for|offline for|downtime of)\b",
         "Reliability contradiction: Claimed zero outages then recounted server downtime"),
        (r"\b(expert|deeply experienced|mastered)\s+(in|with)?\b",
         r"\b(barely used|never touched|only read about|haven't really used)\b",
         "Skill contradiction: Claimed deep expertise then acknowledged lack of hands-on usage"),
    ]

    def __init__(self):
        self.retraction_compiled = [
            (re.compile(p, re.IGNORECASE), desc) for p, desc in self.RETRACTION_PHRASES
        ]
        self.opp_compiled = [
            (re.compile(p1, re.IGNORECASE), re.compile(p2, re.IGNORECASE), desc)
            for p1, p2, desc in self.SEMANTIC_OPPOSITION_PAIRS
        ]
        # Cross-turn memory store: session_id -> {claim_key: (claim_val, turn_idx, text)}
        self._claim_registry: Dict[str, Dict[str, Tuple[Any, int, str]]] = {}

    def analyze_contradictions(
        self,
        session_id: str,
        turn_index: int,
        text: str,
    ) -> Tuple[List[ContradictionIncident], float]:
        """
        Analyzes within-turn retractions and cross-turn factual reversals.
        Returns detected incidents and consistency score (0-100, 100=consistent).
        """
        incidents: List[ContradictionIncident] = []
        if not text or not text.strip():
            return incidents, 100.0

        lower_text = text.lower()

        # 1. Within-turn verbal retractions
        for rx, desc in self.retraction_compiled:
            m = rx.search(lower_text)
            if m:
                incidents.append(
                    ContradictionIncident(
                        severity=ContradictionSeverity.MILD_REVISION,
                        contradiction_type="SELF_CORRECTION_RETRACTION",
                        claim_a="Initial statement",
                        claim_b=m.group(0),
                        turn_b=turn_index,
                        confidence_deduction=12.0,
                        explanation=f"{desc}: Candidate hesitated and retracted statement with '{m.group(0)}'.",
                    )
                )

        # 2. Semantic opposition pairs within turn
        for rx1, rx2, desc in self.opp_compiled:
            m1 = rx1.search(lower_text)
            m2 = rx2.search(lower_text)
            if m1 and m2:
                incidents.append(
                    ContradictionIncident(
                        severity=ContradictionSeverity.DIRECT_CONTRADICTION,
                        contradiction_type="INTERNAL_NARRATIVE_OPPOSITION",
                        claim_a=m1.group(0),
                        claim_b=m2.group(0),
                        turn_b=turn_index,
                        confidence_deduction=25.0,
                        explanation=f"{desc}: '{m1.group(0)}' vs '{m2.group(0)}'.",
                    )
                )

        # 3. Cross-turn state memory tracking
        if session_id not in self._claim_registry:
            self._claim_registry[session_id] = {}
        registry = self._claim_registry[session_id]

        # Extract structured claims
        # A. Experience years claim
        exp_match = re.search(r"\b(\d+)\s*(?:\+)?\s*years?(?:\s*of)?\s*(?:experience|working)?\b", lower_text)
        if exp_match:
            years = int(exp_match.group(1))
            if "experience_years" in registry:
                prev_years, prev_turn, prev_str = registry["experience_years"]
                # Major discrepancy (e.g. claimed 6 years in turn 1, but says 1 year in turn 3)
                if abs(years - prev_years) >= 2 and prev_turn != turn_index:
                    incidents.append(
                        ContradictionIncident(
                            severity=ContradictionSeverity.CRITICAL_INCONSISTENCY,
                            contradiction_type="EXPERIENCE_TIMELINE_CLASH",
                            claim_a=f"{prev_years} years (Turn {prev_turn})",
                            claim_b=f"{years} years (Turn {turn_index})",
                            turn_a=prev_turn,
                            turn_b=turn_index,
                            confidence_deduction=35.0,
                            explanation=f"Candidate stated {prev_years} years experience in Turn {prev_turn}, but claimed {years} years in Turn {turn_index}.",
                        )
                    )
            else:
                registry["experience_years"] = (years, turn_index, exp_match.group(0))

        # B. Team responsibility: "I built it alone" vs later "I was just a junior contributor"
        if re.search(r"\b(built it (alone|myself)|sole (architect|engineer|developer))\b", lower_text):
            registry["ownership"] = ("solo", turn_index, "sole ownership claim")
        elif re.search(r"\b(only shadowed|just watched|did not code|was not involved)\b", lower_text):
            if "ownership" in registry:
                prev_own, prev_turn, prev_str = registry["ownership"]
                if prev_own == "solo" and prev_turn != turn_index:
                    incidents.append(
                        ContradictionIncident(
                            severity=ContradictionSeverity.DIRECT_CONTRADICTION,
                            contradiction_type="RESPONSIBILITY_RETRACTION",
                            claim_a=f"Claimed solo ownership in Turn {prev_turn}",
                            claim_b=f"Admitted minimal involvement in Turn {turn_index}",
                            turn_a=prev_turn,
                            turn_b=turn_index,
                            confidence_deduction=30.0,
                            explanation="Candidate previously claimed sole ownership but later stated they were not directly involved in coding.",
                        )
                    )

        # Compute consistency score
        total_deduction = sum(inc.confidence_deduction for inc in incidents)
        consistency_score = max(10.0, min(100.0, round(100.0 - total_deduction, 1)))
        return incidents, consistency_score


class StressIndicatorScorer:
    """
    Measures quantitative stress indicators:
    - Hesitation frequency per 100 words
    - Stutter and disfluency clustering
    - Negative and defensive sentiment spikes
    - Synthesizes 0-100 Stress Index and StressLevel
    """

    def measure_stress(
        self,
        word_count: int,
        hesitations: List[HesitationSignal],
        sentiment_score: float,
        contradictions: List[ContradictionIncident],
        response_time_seconds: float = 0.0,
    ) -> StressIndicators:
        words = max(1, word_count)
        hes_count = len(hesitations)

        # Hesitation frequency normalized per 100 words
        hes_freq_100w = round((hes_count / words) * 100.0, 1)

        # Cluster count: multiple repetitions or stutters
        repetition_clusters = sum(
            1 for h in hesitations if h.type in {HesitationType.REPEATED_WORD, HesitationType.FALSE_START}
        )

        anxiety_markers = [
            h.token_or_phrase for h in hesitations if h.type == HesitationType.UNCERTAINTY_PHRASE
        ]

        # Defensive or severe contradiction spikes
        defensive_spike = any(
            c.severity in {ContradictionSeverity.DIRECT_CONTRADICTION, ContradictionSeverity.CRITICAL_INCONSISTENCY}
            for c in contradictions
        ) or sentiment_score < 40.0

        # Stress Index Calculation (0.0=calm, 100.0=acute stress)
        # 1. Base from hesitation frequency (e.g. 5 hes per 100w = 25 pts)
        s_hes = min(40.0, hes_freq_100w * 5.0)

        # 2. Base from repetition clusters (stutters / broken words)
        s_clusters = min(25.0, repetition_clusters * 7.5)

        # 3. Latency stress (long freeze > 4s)
        s_latency = 0.0
        if response_time_seconds > 4.0:
            s_latency = min(20.0, (response_time_seconds - 4.0) * 4.0)

        # 4. Emotional distress from low composure
        s_sentiment = 0.0
        if sentiment_score < 65.0:
            s_sentiment = min(25.0, (65.0 - sentiment_score) * 0.7)

        # 5. Contradiction panic penalty
        s_contradiction = 20.0 if defensive_spike else 0.0

        raw_stress = s_hes + s_clusters + s_latency + s_sentiment + s_contradiction
        stress_index = round(max(0.0, min(100.0, raw_stress)), 1)

        # Categorize StressLevel
        if stress_index < 25.0:
            level = StressLevel.LOW
        elif stress_index < 55.0:
            level = StressLevel.MODERATE
        elif stress_index < 78.0:
            level = StressLevel.HIGH
        else:
            level = StressLevel.CRITICAL

        resilience = round(100.0 - stress_index, 1)

        return StressIndicators(
            stress_index=stress_index,
            stress_level=level,
            hesitation_frequency_per_100w=hes_freq_100w,
            repetition_cluster_count=repetition_clusters,
            defensive_spike_detected=defensive_spike,
            anxiety_markers=anxiety_markers[:6],
            stress_resilience_score=resilience,
        )


class ConfidenceAnalyzer:
    """
    Master Day 36 Confidence & Stress Indicators Analyzer.
    Coordinates HesitationPatternDetector, InterviewSentimentScorer,
    ContradictionDetector, and StressIndicatorScorer.
    """

    def __init__(self):
        self.hesitation_detector = HesitationPatternDetector()
        self.sentiment_scorer = InterviewSentimentScorer()
        self.contradiction_detector = ContradictionDetector()
        self.stress_scorer = StressIndicatorScorer()

    def evaluate_turn(
        self,
        turn_index: int,
        text: str,
        response_time_seconds: float = 0.0,
        session_id: str = "default_session",
    ) -> TurnConfidenceBreakdown:
        """
        Evaluates an individual candidate turn across all confidence and stress dimensions.
        """
        words = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", text or "")
        word_count = len(words)

        # 1. Hesitation patterns
        hesitations, s_hesitation = self.hesitation_detector.analyze_hesitations(
            text=text,
            response_time_seconds=response_time_seconds,
        )

        # 2. Sentiment and emotional composure
        sentiment_result = self.sentiment_scorer.analyze_sentiment(text)
        s_sentiment = sentiment_result.composure_score

        # 3. Contradiction patterns
        contradictions, s_consistency = self.contradiction_detector.analyze_contradictions(
            session_id=session_id,
            turn_index=turn_index,
            text=text,
        )

        # 4. Stress indicators
        stress_result = self.stress_scorer.measure_stress(
            word_count=word_count,
            hesitations=hesitations,
            sentiment_score=s_sentiment,
            contradictions=contradictions,
            response_time_seconds=response_time_seconds,
        )

        # 5. Composite Behavioral Confidence Score Calculation
        # Weights: Hesitation (35%), Consistency (25%), Sentiment Composure (25%), Stress Resilience (15%)
        raw_confidence = (
            0.35 * s_hesitation
            + 0.25 * s_consistency
            + 0.25 * s_sentiment
            + 0.15 * stress_result.stress_resilience_score
        )
        final_confidence = round(max(0.0, min(100.0, raw_confidence)), 1)

        # Tier assignment
        if final_confidence >= 85.0:
            tier = ConfidenceTier.AUTHORITATIVE
        elif final_confidence >= 70.0:
            tier = ConfidenceTier.COMPOSED
        elif final_confidence >= 50.0:
            tier = ConfidenceTier.HESITANT
        else:
            tier = ConfidenceTier.HIGH_STRESS

        # Generate recruiter insights
        strengths: List[str] = []
        risks: List[str] = []

        if s_hesitation >= 90.0:
            strengths.append("High verbal fluency with negligible hesitation pauses")
        if s_consistency >= 95.0:
            strengths.append("Rock-solid narrative consistency across claims")
        if sentiment_result.composure_score >= 88.0:
            strengths.append("Calm, constructive, and composed technical demeanor")
        if stress_result.stress_level == StressLevel.LOW:
            strengths.append("High psychological resilience and emotional stability under probing")

        if len(hesitations) >= 3:
            risks.append(f"Frequent hesitation signals ({len(hesitations)} incidents detected)")
        if contradictions:
            risks.append(f"Detected {len(contradictions)} logical inconsistency / retraction incidents")
        if sentiment_result.defensive_cues:
            risks.append("Defensive posture or pushback markers observed")
        if stress_result.stress_level in {StressLevel.HIGH, StressLevel.CRITICAL}:
            risks.append(f"Elevated stress index ({stress_result.stress_index}/100) under technical scrutiny")

        # Synthesis summary
        summary = (
            f"Candidate demonstrated {tier.value} confidence ({final_confidence}/100). "
            f"Stress index: {stress_result.stress_index} ({stress_result.stress_level.value}). "
            f"Sentiment: {sentiment_result.emotional_tone.value}."
        )

        return TurnConfidenceBreakdown(
            turn_index=turn_index,
            confidence_score=final_confidence,
            confidence_tier=tier,
            hesitation_score=s_hesitation,
            sentiment_score=s_sentiment,
            consistency_score=s_consistency,
            stress_index=stress_result.stress_index,
            hesitations=hesitations,
            sentiment=sentiment_result,
            contradictions=contradictions,
            stress=stress_result,
            behavioral_summary=summary,
            key_strengths=strengths,
            risk_flags=risks,
        )

    def aggregate_session(
        self,
        turn_breakdowns: List[TurnConfidenceBreakdown],
    ) -> SessionConfidenceSummary:
        """
        Consolidates multi-turn confidence breakdowns into an ATS-ready candidate summary.
        """
        if not turn_breakdowns:
            return SessionConfidenceSummary(
                average_confidence_score=75.0,
                overall_confidence_tier=ConfidenceTier.COMPOSED,
                average_stress_index=20.0,
                overall_stress_level=StressLevel.LOW,
                overall_hesitation_score=80.0,
                overall_consistency_score=100.0,
                dominant_emotional_tone=SentimentTone.MATTER_OF_FACT,
                total_hesitations_detected=0,
                total_contradictions_detected=0,
                recruiter_behavioral_summary="No completed turns to evaluate.",
            )

        n = len(turn_breakdowns)
        avg_conf = round(sum(t.confidence_score for t in turn_breakdowns) / n, 1)
        avg_stress = round(sum(t.stress_index for t in turn_breakdowns) / n, 1)
        avg_hes = round(sum(t.hesitation_score for t in turn_breakdowns) / n, 1)
        avg_cons = round(sum(t.consistency_score for t in turn_breakdowns) / n, 1)

        total_hes = sum(len(t.hesitations) for t in turn_breakdowns)
        total_contra = sum(len(t.contradictions) for t in turn_breakdowns)

        # Dominant tone
        tones = [t.sentiment.emotional_tone for t in turn_breakdowns]
        dominant_tone = max(set(tones), key=tones.count)

        if avg_conf >= 85.0:
            tier = ConfidenceTier.AUTHORITATIVE
        elif avg_conf >= 70.0:
            tier = ConfidenceTier.COMPOSED
        elif avg_conf >= 50.0:
            tier = ConfidenceTier.HESITANT
        else:
            tier = ConfidenceTier.HIGH_STRESS

        if avg_stress < 25.0:
            stress_level = StressLevel.LOW
        elif avg_stress < 55.0:
            stress_level = StressLevel.MODERATE
        elif avg_stress < 78.0:
            stress_level = StressLevel.HIGH
        else:
            stress_level = StressLevel.CRITICAL

        recruiter_summary = (
            f"Overall behavioral profile: {tier.value} confidence ({avg_conf}/100) with "
            f"{stress_level.value.lower()} stress index ({avg_stress}/100). "
            f"Candidate exhibited {dominant_tone.value.lower()} emotional disposition across {n} turns, "
            f"with {total_hes} hesitation signals and {total_contra} contradiction alerts."
        )

        return SessionConfidenceSummary(
            average_confidence_score=avg_conf,
            overall_confidence_tier=tier,
            average_stress_index=avg_stress,
            overall_stress_level=stress_level,
            overall_hesitation_score=avg_hes,
            overall_consistency_score=avg_cons,
            dominant_emotional_tone=dominant_tone,
            total_hesitations_detected=total_hes,
            total_contradictions_detected=total_contra,
            recruiter_behavioral_summary=recruiter_summary,
        )
