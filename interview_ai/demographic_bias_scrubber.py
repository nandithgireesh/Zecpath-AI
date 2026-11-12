"""
Day 43 Deliverable 1: Demographic Bias Scrubber
==============================================
Identifies and redacts demographic bias signals, proxy variables,
gendered pronouns, age indicators, institution prestige proxies,
and geographic markers to ensure neutral semantic evaluation.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ScrubTelemetry:
    raw_text: str
    scrubbed_text: str
    gender_signals_redacted: int = 0
    age_signals_redacted: int = 0
    institution_signals_redacted: int = 0
    geographic_signals_redacted: int = 0
    name_signals_redacted: int = 0
    redaction_log: List[str] = field(default_factory=list)

    @property
    def total_signals_redacted(self) -> int:
        return (
            self.gender_signals_redacted
            + self.age_signals_redacted
            + self.institution_signals_redacted
            + self.geographic_signals_redacted
            + self.name_signals_redacted
        )


class DemographicBiasScrubber:
    """
    Sanitizes candidate utterances before downstream semantic scoring and sentiment evaluation,
    stripping protected characteristic proxies to guarantee blind, merit-centric scoring.
    """

    # Pre-compiled Patterns
    GENDERED_PRONOUNS_PATTERN = re.compile(
        r"\b(?:he\s+said|she\s+said|he\s+told|she\s+told|he\s+is|she\s+is|he\s+was|she\s+was)\b",
        re.IGNORECASE,
    )
    GENDER_SELF_LABEL_PATTERN = re.compile(
        r"\b(?:as\s+a\s+(?:man|woman|female|male|guy|girl|mother|father|mom|dad))\b",
        re.IGNORECASE,
    )

    AGE_EXPLICIT_PATTERN = re.compile(
        r"\b(?:I\s+am|I'm)\s+(\d{2})\s+years?\s+old\b|\b(?:at\s+my\s+age|in\s+my\s+(?:20s|30s|40s|50s|60s))\b",
        re.IGNORECASE,
    )
    GRADUATION_YEAR_PATTERN = re.compile(
        r"\b(?:graduated|college|university|bachelor'?s|master'?s|phd)\s+(?:in|back\s+in|class\s+of)\s+(19\d{2}|20[0-1]\d)\b",
        re.IGNORECASE,
    )

    INSTITUTION_PRESTIGE_PATTERN = re.compile(
        r"\b(?:Harvard|Stanford|MIT|Massachusetts\s+Institute\s+of\s+Technology|Oxford|Cambridge|Princeton|Yale|Columbia|Berkeley|Carnegie\s+Mellon|IIT\s+[A-Za-z]+|BITS\s+Pilani)\b",
        re.IGNORECASE,
    )

    GEOGRAPHIC_ORIGIN_PATTERN = re.compile(
        r"\b(?:back\s+in|originally\s+from|born\s+in|immigrated\s+from|growing\s+up\s+in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
        re.IGNORECASE,
    )

    NAME_SELF_INTRO_PATTERN = re.compile(
        r"\b(?:my\s+name\s+is|I\s+am|I'm|this\s+is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
        re.IGNORECASE,
    )

    # Dialect and Non-Native Syntax Normalization Map
    DIALECT_NORMALIZATIONS = [
        (re.compile(r"\bdoing\s+the\s+needful\b", re.IGNORECASE), "taking the required action"),
        (re.compile(r"\bprepone\b", re.IGNORECASE), "advance"),
        (re.compile(r"\bpassed\s+out\s+from\s+college\b", re.IGNORECASE), "graduated from college"),
        (re.compile(r"\bupgradation\b", re.IGNORECASE), "upgrade"),
        (re.compile(r"\bdiscuss\s+about\b", re.IGNORECASE), "discuss"),
    ]

    def __init__(self, candidate_name: Optional[str] = None):
        self.candidate_name = candidate_name
        self._name_pattern = None
        if candidate_name and len(candidate_name.strip().split()) > 0:
            parts = [re.escape(p) for p in candidate_name.strip().split() if len(p) > 2]
            if parts:
                self._name_pattern = re.compile(r"\b(?:" + "|".join(parts) + r")\b", re.IGNORECASE)

    def scrub(self, text: str) -> ScrubTelemetry:
        """
        Executes multi-pass demographic signal neutralization across candidate transcript text.
        """
        if not text or not text.strip():
            return ScrubTelemetry(raw_text=text, scrubbed_text="")

        working = text
        log: List[str] = []
        name_count = 0
        gender_count = 0
        age_count = 0
        inst_count = 0
        geo_count = 0

        # 1. Explicit Candidate Name mentions
        if self._name_pattern:
            matches = self._name_pattern.findall(working)
            if matches:
                name_count += len(matches)
                working = self._name_pattern.sub("[CANDIDATE]", working)
                log.append(f"Redacted candidate name token ({len(matches)} occurrences)")

        intro_matches = self.NAME_SELF_INTRO_PATTERN.findall(working)
        if intro_matches:
            name_count += len(intro_matches)
            working = self.NAME_SELF_INTRO_PATTERN.sub("I am [CANDIDATE]", working)
            log.append("Redacted self-introduction name marker")

        # 2. Gender signals & pronouns
        gender_self = self.GENDER_SELF_LABEL_PATTERN.findall(working)
        if gender_self:
            gender_count += len(gender_self)
            working = self.GENDER_SELF_LABEL_PATTERN.sub("as an engineer", working)
            log.append(f"Neutralized self-gender identity markers ({len(gender_self)})")

        gender_pronoun_matches = self.GENDERED_PRONOUNS_PATTERN.findall(working)
        if gender_pronoun_matches:
            gender_count += len(gender_pronoun_matches)
            working = re.sub(r"\bhe\s+said\b|\bshe\s+said\b", "they said", working, flags=re.IGNORECASE)
            working = re.sub(r"\bhe\s+was\b|\bshe\s+was\b", "they were", working, flags=re.IGNORECASE)
            working = re.sub(r"\bhe\s+is\b|\bshe\s+is\b", "they are", working, flags=re.IGNORECASE)
            working = re.sub(r"\bhe\s+told\b|\bshe\s+told\b", "they told", working, flags=re.IGNORECASE)
            log.append(f"Neutralized third-party gendered pronouns ({len(gender_pronoun_matches)})")

        # 3. Age & Graduation Years
        age_matches = self.AGE_EXPLICIT_PATTERN.findall(working)
        if age_matches:
            age_count += len(age_matches)
            working = self.AGE_EXPLICIT_PATTERN.sub("I have technical tenure", working)
            log.append(f"Redacted explicit age indicators ({len(age_matches)})")

        grad_matches = self.GRADUATION_YEAR_PATTERN.findall(working)
        if grad_matches:
            age_count += len(grad_matches)
            working = self.GRADUATION_YEAR_PATTERN.sub(r"graduated [DEGREE_PERIOD]", working)
            log.append(f"Masked academic graduation year proxy ({len(grad_matches)})")

        # 4. University / Institutional Prestige Bias
        inst_matches = self.INSTITUTION_PRESTIGE_PATTERN.findall(working)
        if inst_matches:
            inst_count += len(inst_matches)
            working = self.INSTITUTION_PRESTIGE_PATTERN.sub("[ACCREDITED_INSTITUTION]", working)
            log.append(f"Normalized university prestige proxies: {', '.join(set(inst_matches))}")

        # 5. Geographic / National Origin Bias
        geo_matches = self.GEOGRAPHIC_ORIGIN_PATTERN.findall(working)
        if geo_matches:
            geo_count += len(geo_matches)
            working = self.GEOGRAPHIC_ORIGIN_PATTERN.sub("relocated from [PREVIOUS_LOCATION]", working)
            log.append(f"Masked geographic national origin markers ({len(geo_matches)})")

        # 6. Dialect Normalization (Protects against non-native syntactic bias)
        for pattern, replacement in self.DIALECT_NORMALIZATIONS:
            if pattern.search(working):
                working = pattern.sub(replacement, working)
                log.append(f"Normalized regional syntactic idiom to standard terminology: '{replacement}'")

        # Consolidate spaces
        working = re.sub(r"\s+", " ", working).strip()

        return ScrubTelemetry(
            raw_text=text,
            scrubbed_text=working,
            gender_signals_redacted=gender_count,
            age_signals_redacted=age_count,
            institution_signals_redacted=inst_count,
            geographic_signals_redacted=geo_count,
            name_signals_redacted=name_count,
            redaction_log=log,
        )
