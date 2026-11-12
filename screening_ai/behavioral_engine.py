"""
Day 27: Behavioral Indicators Engine & Signal Aggregator
========================================================
Combines Confidence Analysis and Sentiment Scoring into:
1. Communication Strength Indicators (Fluency, Assertiveness, Engagement, Pacing, Articulation)
2. Per-turn behavioral analysis
3. Comprehensive multi-turn BehavioralIndicatorsReport with green/red flags and recruiter probes.
"""

from typing import List, Dict, Any, Optional
from screening_ai.behavioral_models import (
    HesitationType,
    PaceRating,
    SentimentPolarity,
    EngagementLevel,
    CommunicationGrade,
    CommunicationStrengthIndicator,
    TurnBehavioralAnalysis,
    BehavioralIndicatorsReport,
)
from screening_ai.confidence_analyzer import ConfidenceAnalyzer
from screening_ai.sentiment_scorer import SentimentScorer


class BehavioralIndicatorsEngine:
    """
    End-to-end analyzer assessing candidate communication quality,
    vocal confidence, sentiment signals, and behavioral indicators.
    """

    def __init__(
        self,
        confidence_analyzer: Optional[ConfidenceAnalyzer] = None,
        sentiment_scorer: Optional[SentimentScorer] = None,
    ):
        self.confidence_analyzer = confidence_analyzer or ConfidenceAnalyzer()
        self.sentiment_scorer = sentiment_scorer or SentimentScorer()

    def calculate_communication_indicators(
        self,
        confidence_metrics: Any,
        sentiment_result: Any,
    ) -> CommunicationStrengthIndicator:
        """
        Computes 5 communication pillars: Fluency, Assertiveness, Engagement, Pacing, Articulation.
        """
        # 1. Fluency: based on lack of hesitations, fillers, and stutters
        fluency = max(10.0, 100.0 - (confidence_metrics.total_hesitation_penalty * 1.8))
        fluency = min(100.0, round(fluency, 1))

        # 2. Assertiveness: based on directness and absence of hedging
        assertiveness = max(10.0, 100.0 - confidence_metrics.uncertainty.uncertainty_score)
        assertiveness = min(100.0, round(assertiveness, 1))

        # 3. Engagement: based on sentiment and tone
        if sentiment_result.polarity == SentimentPolarity.DEFENSIVE:
            engagement = 25.0
        elif sentiment_result.engagement_level == EngagementLevel.HIGHLY_ENGAGED:
            engagement = 98.0
        elif sentiment_result.engagement_level == EngagementLevel.COOPERATIVE:
            engagement = 85.0
        elif sentiment_result.engagement_level == EngagementLevel.PASSIVE:
            engagement = 65.0
        elif sentiment_result.engagement_level == EngagementLevel.RELUCTANT:
            engagement = 45.0
        else:
            engagement = 75.0

        # Adjust engagement by compound sentiment score
        engagement = max(10.0, min(100.0, round(engagement + (sentiment_result.compound_score * 10.0), 1)))

        # 4. Pacing: from pace metrics
        pacing = confidence_metrics.pace_metrics.pacing_score

        # 5. Articulation: combining length sufficiency and clarity
        word_count = confidence_metrics.pace_metrics.word_count
        if word_count < 5:
            articulation_penalty = 30.0
        elif word_count < 10:
            articulation_penalty = 15.0
        else:
            articulation_penalty = 0.0

        articulation = max(15.0, min(100.0, round(fluency * 0.6 + pacing * 0.4 - articulation_penalty, 1)))

        # Overall weighted strength
        overall = (
            fluency * 0.25
            + assertiveness * 0.25
            + engagement * 0.20
            + pacing * 0.15
            + articulation * 0.15
        )
        overall = max(10.0, min(100.0, round(overall, 1)))

        if overall >= 85.0:
            grade = CommunicationGrade.EXCELLENT
            summary = "Articulate, highly fluent, and assertive communication style."
        elif overall >= 72.0:
            grade = CommunicationGrade.GOOD
            summary = "Clear and constructive communication with good conversational rhythm."
        elif overall >= 60.0:
            grade = CommunicationGrade.ACCEPTABLE
            summary = "Adequate communication with noticeable hesitation or occasional hedging."
        else:
            grade = CommunicationGrade.NEEDS_IMPROVEMENT
            summary = "Substantial communication gaps: low fluency, heavy hedging, or defensive tone."

        return CommunicationStrengthIndicator(
            fluency_score=fluency,
            assertiveness_score=assertiveness,
            engagement_score=engagement,
            pacing_score=pacing,
            articulation_score=articulation,
            overall_strength_score=overall,
            grade=grade,
            summary=summary,
        )

    def analyze_turn(
        self,
        turn_id: str,
        raw_text: str,
        duration_seconds: Optional[float] = None,
        latency_ms: Optional[int] = None,
        stt_acoustic_confidence: Optional[float] = None,
        word_confidences: Optional[List[Dict[str, Any]]] = None,
    ) -> TurnBehavioralAnalysis:
        """
        Analyzes confidence, pacing, sentiment, and communication indicators for a single turn.
        """
        confidence_metrics = self.confidence_analyzer.evaluate_turn_confidence(
            raw_text=raw_text,
            duration_seconds=duration_seconds,
            latency_ms=latency_ms,
            stt_acoustic_confidence=stt_acoustic_confidence,
            word_confidences=word_confidences,
        )

        sentiment_result = self.sentiment_scorer.analyze_sentiment(raw_text)

        communication_indicators = self.calculate_communication_indicators(
            confidence_metrics=confidence_metrics,
            sentiment_result=sentiment_result,
        )

        # Generate observations
        obs = []
        if confidence_metrics.final_confidence_score >= 85.0:
            obs.append("High vocal and conversational confidence.")
        elif confidence_metrics.final_confidence_score < 60.0:
            obs.append(f"Low confidence tier ({confidence_metrics.final_confidence_score}/100).")

        if confidence_metrics.total_hesitation_penalty > 10.0:
            obs.append(f"Notable hesitation markers detected (-{confidence_metrics.total_hesitation_penalty} pts).")

        if confidence_metrics.uncertainty.hedging_count > 0:
            hedges_str = ", ".join(confidence_metrics.uncertainty.hedging_phrases[:3])
            obs.append(f"Uncertainty / hedging observed: {hedges_str}.")

        if sentiment_result.polarity == SentimentPolarity.DEFENSIVE:
            obs.append("Defensive or guarded language detected.")
        elif sentiment_result.polarity == SentimentPolarity.VERY_POSITIVE:
            obs.append("Enthusiastic and proactive responses.")

        if confidence_metrics.pace_metrics.pace_rating == PaceRating.VERY_SLOW:
            obs.append(f"Pacing is very slow ({confidence_metrics.pace_metrics.wpm} WPM).")
        elif confidence_metrics.pace_metrics.pace_rating == PaceRating.RUSHED:
            obs.append(f"Pacing is rushed ({confidence_metrics.pace_metrics.wpm} WPM).")

        return TurnBehavioralAnalysis(
            turn_id=turn_id,
            speaker="CANDIDATE",
            raw_text=raw_text,
            confidence_metrics=confidence_metrics,
            sentiment=sentiment_result,
            communication_indicators=communication_indicators,
            key_observations=obs,
        )

    def analyze_session(
        self,
        candidate_id: str,
        session_id: str,
        turns: List[Dict[str, Any]],
    ) -> BehavioralIndicatorsReport:
        """
        Aggregates multi-turn responses into a comprehensive behavioral report for recruiters.
        """
        turn_analyses: List[TurnBehavioralAnalysis] = []

        total_confidence = 0.0
        total_compound_sentiment = 0.0
        total_wpm = 0.0
        total_fluency = 0.0
        total_assertiveness = 0.0
        total_engagement = 0.0
        total_pacing = 0.0
        total_articulation = 0.0
        total_overall_strength = 0.0

        green_flags: List[str] = []
        red_flags: List[str] = []
        interviewer_probes: List[str] = []

        candidate_turns = [t for t in turns if t.get("speaker", "CANDIDATE").upper() == "CANDIDATE"]
        if not candidate_turns:
            candidate_turns = turns  # fallback

        for idx, t in enumerate(candidate_turns, 1):
            t_id = t.get("turn_id", f"TURN_{idx:02d}")
            raw_text = t.get("raw_text") or t.get("response_raw") or t.get("text") or ""
            duration = t.get("duration_seconds")
            if duration is None and "start_time_ms" in t and "end_time_ms" in t:
                duration = (t["end_time_ms"] - t["start_time_ms"]) / 1000.0

            latency = t.get("latency_ms")
            stt_conf = t.get("confidence")
            word_confs = t.get("word_confidences")

            analysis = self.analyze_turn(
                turn_id=t_id,
                raw_text=raw_text,
                duration_seconds=duration,
                latency_ms=latency,
                stt_acoustic_confidence=stt_conf,
                word_confidences=word_confs,
            )
            turn_analyses.append(analysis)

            # Accumulate
            total_confidence += analysis.confidence_metrics.final_confidence_score
            total_compound_sentiment += analysis.sentiment.compound_score
            total_wpm += analysis.confidence_metrics.pace_metrics.wpm
            ci = analysis.communication_indicators
            total_fluency += ci.fluency_score
            total_assertiveness += ci.assertiveness_score
            total_engagement += ci.engagement_score
            total_pacing += ci.pacing_score
            total_articulation += ci.articulation_score
            total_overall_strength += ci.overall_strength_score

            # Collect flags
            if analysis.confidence_metrics.final_confidence_score >= 88.0 and ci.fluency_score >= 90.0:
                flag = f"[{t_id}] Highly articulate and confident delivery."
                if flag not in green_flags:
                    green_flags.append(flag)

            if analysis.sentiment.polarity == SentimentPolarity.VERY_POSITIVE:
                flag = f"[{t_id}] High enthusiasm and collaborative demeanor."
                if flag not in green_flags:
                    green_flags.append(flag)

            if analysis.sentiment.polarity == SentimentPolarity.DEFENSIVE:
                flag = f"[{t_id}] Defensive demeanor detected on topic: '{raw_text[:60]}...'."
                if flag not in red_flags:
                    red_flags.append(flag)
                interviewer_probes.append(f"Probe candidate receptiveness and team collaboration: answer was defensive in {t_id}.")

            if analysis.confidence_metrics.uncertainty.hedging_count >= 2:
                hedges = ", ".join(analysis.confidence_metrics.uncertainty.hedging_phrases)
                flag = f"[{t_id}] Notable uncertainty/hedging on statements: {hedges}."
                if flag not in red_flags:
                    red_flags.append(flag)
                interviewer_probes.append(f"Validate candidate depth in next round regarding claims in {t_id} due to tentative phrasing ({hedges}).")

            if analysis.confidence_metrics.total_hesitation_penalty >= 20.0:
                flag = f"[{t_id}] Excessive verbal disfluencies and vocal fillers."
                if flag not in red_flags:
                    red_flags.append(flag)

        n = max(1, len(turn_analyses))
        avg_confidence = round(total_confidence / n, 1)
        avg_sentiment = round(total_compound_sentiment / n, 3)
        avg_wpm = round(total_wpm / n, 1)

        avg_fluency = round(total_fluency / n, 1)
        avg_assertiveness = round(total_assertiveness / n, 1)
        avg_engagement = round(total_engagement / n, 1)
        avg_pacing = round(total_pacing / n, 1)
        avg_articulation = round(total_articulation / n, 1)
        avg_overall_strength = round(total_overall_strength / n, 1)

        # Average pace rating
        if avg_wpm < 100:
            overall_pace = PaceRating.VERY_SLOW
        elif avg_wpm < 120:
            overall_pace = PaceRating.SLOW
        elif avg_wpm <= 165:
            overall_pace = PaceRating.OPTIMAL
        elif avg_wpm <= 185:
            overall_pace = PaceRating.FAST
        else:
            overall_pace = PaceRating.RUSHED

        # Average sentiment polarity
        if avg_sentiment >= 0.4:
            overall_polarity = SentimentPolarity.VERY_POSITIVE
        elif avg_sentiment >= 0.1:
            overall_polarity = SentimentPolarity.POSITIVE
        elif avg_sentiment <= -0.2:
            overall_polarity = SentimentPolarity.NEGATIVE
        else:
            overall_polarity = SentimentPolarity.NEUTRAL

        if any(a.sentiment.polarity == SentimentPolarity.DEFENSIVE for a in turn_analyses):
            overall_polarity = SentimentPolarity.DEFENSIVE

        # Overall grade
        if avg_overall_strength >= 85.0:
            overall_grade = CommunicationGrade.EXCELLENT
            grade_summary = "Candidate demonstrates superior communication strengths, strong vocal confidence, and articulate pacing."
        elif avg_overall_strength >= 72.0:
            overall_grade = CommunicationGrade.GOOD
            grade_summary = "Candidate demonstrates clear and constructive communication with steady conversational flow."
        elif avg_overall_strength >= 60.0:
            grade_summary = "Candidate communication is acceptable but exhibits noticeable hesitation, uncertainty, or pacing variations."
            overall_grade = CommunicationGrade.ACCEPTABLE
        else:
            overall_grade = CommunicationGrade.NEEDS_IMPROVEMENT
            grade_summary = "Candidate exhibits significant communication deficiencies: low confidence, excessive fillers, or defensive tone."

        overall_indicators = CommunicationStrengthIndicator(
            fluency_score=avg_fluency,
            assertiveness_score=avg_assertiveness,
            engagement_score=avg_engagement,
            pacing_score=avg_pacing,
            articulation_score=avg_articulation,
            overall_strength_score=avg_overall_strength,
            grade=overall_grade,
            summary=grade_summary,
        )

        # Executive summary
        exec_summary = (
            f"Candidate {candidate_id} achieved an overall vocal confidence score of {avg_confidence}/100 "
            f"and a communication strength rating of {avg_overall_strength}/100 ({overall_grade.value}). "
            f"Average conversational pace was {avg_wpm} WPM ({overall_pace.value}) with an overall "
            f"{overall_polarity.value.lower()} emotional disposition. "
            f"{'No major behavioral risks identified.' if not red_flags else f'Flagged {len(red_flags)} behavioral observation(s) requiring next-round attention.'}"
        )

        # Add general green flag if none was specific
        if not green_flags and avg_overall_strength >= 70.0:
            green_flags.append(f"Maintained steady conversational pace ({avg_wpm} WPM) throughout the screening call.")

        return BehavioralIndicatorsReport(
            candidate_id=candidate_id,
            session_id=session_id,
            total_turns_analyzed=len(turn_analyses),
            overall_confidence_score=avg_confidence,
            overall_sentiment=overall_polarity,
            average_compound_sentiment=avg_sentiment,
            average_wpm=avg_wpm,
            overall_pace_rating=overall_pace,
            communication_indicators=overall_indicators,
            behavioral_green_flags=green_flags[:5],
            behavioral_red_flags=red_flags[:5],
            recruiter_executive_summary=exec_summary,
            recommended_interviewer_probes=interviewer_probes[:4],
            turn_breakdowns=turn_analyses,
        )
