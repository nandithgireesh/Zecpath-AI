"""
Day 27: Sentiment Scoring Module
================================
Evaluates spoken candidate answers for:
1. Positive / neutral / negative sentiment polarity
2. Compound polarity score (-1.0 to +1.0)
3. Defensive, reluctant, or hostile behavioral demeanor
4. Candidate engagement level and emotional tone synthesis
"""

import re
from typing import List, Dict, Tuple, Optional
from screening_ai.behavioral_models import (
    SentimentPolarity,
    EngagementLevel,
    SentimentAnalysisResult,
)


class SentimentScorer:
    """
    Analyzes emotional tone, professional disposition, and sentiment polarity
    of candidate transcripts during screening calls.
    """

    # Positive and enthusiastic lexicons
    POSITIVE_WORDS = {
        "excited", "thrilled", "passion", "passionate", "love", "loved", "enjoy",
        "enjoyed", "eager", "delighted", "successfully", "successful", "achieved",
        "improved", "optimized", "delivered", "excelled", "proud", "collaborative",
        "teamwork", "pleasure", "gladly", "happy", "great", "rewarding", "enthusiastic",
        "strengths", "best", "fantastic", "opportunity", "growth", "learn", "learning"
    }

    POSITIVE_PHRASES = [
        r"\b(looking forward to)\b",
        r"\b(happy to (help|explain|discuss|elaborate))\b",
        r"\b(proud of)\b",
        r"\b(great (experience|opportunity|team))\b",
        r"\b(really enjoyed)\b",
    ]

    # Negative and dissatisfied lexicons
    NEGATIVE_WORDS = {
        "hate", "hated", "annoying", "annoyed", "frustrated", "frustrating", "terrible",
        "horrible", "toxic", "awful", "pointless", "conflict", "disaster", "struggled",
        "failed", "blame", "fault", "unreasonable", "exhausting", "waste", "boring",
        "unfair", "mess", "problematic", "disappointed", "poor", "bad"
    }

    NEGATIVE_PHRASES = [
        r"\b(waste of time)\b",
        r"\b(couldn't stand)\b",
        r"\b(bad experience)\b",
        r"\b(not my fault)\b",
        r"\b(forced to)\b",
    ]

    # Explicit defensive or reluctant markers
    DEFENSIVE_PATTERNS = [
        r"\b(none of your business)\b",
        r"\b(not your (business|concern))\b",
        r"\b(why do you (need to know|ask))\b",
        r"\b(why are you asking (me )?that)\b",
        r"\b(already told you)\b",
        r"\b(i refuse to (say|answer|disclose))\b",
        r"\b(that's? (private|confidential|none of your))\b",
        r"\b(won't answer)\b",
        r"\b(do i have to answer)\b",
    ]

    RELUCTANT_PATTERNS = [
        r"\b(if i really have to)\b",
        r"\b(i guess if you insist)\b",
        r"\b(reluctant to)\b",
        r"\b(rather not say)\b",
    ]

    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> SentimentAnalysisResult:
        """
        Computes sentiment polarity, compound score (-1.0 to 1.0),
        and classifies candidate engagement and emotional tone.
        """
        if not text or not text.strip():
            return SentimentAnalysisResult(
                polarity=SentimentPolarity.NEUTRAL,
                compound_score=0.0,
                positive_score=0.0,
                neutral_score=1.0,
                negative_score=0.0,
                engagement_level=EngagementLevel.PASSIVE,
                positive_keywords=[],
                negative_keywords=[],
                defensive_keywords=[],
                emotional_tone="Neutral / No content",
            )

        lower_text = text.lower()
        words = re.findall(r"\b[a-zA-Z]{2,}\b", lower_text)
        total_words = max(1, len(words))

        # Check defensive language first
        defensive_found = []
        for pat in self.DEFENSIVE_PATTERNS:
            match = re.search(pat, lower_text)
            if match:
                defensive_found.append(match.group(0))

        reluctant_found = []
        for pat in self.RELUCTANT_PATTERNS:
            match = re.search(pat, lower_text)
            if match:
                reluctant_found.append(match.group(0))

        # Collect positive and negative words
        pos_found = [w for w in words if w in self.POSITIVE_WORDS]
        neg_found = [w for w in words if w in self.NEGATIVE_WORDS]

        # Check multi-word phrases
        for pat in self.POSITIVE_PHRASES:
            match = re.search(pat, lower_text)
            if match:
                pos_found.append(match.group(0))

        for pat in self.NEGATIVE_PHRASES:
            match = re.search(pat, lower_text)
            if match:
                neg_found.append(match.group(0))

        # Remove duplicate keywords while preserving order
        pos_unique = list(dict.fromkeys(pos_found))
        neg_unique = list(dict.fromkeys(neg_found))

        # Scoring calculations
        pos_weight = len(pos_found) * 1.5
        neg_weight = len(neg_found) * 1.8

        # Compound formula: normalized ratio clamped between -1.0 and +1.0
        raw_diff = pos_weight - neg_weight
        if defensive_found:
            raw_diff -= 4.0

        compound = raw_diff / (abs(raw_diff) + 4.0) if raw_diff != 0 else 0.0
        compound = round(max(-1.0, min(1.0, compound)), 3)

        # Proportions
        pos_score = min(1.0, round(len(pos_found) / max(4, total_words), 2))
        neg_score = min(1.0, round((len(neg_found) + (2 if defensive_found else 0)) / max(4, total_words), 2))
        neutral_score = max(0.0, round(1.0 - pos_score - neg_score, 2))

        # Classify polarity & engagement
        if defensive_found:
            polarity = SentimentPolarity.DEFENSIVE
            engagement = EngagementLevel.DEFENSIVE
            tone = "Defensive and guarded"
        elif reluctant_found:
            polarity = SentimentPolarity.NEGATIVE
            engagement = EngagementLevel.RELUCTANT
            tone = "Reluctant and hesitant"
        elif compound >= 0.45:
            polarity = SentimentPolarity.VERY_POSITIVE
            engagement = EngagementLevel.HIGHLY_ENGAGED
            tone = "Enthusiastic and highly collaborative"
        elif compound >= 0.15:
            polarity = SentimentPolarity.POSITIVE
            engagement = EngagementLevel.COOPERATIVE
            tone = "Positive and constructive"
        elif compound <= -0.15:
            polarity = SentimentPolarity.NEGATIVE
            engagement = EngagementLevel.PASSIVE
            tone = "Critical or dissatisfied"
        else:
            polarity = SentimentPolarity.NEUTRAL
            if total_words < 5:
                engagement = EngagementLevel.PASSIVE
                tone = "Terse and passive"
            else:
                engagement = EngagementLevel.COOPERATIVE
                tone = "Professional and matter-of-fact"

        return SentimentAnalysisResult(
            polarity=polarity,
            compound_score=compound,
            positive_score=pos_score,
            neutral_score=neutral_score,
            negative_score=neg_score,
            engagement_level=engagement,
            positive_keywords=pos_unique[:5],
            negative_keywords=neg_unique[:5],
            defensive_keywords=defensive_found[:3],
            emotional_tone=tone,
        )
