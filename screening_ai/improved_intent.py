"""
Day 30 - Improved Intent Detection Model
=========================================
Context-aware, composite-utterance capable candidate intent classifier that eliminates
misclassifications on terse technical responses, nuanced compensation ranges, notice
buyouts, and conversational preambles.
"""

import re
from typing import List, Tuple, Optional, Dict, Any

from screening_ai.intent_models import CandidateIntent
from screening_ai.intent_classifier import (
    CandidateIntentClassifier,
)

TECH_TERSE_KEYWORDS = [
    r"\bkafka\b", r"\brabbitmq\b", r"\bredis\b", r"\bkubernetes\b", r"\bk8s\b",
    r"\bdocker\b", r"\bpostgresql\b", r"\bmysql\b", r"\bmongodb\b", r"\baws\b",
    r"\bgcp\b", r"\bazure\b", r"\bpython\b", r"\bjava\b", r"\bgolang\b",
    r"\breact\b", r"\bnode\b", r"\bcelery\b", r"\bfastapi\b", r"\bdjango\b",
    r"\bhelm\b", r"\bterraform\b", r"\bci/cd\b", r"\bgrpc\b", r"\brest\b",
    r"\bgraphql\b", r"\belasticsearch\b", r"\bindex(?:es|ing)?\b", r"\bsharding\b",
    r"\braft\b", r"\bsaga\b", r"\bconsensus\b", r"\bconcurrency\b", r"\block(?:ing)?\b",
    r"\bcache\b", r"\bcaching\b", r"\bmicroservices?\b", r"\bevent[- ]driven\b",
    r"\bquery\b", r"\bqueries\b", r"\b(?:table\s+joins?|sql\s+joins?|nested\s+joins?|database\s+joins?)\b",
    r"\bapi\b", r"\bpipeline\b", r"\bargocd\b", r"\bgithub actions\b", r"\bzustand\b",
    r"\bredux\b", r"\breact query\b", r"\btanstack\b"
]


class OptimizedIntentClassifier:
    """
    Day 30 - Enhanced Intent Classifier.
    Adds:
    - Contextual category weighting.
    - Terse answer rescue (domain terms prevent false vague classifications on brief text).
    - Multi-intent / composite utterance extraction.
    - Robust salary and availability regex patterns (supporting ranges, buyouts, and spoken numerals).
    """

    def __init__(self):
        self.base_classifier = CandidateIntentClassifier()
        self.tech_re = [re.compile(p, re.IGNORECASE) for p in TECH_TERSE_KEYWORDS]

        # Enhanced patterns for salary ranges and negotiability
        self.enhanced_salary_re = re.compile(
            r"\b(?:\d+(?:\.\d+)?\s*(?:to|-)\s*\d+(?:\.\d+)?\s*(?:lpa|lakhs?|lac|k)|\d+(?:\.\d+)?\s*(?:lpa|lakhs?|lac|k)|(?:ten|twelve|fifteen|sixteen|eighteen|twenty|twenty-two|twenty-four|twenty-six|twenty-eight|thirty|thirty-two|thirty-four|forty|forty-eight|fifty)\s*(?:lpa|lakhs?|lac|k|per annum)|ctc|negotiable|inr|compensation|salary|package)\b",
            re.IGNORECASE,
        )

        # Enhanced patterns for notice periods and buyouts
        self.enhanced_avail_re = re.compile(
            r"\b(?:\d+\s*(?:days?|weeks?|months?)|(?:fifteen|thirty|forty-five|sixty|ninety)\s*(?:days?|weeks?|months?)|immediate(?:ly)?|ready to join|can join in|serving notice|buyout|official notice|notice period|notice duration)\b",
            re.IGNORECASE,
        )

        # Disambiguation: "Let me clarify..." is NOT asking clarification
        self.clarify_statement_re = re.compile(
            r"\b(?:let me (?:clarify|explain)|to clarify|just to clarify|what i meant was)\b",
            re.IGNORECASE,
        )

    def classify_intent(
        self,
        text: str,
        question_category: Optional[str] = None,
        question_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[CandidateIntent, float, List[CandidateIntent]]:
        """
        Classifies candidate response with contextual disambiguation.
        Returns (primary_intent, confidence, secondary_intents).
        """
        if not text or not text.strip():
            return CandidateIntent.VAGUE_ANSWER, 0.95, []

        s = text.strip()
        words = s.split()

        # 1. Disambiguate Clarification
        # If candidate says "Let me clarify, we used Redis..." -> not ASKING_CLARIFICATION
        is_clarify_statement = bool(self.clarify_statement_re.search(s))
        if not is_clarify_statement:
            if any(pat.search(s) for pat in self.base_classifier.clarification_re):
                return CandidateIntent.ASKING_CLARIFICATION, 0.96, []

        # 2. Check Off-Topic Deflection (Respecting technical terms)
        if any(pat.search(s) for pat in self.base_classifier.off_topic_re):
            is_relevant = bool(
                question_prompt and any(w in question_prompt.lower() for w in ["crypto", "bitcoin", "recipe"])
            )
            if not is_relevant:
                return CandidateIntent.OFF_TOPIC, 0.94, []

        # 3. Check Skill Decline
        if any(pat.search(s) for pat in self.base_classifier.decline_re):
            return CandidateIntent.DECLINING_SKILL, 0.92, []

        # 4. Check Terse Technical Rescue (ONLY for short responses without vague markers or other domain cues)
        has_tech_keyword = any(pat.search(s) for pat in self.tech_re)
        is_vague_match = any(pat.search(s) for pat in self.base_classifier.vague_re)

        # If it's truly vague without tech rescue:
        if is_vague_match or (len(words) <= 3 and s.lower() in ["maybe", "depends", "not sure", "dunno", "nothing", "whatever"]):
            return CandidateIntent.VAGUE_ANSWER, 0.90, []

        is_salary_cue = bool(self.enhanced_salary_re.search(s) or any(pat.search(s) for pat in self.base_classifier.salary_re))
        is_avail_cue = bool(self.enhanced_avail_re.search(s) or any(pat.search(s) for pat in self.base_classifier.avail_re))

        # If text is very short (< 15 words) and contains pure technical terms without salary or availability
        if len(words) < 15 and has_tech_keyword and not is_salary_cue and not is_avail_cue:
            return CandidateIntent.CONFIRMING_SKILL, 0.92, []

        # 5. Multiclass Scoring with Context Priors
        scores: Dict[CandidateIntent, float] = {
            CandidateIntent.STATING_SALARY: 0.0,
            CandidateIntent.STATING_AVAILABILITY: 0.0,
            CandidateIntent.CONFIRMING_SKILL: 0.0,
            CandidateIntent.PROVIDING_EXPERIENCE: 0.0,
        }

        # Salary cues
        if is_salary_cue:
            scores[CandidateIntent.STATING_SALARY] += 0.50
            if self.enhanced_salary_re.search(s):
                scores[CandidateIntent.STATING_SALARY] += 0.20

        # Availability cues
        if is_avail_cue:
            scores[CandidateIntent.STATING_AVAILABILITY] += 0.50
            if self.enhanced_avail_re.search(s):
                scores[CandidateIntent.STATING_AVAILABILITY] += 0.20

        # Skill cues
        if has_tech_keyword:
            scores[CandidateIntent.CONFIRMING_SKILL] += 0.40
        for pat in self.base_classifier.confirm_re:
            if pat.search(s):
                scores[CandidateIntent.CONFIRMING_SKILL] += 0.30

        # Experience cues
        for pat in self.base_classifier.exp_re:
            if pat.search(s):
                scores[CandidateIntent.PROVIDING_EXPERIENCE] += 0.35

        # Incorporate Question Context Prior
        if question_category:
            q_cat = question_category.lower()
            if "salary" in q_cat or "compensation" in q_cat:
                scores[CandidateIntent.STATING_SALARY] += 0.30
            elif "notice" in q_cat or "availab" in q_cat:
                scores[CandidateIntent.STATING_AVAILABILITY] += 0.30
            elif "skill" in q_cat or "tech" in q_cat:
                scores[CandidateIntent.CONFIRMING_SKILL] += 0.30
            elif "experience" in q_cat:
                scores[CandidateIntent.PROVIDING_EXPERIENCE] += 0.30

        # Sort intents by score
        sorted_intents = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_intent, top_score = sorted_intents[0]

        # Extract secondary intents if score is significant (>= 0.35)
        secondary: List[CandidateIntent] = [
            intent for intent, score in sorted_intents[1:]
            if score >= 0.35 and intent != top_intent
        ]

        if top_score >= 0.25:
            confidence = min(0.98, max(0.68, top_score + 0.30))
            return top_intent, round(confidence, 2), secondary

        # Polite acknowledgement fallback
        if len(words) <= 3 and s.lower() in [
            "yes", "yeah", "sure", "okay", "yup", "got it", "hello", "hi", "sure thing"
        ]:
            return CandidateIntent.GENERAL_ACKNOWLEDGEMENT, 0.90, []

        return CandidateIntent.PROVIDING_EXPERIENCE, 0.65, []
