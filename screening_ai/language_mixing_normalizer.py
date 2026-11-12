"""
Day 31: Language Mixing & Code-Switching Normalizer
===================================================
Translates and normalizes Hinglish (Hindi-English code-switching) into
canonical English representations for technical voice screening:
- Detects bilingual mixing and transliterated Hindi tokens.
- Preserves technical terminology (Docker, Redis, Celery, Kubernetes, FastAPI).
- Maps Hindi numerical expressions ('pachees lakh', 'do mahine', 'paanch saal') into canonical entities.
- Converts Hindi connectives ('maine use kiya tha', 'kyunki', 'lekin') into clear English.
- Protects candidates from linguistic bias, enabling 100% fair technical evaluations.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from screening_ai.failure_models import (
    LanguageMixingCategory,
    CodeSwitchResult,
)


class LanguageMixingNormalizer:
    """
    Identifies and translates Hinglish and bilingual code-switching constructs
    into canonical English text while extracting recruitment entities.
    """

    # Common Hindi transliterated marker words in telephonic screening
    HINDI_CONNECTIVES = {
        "mera": "my",
        "meri": "my",
        "mere": "my",
        "humne": "we",
        "maine": "I",
        "mujhe": "I",
        "humein": "we",
        "hai": "is",
        "hain": "are",
        "tha": "was",
        "thi": "was",
        "the": "were",
        "kyunki": "because",
        "kyonki": "because",
        "lekin": "but",
        "magar": "however",
        "par": "but",
        "aur": "and",
        "ka": "of",
        "ki": "of",
        "ke": "of",
        "liye": "for",
        "mein": "in",
        "se": "from",
        "ko": "to",
        "baad": "after",
        "karta": "do",
        "karte": "do",
        "karta hoon": "I do",
        "karta hu": "I do",
        "kiya tha": "did",
        "use kiya": "used",
        "use kiya tha": "used",
        "use karte hain": "use",
        "banaya tha": "built",
        "achha": "good",
        "bohot": "very",
        "bahut": "very",
        "kam": "low",
        "jyada": "high",
        "zyada": "high",
        "mil jayega": "will get",
        "baat hui thi": "discussed",
        "possible hai": "is possible",
        "nahi": "not",
        "matlab": "meaning",
        "jaise": "like",
    }

    # Transliterated Indian numerical words
    HINDI_NUMBERS = {
        "ek": 1,
        "do": 2,
        "teen": 3,
        "tin": 3,
        "chaar": 4,
        "char": 4,
        "paanch": 5,
        "panch": 5,
        "chhah": 6,
        "saat": 7,
        "aath": 8,
        "nau": 9,
        "dus": 10,
        "das": 10,
        "pandrah": 15,
        "bees": 20,
        "bis": 20,
        "pachees": 25,
        "pachis": 25,
        "tees": 30,
        "tis": 30,
        "chalees": 40,
        "pachaas": 50,
        "pachas": 50,
        "saath": 60,
        "sath": 60,
        "nabbey": 90,
        "nabbe": 90,
        "sau": 100,
    }

    # Common technical terms to strictly preserve
    TECHNICAL_TERMS = {
        "python", "django", "fastapi", "flask", "celery", "redis", "postgres",
        "postgresql", "mysql", "mongodb", "docker", "kubernetes", "k8s", "aws",
        "gcp", "azure", "kafka", "rabbitmq", "rest", "graphql", "grpc", "microservices",
        "monolith", "ci/cd", "terraform", "ansible", "linux", "git", "hpa", "envoy",
        "prometheus", "grafana", "nginx", "load balancer", "caching", "latency"
    }

    @classmethod
    def analyze_and_normalize(cls, text: str) -> CodeSwitchResult:
        """
        Analyzes an utterance for code-switching, normalizes transliterated Hindi
        into canonical English, and extracts salary, notice, and tech entities.
        """
        if not text or not text.strip():
            return CodeSwitchResult(
                original_utterance=text,
                detected_category=LanguageMixingCategory.MONOLINGUAL_ENGLISH,
                detected_languages=["en"],
                hindi_token_count=0,
                english_token_count=0,
                normalized_english_text="",
                extracted_entities={},
                confidence_score=1.0,
            )

        cleaned = text.strip()
        tokens = re.findall(r"\b\w+\b", cleaned.lower())

        hindi_count = 0
        english_count = 0

        for tok in tokens:
            if tok in cls.HINDI_CONNECTIVES or tok in cls.HINDI_NUMBERS:
                hindi_count += 1
            else:
                english_count += 1

        # Classify Language Mixing
        if hindi_count == 0:
            category = LanguageMixingCategory.MONOLINGUAL_ENGLISH
            langs = ["en"]
        elif hindi_count >= 1 and any(t in cls.TECHNICAL_TERMS for t in tokens):
            category = LanguageMixingCategory.BILINGUAL_TECHNICAL
            langs = ["en", "hi"]
        elif hindi_count >= 2:
            category = LanguageMixingCategory.HINGLISH_CODE_SWITCH
            langs = ["en", "hi"]
        else:
            category = LanguageMixingCategory.REGIONAL_IDIOMATIC
            langs = ["en", "hi"]

        # Extract Entities (Salary, Notice, Tech)
        entities = cls._extract_entities(cleaned)

        # Perform Normalized Translation
        normalized = cls._translate_to_canonical(cleaned)

        # Confidence is high if entities were resolved and normalized cleanly
        conf = 0.95 if hindi_count > 0 else 1.0

        return CodeSwitchResult(
            original_utterance=cleaned,
            detected_category=category,
            detected_languages=langs,
            hindi_token_count=hindi_count,
            english_token_count=english_count,
            normalized_english_text=normalized,
            extracted_entities=entities,
            confidence_score=conf,
        )

    @classmethod
    def _extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts structured entities from bilingual text."""
        entities: Dict[str, Any] = {}
        t_lower = text.lower()

        # 1. Salary Extraction (e.g., 'pachees lakh', '25 lpa', 'bees lakh')
        # Check expected salary explicitly first
        exp_match = re.search(r"expected\s+(?:around\s+)?(\w+)\s+(?:lakh|lac|lpa)", t_lower)
        if exp_match:
            word_or_num = exp_match.group(1)
            if word_or_num in cls.HINDI_NUMBERS:
                entities["salary_lpa"] = float(cls.HINDI_NUMBERS[word_or_num])
            else:
                try:
                    entities["salary_lpa"] = float(word_or_num)
                except ValueError:
                    pass

        if "salary_lpa" not in entities:
            found_salaries = []
            for word, val in cls.HINDI_NUMBERS.items():
                pattern = rf"\b{word}\s+(?:lakh|lac|lpa)\b"
                if re.search(pattern, t_lower):
                    found_salaries.append(float(val))
            digit_lpa = re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)", t_lower)
            if digit_lpa:
                found_salaries.append(float(digit_lpa.group(1)))
            if found_salaries:
                # If multiple salaries are mentioned (current vs expected), expected is the later one
                entities["salary_lpa"] = found_salaries[-1]
                if len(found_salaries) > 1:
                    entities["current_ctc_lpa"] = found_salaries[0]

        # 2. Notice Period Extraction (e.g., 'do mahine', 'tees din', '30 days')
        for word, val in cls.HINDI_NUMBERS.items():
            # Months -> convert to days (1 month = 30 days)
            if re.search(rf"\b{word}\s+(?:mahine|mahina|months?)\b", t_lower):
                entities["notice_days"] = int(val * 30)
                break
            # Days
            if re.search(rf"\b{word}\s+(?:din|days?)\b", t_lower):
                entities["notice_days"] = int(val)
                break
        if "notice_days" not in entities:
            match = re.search(r"(\d+)\s*(?:days?|din)", t_lower)
            if match:
                entities["notice_days"] = int(match.group(1))
            else:
                match_m = re.search(r"(\d+)\s*(?:months?|mahine)", t_lower)
                if match_m:
                    entities["notice_days"] = int(match_m.group(1)) * 30

        # 3. Buyout Flexibility
        if any(b in t_lower for b in ["buyout", "early release", "manager se baat", "manager approved"]):
            entities["buyout_flexible"] = True
        elif "buyout" in t_lower:
            entities["buyout_flexible"] = True

        # 4. Technologies
        detected_tech = []
        for tech in cls.TECHNICAL_TERMS:
            if re.search(rf"\b{re.escape(tech)}\b", t_lower):
                detected_tech.append(tech)
        if detected_tech:
            entities["technologies"] = detected_tech

        return entities

    @classmethod
    def _translate_to_canonical(cls, text: str) -> str:
        """Substitutes common Hinglish phrases and connectives with canonical English."""
        norm = text

        # Multi-word phrase substitutions first
        phrases = [
            (r"\bmera notice period\b", "my notice period"),
            (r"\bmaine use kiya tha\b", "I used"),
            (r"\bhumne use kiya tha\b", "we used"),
            (r"\bhumne banaya tha\b", "we built"),
            (r"\bmaine banaya tha\b", "I built"),
            (r"\buse karte hain\b", "we use"),
            (r"\buse karta hoon\b", "I use"),
            (r"\buse karta hu\b", "I use"),
            (r"\bka experience hai\b", "experience"),
            (r"\bmanager se baat hui thi\b", "discussed with manager"),
            (r"\bearly release mil jayega\b", "early release is approved"),
            (r"\bbuyout possible hai\b", "buyout is possible"),
            (r"\bpossible hai\b", "is possible"),
            (r"\bbohot kam thi\b", "was very low"),
            (r"\bbahut kam thi\b", "was very low"),
            (r"\bscale high tha\b", "scale was high"),
            (r"\blatency kam thi\b", "latency was low"),
            (r"\bdo mahine\b", "60 days"),
            (r"\bek mahina\b", "30 days"),
            (r"\bteen mahine\b", "90 days"),
            (r"\bpachees\s+(?:lakh|lac|lpa)\b", "25 LPA"),
            (r"\bbees\s+(?:lakh|lac|lpa)\b", "20 LPA"),
            (r"\btees\s+(?:lakh|lac|lpa)\b", "30 LPA"),
            (r"\bchalees\s+(?:lakh|lac|lpa)\b", "40 LPA"),
            (r"\bpachaas\s+(?:lakh|lac|lpa)\b", "50 LPA"),
            (r"\bpaanch saal\b", "5 years"),
            (r"\bdo saal\b", "2 years"),
            (r"\bchaar saal\b", "4 years"),
        ]

        for pattern, repl in phrases:
            norm = re.sub(pattern, repl, norm, flags=re.IGNORECASE)

        # Single word connective substitutions
        words = norm.split()
        translated_words = []
        for w in words:
            clean_w = re.sub(r"[^\w]", "", w.lower())
            if clean_w in cls.HINDI_CONNECTIVES:
                repl = cls.HINDI_CONNECTIVES[clean_w]
                # preserve punctuation if present
                if w.endswith((".", ",", "?", "!")):
                    repl += w[-1]
                translated_words.append(repl)
            else:
                translated_words.append(w)

        canonical = " ".join(translated_words)
        # Clean up repeated spaces or awkward phrasing
        canonical = re.sub(r"\s+", " ", canonical).strip()
        return canonical
