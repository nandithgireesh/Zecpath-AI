import re
from typing import List, Dict, Any, Tuple, Optional
from screening_ai.transcript_models import (
    TranscriptTurn,
    QuestionInteractionRecord,
    ExtractedEntities,
    VoiceTranscriptPayload,
    NormalizedScreeningData,
    NormalizationResult,
    ConfidenceLevel,
)

FILLER_WORDS = [
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
]

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100"
}

KNOWN_SKILLS = [
    "python", "tensorflow", "pytorch", "machine learning", "deep learning",
    "keras", "scikit-learn", "nlp", "pandas", "numpy", "fastapi", "docker",
    "kubernetes", "aws", "react", "node.js", "nodejs", "mongodb", "express",
    "javascript", "typescript", "sql", "postgresql", "git", "ci/cd"
]


class TranscriptNormalizer:
    """
    Day 23 Speech Transcript Normalization Engine.
    Converts noisy, colloquial speech-to-text outputs into cleaned, standardized, AI-ready data.
    """

    def __init__(self, confidence_threshold: float = 0.70):
        self.confidence_threshold = confidence_threshold
        self.filler_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in FILLER_WORDS]

    def clean_text(self, raw_text: str) -> str:
        """Basic text cleanup: whitespace collapse, trim."""
        if not raw_text:
            return ""
        cleaned = re.sub(r"\s+", " ", raw_text).strip()
        return cleaned

    def remove_filler_words(self, text: str) -> Tuple[str, List[str]]:
        """Identify and remove verbal fillers and conversational disfluencies."""
        if not text:
            return "", []

        removed = []
        cleaned = text
        for pattern in self.filler_patterns:
            matches = pattern.findall(cleaned)
            if matches:
                removed.extend(matches)
                cleaned = pattern.sub(" ", cleaned)

        # Collapse spaces and clean leftover punctuation
        cleaned = re.sub(r"\s+([,.?!])", r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Remove leading/trailing commas or dots
        cleaned = re.sub(r"^[,.\s]+|[,.\s]+$", "", cleaned).strip()
        return cleaned, removed

    def normalize_number_words(self, text: str) -> str:
        """Convert spoken number words (e.g., 'three', 'two and a half') to numeric tokens."""
        if not text:
            return ""

        res = text
        # Replace fractions / spoken fractions
        res = re.sub(r"\btwo and a half\b", "2.5", res, flags=re.IGNORECASE)
        res = re.sub(r"\bthree and a half\b", "3.5", res, flags=re.IGNORECASE)
        res = re.sub(r"\bone and a half\b", "1.5", res, flags=re.IGNORECASE)
        res = re.sub(r"\bhalf\b", "0.5", res, flags=re.IGNORECASE)

        # Replace standard single number words
        for word, digit in NUMBER_WORDS.items():
            pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
            res = pattern.sub(digit, res)

        return res

    def normalize_experience(self, text: str) -> Optional[float]:
        """Extract and normalize years of experience from spoken utterance."""
        if not text:
            return None

        # Convert words to numbers first
        s = self.normalize_number_words(text)

        # Look for explicit patterns like: "3.5 years", "3 yrs", "4 years of experience"
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?)", s, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass

        # Year range like "2021 to 2024"
        m_range = re.search(r"(20\d\d)\s*(?:to|-|till|until)\s*(20\d\d|present|current)", s, re.IGNORECASE)
        if m_range:
            start_yr = int(m_range.group(1))
            end_str = m_range.group(2).lower()
            end_yr = 2026 if "present" in end_str or "current" in end_str else int(end_str)
            diff = max(0.0, float(end_yr - start_yr))
            return diff

        return None

    def normalize_notice_period(self, text: str) -> Tuple[Optional[int], bool]:
        """
        Normalize notice period expressions into days integer and immediate flag.
        Returns: (notice_period_days, is_immediate_joiner)
        """
        if not text:
            return None, False

        s = self.normalize_number_words(text.lower())

        # Check immediate joiner using word boundaries
        immediate_pattern = r"\b(?:immediate(?:ly)?|ready immediately|available immediately|zero\s*days?|0\s*days?)\b"
        if re.search(immediate_pattern, s):
            return 0, True

        # Check explicit days: "60 days", "15 days"
        m_days = re.search(r"(\d+)\s*(?:days?|day)", s)
        if m_days:
            return int(m_days.group(1)), False

        # Check months: "1 month", "2 months", "3 months"
        m_months = re.search(r"(\d+(?:\.\d+)?)\s*(?:months?|month)", s)
        if m_months:
            months = float(m_months.group(1))
            return int(round(months * 30)), False

        # Check weeks: "2 weeks"
        m_weeks = re.search(r"(\d+)\s*(?:weeks?|week)", s)
        if m_weeks:
            return int(m_weeks.group(1)) * 7, False

        return None, False

    def normalize_salary(self, text: str) -> Tuple[Optional[float], bool]:
        """
        Normalize CTC / salary expressions into float (LPA) and negotiation flag.
        Returns: (ctc_lpa, is_negotiable)
        """
        if not text:
            return None, False

        s = self.normalize_number_words(text.lower())

        is_negotiable = any(k in s for k in ["negotiable", "flexible", "open to discuss", "open for discussion"])

        # Check patterns like "12 LPA", "12.5 lakhs", "14 lac", "15,00,000"
        m_lpa = re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac|lakh)", s)
        if m_lpa:
            return float(m_lpa.group(1)), is_negotiable

        # Absolute INR numbers like 1200000 or 12,00,000
        clean_nums = re.sub(r"[,]", "", s)
        m_abs = re.search(r"\b(\d{6,8})\b", clean_nums)
        if m_abs:
            val = float(m_abs.group(1))
            val_lpa = round(val / 100000.0, 2)
            return val_lpa, is_negotiable

        # Bare number if in context of salary
        m_bare = re.search(r"\b(\d+(?:\.\d+)?)\b", s)
        if m_bare:
            val = float(m_bare.group(1))
            if 1.0 <= val <= 100.0:  # Sensible LPA range
                return val, is_negotiable

        return None, is_negotiable

    def extract_skills_mentioned(self, text: str) -> List[str]:
        """Identify verified technical skills mentioned in the candidate utterance."""
        if not text:
            return []

        lower = text.lower()
        found = []
        for skill in KNOWN_SKILLS:
            # Word boundary search
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, lower):
                found.append(skill)
        return found

    def evaluate_confidence(self, confidence: float) -> Tuple[ConfidenceLevel, bool]:
        """Map numeric confidence to standard enum and flag low confidence utterances."""
        if confidence >= 0.85:
            return ConfidenceLevel.HIGH, False
        elif confidence >= 0.70:
            return ConfidenceLevel.MEDIUM, False
        elif confidence >= 0.50:
            return ConfidenceLevel.LOW, True
        else:
            return ConfidenceLevel.CRITICAL_LOW, True

    def normalize_utterance(self, raw_text: str, confidence: float = 0.9) -> NormalizationResult:
        """Full normalization pipeline for a single speech utterance."""
        cleaned = self.clean_text(raw_text)
        no_fillers, removed_fillers = self.remove_filler_words(cleaned)
        normalized_text = self.normalize_number_words(no_fillers)

        conf_level, is_low = self.evaluate_confidence(confidence)

        # Extract entities
        exp = self.normalize_experience(normalized_text)
        notice_days, is_imm = self.normalize_notice_period(normalized_text)
        ctc, is_neg = self.normalize_salary(normalized_text)
        skills = self.extract_skills_mentioned(normalized_text)

        entities: Dict[str, Any] = {}
        if exp is not None:
            entities["experience_years"] = exp
        if notice_days is not None:
            entities["notice_period_days"] = notice_days
            entities["is_immediate_joiner"] = is_imm
        if ctc is not None:
            entities["ctc_lpa"] = ctc
            entities["ctc_negotiable"] = is_neg
        if skills:
            entities["skills"] = skills

        return NormalizationResult(
            raw_text=raw_text,
            cleaned_text=normalized_text,
            removed_fillers=removed_fillers,
            normalized_entities=entities,
            confidence=confidence,
            confidence_level=conf_level,
            is_low_confidence=is_low,
        )

    def normalize_full_transcript(self, payload: VoiceTranscriptPayload) -> NormalizedScreeningData:
        """
        Processes all turns and question interactions in a voice transcript session,
        producing a clean, structured, AI-ready screening data object.
        """
        all_cleaned_turns = []
        low_confidence_count = 0
        total_confidence = 0.0

        for turn in payload.turns:
            norm_res = self.normalize_utterance(turn.raw_text, turn.confidence)
            turn.normalized_text = norm_res.cleaned_text
            turn.is_low_confidence = norm_res.is_low_confidence
            if norm_res.is_low_confidence:
                low_confidence_count += 1
            total_confidence += turn.confidence

            speaker_tag = "Recruiter Bot" if turn.speaker.value == "BOT" else "Candidate"
            all_cleaned_turns.append(f"{speaker_tag}: {norm_res.cleaned_text}")

        # Process question interactions and build extracted profile
        profile = ExtractedEntities()
        category_evals: Dict[str, Any] = {}

        for qi in payload.question_interactions:
            norm_res = self.normalize_utterance(qi.response_raw, qi.confidence)
            qi.response_normalized = norm_res.cleaned_text

            category = qi.category
            cat_entities = qi.extracted_entities

            if "experience" in category.lower():
                exp = self.normalize_experience(norm_res.cleaned_text)
                if exp is not None:
                    cat_entities.experience_years = exp
                    profile.experience_years = exp

            elif "skills" in category.lower():
                skills = self.extract_skills_mentioned(norm_res.cleaned_text)
                if skills:
                    cat_entities.skills_confirmed = skills
                    profile.skills_confirmed = list(set(profile.skills_confirmed + skills))

            elif "notice" in category.lower():
                days, imm = self.normalize_notice_period(norm_res.cleaned_text)
                if days is not None:
                    cat_entities.notice_period_days = days
                    cat_entities.is_immediate_joiner = imm
                    profile.notice_period_days = days
                    profile.is_immediate_joiner = imm

            elif "salary" in category.lower():
                ctc, neg = self.normalize_salary(norm_res.cleaned_text)
                if ctc is not None:
                    cat_entities.expected_ctc_lpa = ctc
                    cat_entities.ctc_negotiable = neg
                    profile.expected_ctc_lpa = ctc
                    profile.ctc_negotiable = neg

            elif "location" in category.lower():
                txt_lower = norm_res.cleaned_text.lower()
                reloc = any(k in txt_lower for k in ["relocate", "willing", "open to", "yes"])
                remote = any(k in txt_lower for k in ["remote", "wfh", "work from home"])
                cat_entities.relocation_willingness = reloc
                cat_entities.remote_preferred = remote
                profile.relocation_willingness = reloc
                profile.remote_preferred = remote

            elif "education" in category.lower():
                cat_entities.highest_degree = norm_res.cleaned_text
                profile.highest_degree = norm_res.cleaned_text

            category_evals[category] = {
                "question_id": qi.question_id,
                "raw_response": qi.response_raw,
                "normalized_response": norm_res.cleaned_text,
                "confidence": qi.confidence,
                "validation_status": qi.validation_status,
                "entities": cat_entities.model_dump() if hasattr(cat_entities, "model_dump") else cat_entities.dict(),
            }

        avg_conf = total_confidence / max(1, len(payload.turns))

        return NormalizedScreeningData(
            session_id=payload.session_id,
            candidate_id=payload.metadata.candidate_id,
            candidate_name=payload.metadata.candidate_name or "Candidate",
            job_id=payload.metadata.job_id,
            role_name=payload.metadata.role_name or "General Role",
            overall_audio_quality={
                "avg_confidence": round(avg_conf, 3),
                "low_confidence_turn_count": low_confidence_count,
                "has_auditory_clarity_issues": low_confidence_count > (len(payload.turns) * 0.3),
            },
            extracted_profile=profile,
            category_evaluations=category_evals,
            readiness_for_scoring=True,
            full_normalized_dialogue="\n".join(all_cleaned_turns),
        )
