import re
from typing import List, Tuple, Optional, Dict, Any
from screening_ai.intent_models import CandidateIntent


CLARIFICATION_PATTERNS = [
    r"\bcan you repeat\b",
    r"\bcould you repeat\b",
    r"\bwhat do you mean\b",
    r"\bpardon\b",
    r"\bsorry (?:i )?didn'?t (?:hear|get|understand)\b",
    r"\bcome again\b",
    r"\bcan you rephrase\b",
    r"\bwhat was the question\b",
    r"\bwhat exactly\b",
    r"\bplease repeat\b",
    r"\b(?:can|could) you (?:clarify|explain)\b",
    r"\bcan you tell me more\b",
    r"\bcould you tell me more\b",
]

OFF_TOPIC_PATTERNS = [
    r"\bweather\b",
    r"\btell me a joke\b",
    r"\bwho made you\b",
    r"\bare you an ai\b",
    r"\bare you human\b",
    r"\bspeak to a human\b",
    r"\btransfer to (?:a )?recruiter\b",
    r"\bcricket\b",
    r"\bfootball\b",
    r"\bpolitics\b",
    r"\bmovie\b",
    r"\bstock market\b",
    r"\bcrypto\b",
    r"\bbitcoin\b",
    r"\bpizza\b",
    r"\brecip(?:e|es)\b",
]

VAGUE_PATTERNS = [
    r"\ba little bit of everything\b",
    r"\bit depends\b",
    r"\bdepends on (?:the )?(?:company|role|project)\b",
    r"\bas per company (?:norms|standards?)\b",
    r"\bas per industry (?:norms|standards?)\b",
    r"\bwhatever (?:is )?(?:fair|market|standard)\b",
    r"\bi know everything\b",
    r"\bi can do everything\b",
    r"\bnothing specific\b",
    r"\bnot sure\b",
    r"\bmaybe,?\s*maybe not\b",
    r"\bsomewhere around there\b",
    r"\bjust general stuff\b",
]

DECLINE_SKILL_PATTERNS = [
    r"\b(?:haven'?t|have not) (?:worked|used|coded|built)\b",
    r"\bno experience (?:in|with)\b",
    r"\bnever (?:used|worked with|touched)\b",
    r"\bdon'?t know\b",
    r"\bdo not know\b",
    r"\bnot familiar with\b",
    r"\bnot much exposure\b",
    r"\blittle to no (?:experience|exposure)\b",
    r"\bzero experience\b",
]

CONFIRM_SKILL_PATTERNS = [
    r"\bhands[- ]on experience\b",
    r"\bproficient (?:in|with)\b",
    r"\bexperienced (?:in|with)\b",
    r"\bworked (?:extensively|closely)? with\b",
    r"\bi use\b",
    r"\bexpert (?:in|with)\b",
    r"\bstrong knowledge\b",
    r"\bcore skill\b",
    r"\bprimary stack\b",
]

SALARY_PATTERNS = [
    r"\b(?:ctc|lpa|inr|salary|compensation|package|fixed|variable)\b",
    r"\b\d+(?:\.\d+)?\s*(?:lakhs?|lpa|lac|k|per annum)\b",
    r"\bcurrent(?:ly)? (?:earning|drawing|making)\b",
    r"\bexpect(?:ing|ation)?\b",
]

AVAILABILITY_PATTERNS = [
    r"\bnotice period\b",
    r"\bimmediate(?:ly)?\b",
    r"\bready to join\b",
    r"\b\d+\s*(?:days?|weeks?|months?)\b",
    r"\bserving notice\b",
    r"\bbuyout\b",
    r"\blst working day\b",
    r"\blast day\b",
]

EXPERIENCE_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*(?:years?|yrs?)\b",
    r"\btotal experience\b",
    r"\bworked as\b",
    r"\bmy role (?:was|is)\b",
    r"\bsoftware engineer\b",
    r"\bdata scientist\b",
    r"\bdeveloper\b",
    r"\barchitect\b",
    r"\bresponsibilit(?:y|ies)\b",
    r"\bbuilt and deployed\b",
]


class CandidateIntentClassifier:
    """
    Day 25 Intent Classifier.
    Classifies candidate responses into communicative intent categories
    (e.g., providing experience, skill confirmation/decline, salary, availability,
    clarification query, off-topic deflection, or vague evasion).
    """

    def __init__(self):
        self.clarification_re = [re.compile(p, re.IGNORECASE) for p in CLARIFICATION_PATTERNS]
        self.off_topic_re = [re.compile(p, re.IGNORECASE) for p in OFF_TOPIC_PATTERNS]
        self.vague_re = [re.compile(p, re.IGNORECASE) for p in VAGUE_PATTERNS]
        self.decline_re = [re.compile(p, re.IGNORECASE) for p in DECLINE_SKILL_PATTERNS]
        self.confirm_re = [re.compile(p, re.IGNORECASE) for p in CONFIRM_SKILL_PATTERNS]
        self.salary_re = [re.compile(p, re.IGNORECASE) for p in SALARY_PATTERNS]
        self.avail_re = [re.compile(p, re.IGNORECASE) for p in AVAILABILITY_PATTERNS]
        self.exp_re = [re.compile(p, re.IGNORECASE) for p in EXPERIENCE_PATTERNS]

    def classify_intent(
        self,
        text: str,
        question_category: Optional[str] = None,
        question_prompt: Optional[str] = None,
    ) -> Tuple[CandidateIntent, float, List[CandidateIntent]]:
        """
        Classify the candidate utterance into primary intent, confidence, and secondary intents.
        """
        if not text or not text.strip():
            return CandidateIntent.VAGUE_ANSWER, 0.95, []

        s = text.strip()

        # 1. Check Clarification
        if any(pat.search(s) for pat in self.clarification_re):
            return CandidateIntent.ASKING_CLARIFICATION, 0.95, []

        # 2. Check Off-Topic Deflection
        if any(pat.search(s) for pat in self.off_topic_re):
            # Check if this isn't an explicit tech skill question mentioning that word
            is_relevant_tech = bool(question_prompt and any(w in question_prompt.lower() for w in ["crypto", "recipe"]))
            if not is_relevant_tech:
                return CandidateIntent.OFF_TOPIC, 0.92, []

        # 3. Check Vague / Evasive Response
        is_vague_match = any(pat.search(s) for pat in self.vague_re)
        # If text is extremely short and evasive
        words = s.split()
        if is_vague_match or (len(words) <= 3 and s.lower() in ["maybe", "depends", "not sure", "dunno", "nothing"]):
            return CandidateIntent.VAGUE_ANSWER, 0.88, []

        # 4. Check Skill Decline
        has_decline = any(pat.search(s) for pat in self.decline_re)
        if has_decline:
            return CandidateIntent.DECLINING_SKILL, 0.92, []

        # Detect domain candidate intents
        scores: Dict[CandidateIntent, float] = {
            CandidateIntent.STATING_SALARY: 0.0,
            CandidateIntent.STATING_AVAILABILITY: 0.0,
            CandidateIntent.PROVIDING_EXPERIENCE: 0.0,
            CandidateIntent.CONFIRMING_SKILL: 0.0,
        }

        for pat in self.salary_re:
            if pat.search(s):
                scores[CandidateIntent.STATING_SALARY] += 0.35

        for pat in self.avail_re:
            if pat.search(s):
                scores[CandidateIntent.STATING_AVAILABILITY] += 0.35

        for pat in self.exp_re:
            if pat.search(s):
                scores[CandidateIntent.PROVIDING_EXPERIENCE] += 0.30

        for pat in self.confirm_re:
            if pat.search(s):
                scores[CandidateIntent.CONFIRMING_SKILL] += 0.35

        # Incorporate Question Category Prior
        if question_category:
            q_cat = question_category.lower()
            if "salary" in q_cat or "compensation" in q_cat:
                scores[CandidateIntent.STATING_SALARY] += 0.25
            elif "notice" in q_cat or "availab" in q_cat:
                scores[CandidateIntent.STATING_AVAILABILITY] += 0.25
            elif "experience" in q_cat:
                scores[CandidateIntent.PROVIDING_EXPERIENCE] += 0.25
            elif "skill" in q_cat or "tech" in q_cat:
                scores[CandidateIntent.CONFIRMING_SKILL] += 0.25

        # Sort intents by score
        sorted_intents = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_intent, top_score = sorted_intents[0]

        # Check secondary intents
        secondary = [
            intent for intent, score in sorted_intents[1:]
            if score >= 0.30 and intent != top_intent
        ]

        if top_score >= 0.25:
            confidence = min(0.98, max(0.65, top_score + 0.35))
            return top_intent, round(confidence, 2), secondary

        # Polite acknowledgement fallback
        if len(words) <= 2 and s.lower() in ["yes", "yeah", "sure", "okay", "yup", "got it", "hello", "hi"]:
            return CandidateIntent.GENERAL_ACKNOWLEDGEMENT, 0.90, []

        # Default fallback
        return CandidateIntent.PROVIDING_EXPERIENCE, 0.60, []
