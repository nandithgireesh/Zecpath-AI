import re
from typing import List, Dict, Any, Tuple, Optional
from screening_ai.stt_models import (
    SpeechEdgeCaseType,
    SpeechEdgeCaseAnalysis,
    CleanTranscriptResult,
)

FILLER_PATTERNS = [
    r"\bum+\b",
    r"\buh+\b",
    r"\ber+\b",
    r"\bah+\b",
    r"\bhmm+\b",
    r"\byou know\b",
    r"\blike\b",
    r"\bactually\b",
    r"\bbasically\b",
    r"\bsort of\b",
    r"\bkind of\b",
    r"\bi mean\b",
    r"\bso yeah\b",
    r"\bwell\b",
    r"\bright\b",
    r"\byaar\b",
    r"\bna\b",
    r"\bmatlab\b",
    r"\btoh\b",
]

# Proper nouns and technical vocabulary that must retain strict canonical casing
CANONICAL_PROPER_NOUNS = {
    "python": "Python",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "fastapi": "FastAPI",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "git": "Git",
    "ci/cd": "CI/CD",
    "b.tech": "B.Tech",
    "btech": "B.Tech",
    "m.tech": "M.Tech",
    "mtech": "M.Tech",
    "bca": "BCA",
    "mca": "MCA",
    "ph.d": "Ph.D",
    "phd": "Ph.D",
    "bangalore": "Bangalore",
    "bengaluru": "Bengaluru",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "pune": "Pune",
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "zecpath": "Zecpath",
    "lpa": "LPA",
    "ctc": "CTC",
    "inr": "INR",
}


class CleanTranscriptProcessor:
    """
    Day 24 Clean Transcript Processor.
    Provides advanced text cleanup (filler words, smart punctuation, proper noun casing)
    and conversational edge-case handling (interrupted speech, partial answers, silence).
    """

    def __init__(self):
        self.filler_regexes = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]

    def remove_filler_words(self, text: str) -> Tuple[str, List[str]]:
        """Remove spoken disfluencies and conversational verbal fillers."""
        if not text:
            return "", []

        removed = []
        cleaned = text
        for pat in self.filler_regexes:
            matches = pat.findall(cleaned)
            if matches:
                removed.extend(matches)
                cleaned = pat.sub(" ", cleaned)

        # Collapse whitespace and dangling punctuation
        cleaned = re.sub(r"\s+([,.?!])", r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = re.sub(r"^[,.\s]+|[,.\s]+$", "", cleaned).strip()
        return cleaned, removed

    def correct_punctuation(self, text: str) -> str:
        """
        Correct sentence punctuation:
        - Capitalize sentence beginnings.
        - Infer question marks for interrogative phrases.
        - Ensure terminal punctuation.
        """
        if not text:
            return ""

        s = text.strip()
        if not s:
            return ""

        # Capitalize first character
        s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()

        # Check if sentence is an interrogative question
        question_starters = [
            r"\bcan\b", r"\bcould\b", r"\bwhat\b", r"\bwhen\b", r"\bwhere\b",
            r"\bwhy\b", r"\bwho\b", r"\bhow\b", r"\bis\b", r"\bare\b",
            r"\bdo\b", r"\bdoes\b", r"\bwould\b", r"\bmay\b"
        ]
        is_question = any(re.match(pattern, s, re.IGNORECASE) for pattern in question_starters)

        # Apply terminal punctuation if missing
        if not s.endswith((".", "?", "!", "--", "…")):
            s += "?" if is_question else "."

        # Fix spacing around internal commas
        s = re.sub(r"\s*,\s*", ", ", s)
        s = re.sub(r"\s+", " ", s).strip()

        return s

    def normalize_case(self, text: str) -> str:
        """
        Normalize casing:
        Lowercases general words while strictly preserving proper technical nouns
        (e.g., Python, TensorFlow, PyTorch, Docker, B.Tech, Bangalore, LPA).
        """
        if not text:
            return ""

        result = text
        for token_lower, canonical in CANONICAL_PROPER_NOUNS.items():
            pattern = re.compile(rf"\b{re.escape(token_lower)}\b", re.IGNORECASE)
            result = pattern.sub(canonical, result)

        return result

    def detect_interrupted_speech(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if candidate speech was interrupted mid-sentence
        (e.g. trailing hyphens '--', ellipsis '...', abrupt preposition/conjunction end).
        """
        if not text:
            return False, None

        s = text.strip()

        # Explicit trailing cutoff markers
        if s.endswith("--") or s.endswith("-") or s.endswith("...") or s.endswith("…"):
            return True, "I noticed you were cut off there. Please take your time and complete your thought."

        # Cut off on dangling conjunctions or prepositions
        trailing_dangling = re.search(r"\b(?:and|but|or|because|so|that|with|in|at|to|for|my previous)\s*$", s, re.IGNORECASE)
        if trailing_dangling:
            return True, "It sounds like you were about to say more. Please feel free to complete your sentence."

        # Cut off on trailing word fragments like "work-"
        if re.search(r"\b\w+-\s*$", s):
            return True, "I noticed a brief interruption in the audio. Could you finish what you were saying?"

        return False, None

    def detect_partial_answer(self, category: str, text: str) -> Tuple[bool, List[str], Optional[str]]:
        """
        Detect if candidate provided only a partial answer to a category probe.
        Identifies missing parameter slots and produces a targeted follow-up prompt.
        """
        if not text:
            return True, ["complete_response"], "Could you please provide your response to the question?"

        lower = text.lower()
        missing = []
        follow_up = None

        cat_norm = category.lower()

        if "salary" in cat_norm:
            # Check if expected CTC number is present
            has_num = bool(re.search(r"\b\d+(?:\.\d+)?\b", lower))
            if not has_num:
                missing.append("expected_ctc_lpa")
                follow_up = "Could you please share your expected CTC in terms of LPA (Lakhs Per Annum)?"

        elif "notice" in cat_norm:
            # Check if duration or immediate status is present
            has_duration = any(k in lower for k in ["day", "month", "week", "immediate", "ready", "zero"])
            has_num = bool(re.search(r"\b\d+\b", lower))
            if not (has_duration or has_num):
                missing.append("notice_period_duration")
                follow_up = "Could you specify your official notice period duration in days or months?"

        elif "experience" in cat_norm:
            # Check if total years is mentioned
            has_num = bool(re.search(r"\b\d+(?:\.\d+)?\b", lower))
            has_time = any(k in lower for k in ["year", "yr", "month"])
            if not (has_num and has_time):
                missing.append("total_experience_years")
                follow_up = "Could you clarify how many total years of relevant professional experience you have?"

        elif "location" in cat_norm:
            # Check if relocation willingness or city is stated
            has_loc_status = any(k in lower for k in ["relocate", "open to", "remote", "bangalore", "hyderabad", "yes", "no"])
            if not has_loc_status:
                missing.append("relocation_preference")
                follow_up = "Are you open to relocating to our office locations, or are you strictly seeking remote work?"

        return bool(missing), missing, follow_up

    def detect_silence(self, text: str, silence_duration_sec: float = 0.0) -> Tuple[bool, Optional[str]]:
        """
        Detect candidate silence (> 3.0 seconds) or empty transcribed speech.
        """
        is_empty = not text or not text.strip()
        is_long_silence = silence_duration_sec >= 3.0

        if is_empty or is_long_silence:
            return True, "I didn't hear a response from you. Are you still with me on the call?"

        return False, None

    def process_transcript(
        self,
        raw_text: str,
        category: str = "General",
        silence_duration_sec: float = 0.0,
    ) -> CleanTranscriptResult:
        """
        Comprehensive text cleanup and edge-case evaluation pipeline:
        1. Silence detection
        2. Interrupted speech detection
        3. Filler word removal
        4. Punctuation correction
        5. Proper noun casing normalization
        6. Partial answer detection
        """
        # 1. Silence check
        is_silence, silence_prompt = self.detect_silence(raw_text, silence_duration_sec)
        if is_silence:
            return CleanTranscriptResult(
                original_text=raw_text or "",
                cleaned_text="",
                removed_fillers=[],
                punctuation_corrected=False,
                proper_case_applied=False,
                edge_case_analysis=SpeechEdgeCaseAnalysis(
                    edge_case=SpeechEdgeCaseType.SILENCE_DETECTED,
                    is_silence=True,
                    recovery_prompt=silence_prompt,
                ),
            )

        # 2. Interrupted speech check
        is_interrupted, interrupt_prompt = self.detect_interrupted_speech(raw_text)

        # 3. Filler removal
        no_fillers, removed_fillers = self.remove_filler_words(raw_text)

        # 4. Punctuation correction
        punctuated = self.correct_punctuation(no_fillers)

        # 5. Case normalization for technical proper nouns
        cased = self.normalize_case(punctuated)

        # 6. Partial answer check
        is_partial, missing_slots, partial_prompt = self.detect_partial_answer(category, cased)

        # Determine dominant edge case
        edge_case = SpeechEdgeCaseType.NORMAL
        recovery_prompt = None

        if is_interrupted:
            edge_case = SpeechEdgeCaseType.INTERRUPTED_SPEECH
            recovery_prompt = interrupt_prompt
        elif is_partial:
            edge_case = SpeechEdgeCaseType.PARTIAL_ANSWER
            recovery_prompt = partial_prompt

        analysis = SpeechEdgeCaseAnalysis(
            edge_case=edge_case,
            is_interrupted=is_interrupted,
            is_partial=is_partial,
            is_silence=False,
            missing_required_entities=missing_slots,
            recovery_prompt=recovery_prompt,
        )

        return CleanTranscriptResult(
            original_text=raw_text,
            cleaned_text=cased,
            removed_fillers=removed_fillers,
            punctuation_corrected=True,
            proper_case_applied=True,
            edge_case_analysis=analysis,
        )
