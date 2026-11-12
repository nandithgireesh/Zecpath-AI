"""
Day 36 Deliverable 2: Sentiment Scoring Engine
=============================================
Specialized interview sentiment analysis engine measuring candidate:
1. Constructive optimism vs defeatist mindset
2. Emotional composure & poise under technical questioning
3. Defensive, reluctant, or evasive posturing
4. Quantitative compound polarity (-1.0 to +1.0) and 0-100 composure score
"""

import re
from typing import List, Dict, Tuple, Optional
from interview_ai.confidence_models import (
    SentimentPolarity,
    SentimentTone,
    SentimentTurnScore,
)


class InterviewSentimentScorer:
    """
    Evaluates emotional tone, professional disposition, and emotional stability
    from candidate interview transcripts.
    """

    # 1. Professional enthusiasm, ownership, and achievement lexicons
    POSITIVE_WORDS = {
        "excited", "thrilled", "passion", "passionate", "love", "loved", "enjoy",
        "enjoyed", "eager", "delighted", "successfully", "successful", "achieved",
        "improved", "optimized", "delivered", "excelled", "proud", "collaborative",
        "teamwork", "pleasure", "gladly", "happy", "great", "rewarding", "enthusiastic",
        "strengths", "best", "fantastic", "opportunity", "growth", "learn", "learning",
        "innovative", "initiative", "ownership", "solved", "streamlined", "impact",
        "resilient", "thrived", "effective", "efficient", "dedication", "accomplished"
    }

    POSITIVE_PHRASES = [
        r"\b(looking forward to)\b",
        r"\b(happy to (help|explain|discuss|elaborate|share))\b",
        r"\b(proud of (the|our|what))\b",
        r"\b(great (experience|opportunity|team|challenge))\b",
        r"\b(really enjoyed (working|building|solving))\b",
        r"\b(took the initiative)\b",
        r"\b(took full ownership)\b",
        r"\b(turned (it|things) around)\b",
        r"\b(passion for (software|engineering|coding|problem))\b",
    ]

    # 2. Defeatist, overwhelmed, or dissatisfied lexicons
    NEGATIVE_WORDS = {
        "hate", "hated", "annoying", "annoyed", "frustrated", "frustrating", "terrible",
        "horrible", "toxic", "awful", "pointless", "conflict", "disaster", "struggled",
        "failed", "blame", "fault", "unreasonable", "exhausting", "waste", "boring",
        "unfair", "mess", "problematic", "disappointed", "poor", "bad", "hopeless",
        "helpless", "impossible", "chaos", "nightmare", "stuck", "overwhelmed"
    }

    NEGATIVE_PHRASES = [
        r"\b(waste of time)\b",
        r"\b(couldn't stand)\b",
        r"\b(bad experience)\b",
        r"\b(not my fault)\b",
        r"\b(forced to)\b",
        r"\b(had no choice)\b",
        r"\b(everyone gave up)\b",
        r"\b(nobody helped (me)?)\b",
        r"\b(management had no clue)\b",
        r"\b(completely overwhelmed)\b",
    ]

    # 3. Defensive, evasive, or reluctant markers
    DEFENSIVE_PATTERNS = [
        r"\b(none of your business)\b",
        r"\b(not your (business|concern))\b",
        r"\b(why do you (need to know|ask))\b",
        r"\b(why are you asking (me )?that)\b",
        r"\b(already told you)\b",
        r"\b(as i already said)\b",
        r"\b(i refuse to (say|answer|disclose))\b",
        r"\b(that's? (private|confidential|none of your))\b",
        r"\b(won't answer)\b",
        r"\b(do i really have to answer)\b",
        r"\b(that's? a stupid question)\b",
        r"\b(you wouldn't understand)\b",
    ]

    RELUCTANT_PATTERNS = [
        r"\b(if i really have to)\b",
        r"\b(i guess if you insist)\b",
        r"\b(reluctant to)\b",
        r"\b(rather not say)\b",
        r"\b(not really comfortable sharing)\b",
    ]

    # 4. Anxiety and insecurity markers
    ANXIETY_PATTERNS = [
        r"\b(i'm really nervous)\b",
        r"\b(my mind just went blank)\b",
        r"\b(sorry i'm messing this up)\b",
        r"\b(i don't think i'm good enough)\b",
        r"\b(i'm terrible at interviews)\b",
        r"\b(please don't judge me)\b",
        r"\[laughs? nervously\]",
        r"\[sighs? heavily\]",
    ]

    def __init__(self):
        # Precompile regexes for optimal high-throughput scoring
        self.pos_regexes = [re.compile(p, re.IGNORECASE) for p in self.POSITIVE_PHRASES]
        self.neg_regexes = [re.compile(p, re.IGNORECASE) for p in self.NEGATIVE_PHRASES]
        self.def_regexes = [re.compile(p, re.IGNORECASE) for p in self.DEFENSIVE_PATTERNS]
        self.reluctant_regexes = [re.compile(p, re.IGNORECASE) for p in self.RELUCTANT_PATTERNS]
        self.anxiety_regexes = [re.compile(p, re.IGNORECASE) for p in self.ANXIETY_PATTERNS]

    def analyze_sentiment(self, text: str) -> SentimentTurnScore:
        """
        Analyzes spoken candidate response text and computes sentiment polarity,
        compound score (-1.0 to 1.0), and emotional composure.
        """
        if not text or not text.strip():
            return SentimentTurnScore(
                polarity=SentimentPolarity.NEUTRAL,
                compound_score=0.0,
                positive_score=0.0,
                neutral_score=1.0,
                negative_score=0.0,
                composure_score=80.0,
                emotional_tone=SentimentTone.MATTER_OF_FACT,
                positive_cues=[],
                negative_cues=[],
                defensive_cues=[],
            )

        lower_text = text.lower()
        words = re.findall(r"\b[a-zA-Z]{2,}\b", lower_text)
        total_words = max(1, len(words))

        positive_cues: List[str] = []
        negative_cues: List[str] = []
        defensive_cues: List[str] = []
        anxiety_cues: List[str] = []

        # 1. Match individual words
        for w in words:
            if w in self.POSITIVE_WORDS:
                positive_cues.append(w)
            elif w in self.NEGATIVE_WORDS:
                negative_cues.append(w)

        # 2. Match multi-word phrases
        for rx in self.pos_regexes:
            for m in rx.finditer(lower_text):
                positive_cues.append(m.group(0))

        for rx in self.neg_regexes:
            for m in rx.finditer(lower_text):
                negative_cues.append(m.group(0))

        for rx in self.def_regexes:
            for m in rx.finditer(lower_text):
                defensive_cues.append(m.group(0))

        for rx in self.reluctant_regexes:
            for m in rx.finditer(lower_text):
                defensive_cues.append(f"reluctant: {m.group(0)}")

        for rx in self.anxiety_regexes:
            for m in rx.finditer(lower_text):
                anxiety_cues.append(m.group(0))

        # Weight scoring
        pos_count = len(positive_cues)
        neg_count = len(negative_cues)
        def_count = len(defensive_cues)
        anx_count = len(anxiety_cues)

        # Compute raw weights
        w_pos = pos_count * 1.5
        w_neg = neg_count * 1.8 + def_count * 3.0 + anx_count * 2.0
        w_total = w_pos + w_neg + (total_words * 0.25)

        pos_prob = min(1.0, round(w_pos / w_total, 3))
        neg_prob = min(1.0, round(w_neg / w_total, 3))
        neu_prob = max(0.0, round(1.0 - (pos_prob + neg_prob), 3))

        # Compound score calculation (-1.0 to +1.0)
        compound = round(pos_prob - neg_prob, 3)

        # Classify high-level polarity
        if compound >= 0.15:
            polarity = SentimentPolarity.POSITIVE
        elif compound <= -0.15:
            polarity = SentimentPolarity.NEGATIVE
        else:
            polarity = SentimentPolarity.NEUTRAL

        # Composure Score (0 to 100)
        # Base starts at 85 (neutral calm professional)
        composure = 85.0 + (pos_prob * 15.0) - (neg_prob * 35.0) - (def_count * 18.0) - (anx_count * 12.0)
        composure = round(max(0.0, min(100.0, composure)), 1)

        # Determine fine-grained professional emotional tone
        if def_count > 0:
            tone = SentimentTone.DEFENSIVE_GUARDED
        elif anx_count > 0 or composure < 50.0:
            tone = SentimentTone.ANXIOUS_HESITANT
        elif neg_count >= 2 and compound < -0.3:
            tone = SentimentTone.FRUSTRATED
        elif pos_count >= 3 or compound >= 0.40:
            tone = SentimentTone.ENTHUSIASTIC
        elif pos_count >= 1 or compound > 0.10:
            tone = SentimentTone.COMPOSED_OPTIMISTIC
        else:
            tone = SentimentTone.MATTER_OF_FACT

        return SentimentTurnScore(
            polarity=polarity,
            compound_score=compound,
            positive_score=pos_prob,
            neutral_score=neu_prob,
            negative_score=neg_prob,
            composure_score=composure,
            emotional_tone=tone,
            positive_cues=list(set(positive_cues))[:8],
            negative_cues=list(set(negative_cues))[:8],
            defensive_cues=list(set(defensive_cues))[:8],
        )
