import re
from typing import List, Dict, Any, Optional, Tuple

from screening_ai.intent_models import (
    CandidateIntent,
    ProficiencyLevel,
    SkillDetail,
    ExperienceDetail,
    AvailabilityDetail,
    SalaryDetail,
    SemanticQualityScore,
    StructuredAnswerObject,
)
from screening_ai.intent_classifier import CandidateIntentClassifier


TECHNICAL_SKILL_PATTERNS = {
    "python": r"\bpython(?:3)?\b",
    "pytorch": r"\bpytorch\b",
    "tensorflow": r"\btensorflow\b",
    "keras": r"\bkeras\b",
    "scikit-learn": r"\bscikit[- ]learn|sklearn\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes|k8s\b",
    "fastapi": r"\bfastapi\b",
    "flask": r"\bflask\b",
    "django": r"\bdjango\b",
    "react": r"\breact(?:\.js)?\b",
    "node.js": r"\bnode(?:\.js)?\b",
    "aws": r"\baws|amazon web services\b",
    "gcp": r"\bgcp|google cloud\b",
    "azure": r"\bazure\b",
    "sql": r"\bsql\b",
    "postgresql": r"\bpostgres(?:ql)?\b",
    "mongodb": r"\bmongodb|mongo\b",
    "ci/cd": r"\bci[/-]cd|jenkins|github actions\b",
    "git": r"\bgit(?:hub|lab)?\b",
    "kafka": r"\bkafka\b",
    "spark": r"\bspark|pyspark\b",
    "nlp": r"\bnlp|natural language processing\b",
    "llm": r"\bllms?|large language models?\b",
    "transformers": r"\btransformers?|hugging\s*face\b",
    "bert": r"\bbert\b",
    "c++": r"\bc\+\+\b",
    "java": r"\bjava\b",
}

PROFICIENCY_INDICATORS = {
    ProficiencyLevel.ADVANCED: [
        r"\bexpert\b", r"\blead\b", r"\barchitect\b", r"\bextensively\b",
        r"\badvanced\b", r"\bin[- ]depth\b", r"\bmastered\b", r"\b5\+?\s*years\b"
    ],
    ProficiencyLevel.INTERMEDIATE: [
        r"\bproficient\b", r"\bsolid\b", r"\bhands[- ]on\b", r"\bgood\b",
        r"\bcomfortable\b", r"\bworking with\b", r"\bday[- ]to[- ]day\b"
    ],
    ProficiencyLevel.BEGINNER: [
        r"\bbasic\b", r"\bfundamental\b", r"\bbeginner\b", r"\bfamiliar\b",
        r"\blearning\b", r"\blittle experience\b", r"\bacademic\b"
    ],
}

ROLE_PATTERNS = [
    (r"\bmachine learning engineer\b", "Machine Learning Engineer"),
    (r"\bdata scientist\b", "Data Scientist"),
    (r"\bbackend (?:developer|engineer)\b", "Backend Engineer"),
    (r"\bfull[- ]stack (?:developer|engineer)\b", "Full Stack Engineer"),
    (r"\bdevops (?:engineer|specialist)\b", "DevOps Engineer"),
    (r"\bsoftware (?:engineer|developer)\b", "Software Engineer"),
    (r"\bfrontend (?:developer|engineer)\b", "Frontend Engineer"),
    (r"\bdata engineer\b", "Data Engineer"),
]

DOMAIN_PATTERNS = [
    (r"\bfintech|banking|financial\b", "Fintech"),
    (r"\bhealth(?:care)?|medical\b", "Healthcare"),
    (r"\be[- ]commerce|retail\b", "E-Commerce"),
    (r"\bsaas|b2b\b", "SaaS"),
    (r"\bedtech|education\b", "EdTech"),
    (r"\btelecom\b", "Telecommunications"),
    (r"\bautomotive|ev\b", "Automotive"),
]

WORD_NUMBERS = {
    "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
    "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0,
    "two and a half": 2.5, "three and a half": 3.5, "four and a half": 4.5,
    "five and a half": 5.5, "six and a half": 6.5
}


class AnswerUnderstandingEngine:
    """
    Day 25 Answer Intent & Understanding Engine.
    Extracts deep semantic entities (Skills, Experience, Availability, Salary),
    detects off-topic responses, identifies vague/incomplete answers, and
    compiles structured semantic answer objects.
    """

    def __init__(self):
        self.classifier = CandidateIntentClassifier()

    # -------------------------------------------------------------
    # 1. Skills Extraction
    # -------------------------------------------------------------
    def extract_skills(self, text: str) -> List[SkillDetail]:
        """Extract confirmed and declined technical skills along with inferred proficiency."""
        if not text:
            return []

        lower = text.lower()
        extracted: List[SkillDetail] = []

        # Split into sub-clauses so negations in one clause don't pollute another
        clauses = re.split(r"[,;]|\b(?:but|however|although|whereas)\b", lower)

        for canonical_name, pattern in TECHNICAL_SKILL_PATTERNS.items():
            for clause in clauses:
                m = re.search(pattern, clause)
                if m:
                    skill_start = m.start()
                    # Look at local window preceding and including this skill
                    window_start = max(0, skill_start - 45)
                    local_window = clause[window_start:m.end()]

                    # Check if declined locally or in clause
                    clause_decline = bool(re.search(
                        r"\b(?:haven'?t|have not|no experience|never (?:used|worked|touched)|don'?t know|do not know|not familiar|zero experience|not much exposure)\b",
                        local_window
                    )) or bool(re.search(
                        rf"(?:haven'?t|not|never|no|without)\s+(?:\w+\s+){{0,3}}{pattern}",
                        clause
                    ))

                    is_confirmed = not clause_decline
                    sentiment = "positive" if is_confirmed else "negative"

                    # Infer proficiency from local window around skill
                    proficiency = ProficiencyLevel.UNSPECIFIED
                    if is_confirmed:
                        for prof, indicators in PROFICIENCY_INDICATORS.items():
                            if any(re.search(ind, local_window) for ind in indicators):
                                proficiency = prof
                                break
                        # Fallback to clause if not found in local window
                        if proficiency == ProficiencyLevel.UNSPECIFIED:
                            for prof, indicators in PROFICIENCY_INDICATORS.items():
                                if any(re.search(ind, clause) for ind in indicators):
                                    proficiency = prof
                                    break

                    extracted.append(SkillDetail(
                        skill=canonical_name,
                        proficiency=proficiency,
                        sentiment=sentiment,
                        is_confirmed=is_confirmed,
                    ))
                    break


        return extracted

    # -------------------------------------------------------------
    # 2. Experience Extraction
    # -------------------------------------------------------------
    def extract_experience(self, text: str) -> Optional[ExperienceDetail]:
        """Extract total years of experience, primary role, and industry domain."""
        if not text:
            return None

        lower = text.lower()
        years: Optional[float] = None

        # Try word numbers first
        for phrase, val in WORD_NUMBERS.items():
            if f"{phrase} year" in lower or f"{phrase} yr" in lower:
                years = val
                break

        # Try digit regex
        if years is None:
            match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)\b", lower)
            if match:
                try:
                    years = float(match.group(1))
                except ValueError:
                    pass

        # Identify Role
        primary_role: Optional[str] = None
        for pat, title in ROLE_PATTERNS:
            if re.search(pat, lower):
                primary_role = title
                break

        # Identify Domains
        domains: List[str] = []
        for pat, dom in DOMAIN_PATTERNS:
            if re.search(pat, lower):
                domains.append(dom)

        # Identify key technologies mentioned
        techs = [canonical for canonical, pat in TECHNICAL_SKILL_PATTERNS.items() if re.search(pat, lower)]

        if years is not None or primary_role is not None or techs:
            return ExperienceDetail(
                total_years=years,
                primary_role=primary_role,
                domains=domains,
                key_technologies=techs,
                responsibilities_summary=text[:250],
            )
        return None

    # -------------------------------------------------------------
    # 3. Availability Extraction
    # -------------------------------------------------------------
    def extract_availability(self, text: str) -> Optional[AvailabilityDetail]:
        """Extract notice period duration, immediate availability, and buyout flags."""
        if not text:
            return None

        lower = text.lower()
        is_immediate = any(k in lower for k in ["immediate", "ready to join", "right away", "zero days", "tomorrow"])
        can_buyout = any(k in lower for k in ["buyout", "buy out", "company can pay"])
        serving_notice = any(k in lower for k in ["serving notice", "resigned", "last working day", "lwd"])

        notice_days: Optional[int] = None
        if is_immediate:
            notice_days = 0
        else:
            # Days regex
            day_match = re.search(r"\b(\d+)\s*(?:days?)\b", lower)
            if day_match:
                notice_days = int(day_match.group(1))
            else:
                # Months regex
                month_match = re.search(r"\b(\d+)\s*(?:months?)\b", lower)
                if month_match:
                    notice_days = int(month_match.group(1)) * 30
                else:
                    # Weeks regex
                    week_match = re.search(r"\b(\d+)\s*(?:weeks?)\b", lower)
                    if week_match:
                        notice_days = int(week_match.group(1)) * 7

        if notice_days is not None or is_immediate or serving_notice:
            return AvailabilityDetail(
                notice_period_days=notice_days,
                is_immediate_joiner=is_immediate,
                can_buyout_notice=can_buyout,
                serving_notice=serving_notice,
            )
        return None

    # -------------------------------------------------------------
    # 4. Salary Extraction
    # -------------------------------------------------------------
    def extract_salary(self, text: str) -> Optional[SalaryDetail]:
        """Extract current CTC, expected CTC, and negotiability flags."""
        if not text:
            return None

        lower = text.lower()
        is_negotiable = any(k in lower for k in ["negotiable", "flexible", "open to", "market standard", "discuss"])

        current_ctc: Optional[float] = None
        expected_ctc: Optional[float] = None

        # Look for patterns like "current 12 LPA and expected CTC is 16.5 LPA"
        curr_match = re.search(r"(?:current(?:ly)?|earning|drawing)(?:\s+(?:ctc|salary|package))?\s*(?:is|of|around)?\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac)?", lower)
        if curr_match:
            current_ctc = float(curr_match.group(1))

        exp_match = re.search(r"(?:expect(?:ing|ed)?|looking for|target)(?:\s+(?:ctc|salary|package))?\s*(?:is|of|around)?\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac)?", lower)
        if exp_match:
            expected_ctc = float(exp_match.group(1))

        # Fallback: scan for any standalone LPA numbers
        if current_ctc is None and expected_ctc is None:
            lpa_numbers = [float(m) for m in re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac)\b", lower)]
            if len(lpa_numbers) == 1:
                expected_ctc = lpa_numbers[0]
            elif len(lpa_numbers) >= 2:
                current_ctc = lpa_numbers[0]
                expected_ctc = lpa_numbers[1]


        if current_ctc is not None or expected_ctc is not None or is_negotiable:
            return SalaryDetail(
                current_ctc_lpa=current_ctc,
                expected_ctc_lpa=expected_ctc,
                is_negotiable=is_negotiable,
                flexibility_note="Negotiable" if is_negotiable else "Strict/Fixed",
            )
        return None

    # -------------------------------------------------------------
    # 5. Off-Topic & Vagueness Evaluation
    # -------------------------------------------------------------
    def evaluate_quality(
        self,
        text: str,
        question_category: Optional[str] = None,
        question_prompt: Optional[str] = None,
        primary_intent: CandidateIntent = CandidateIntent.PROVIDING_EXPERIENCE,
    ) -> SemanticQualityScore:
        """
        Evaluate semantic relevance, clarity, off-topic deflection,
        vagueness, and missing required slots.
        """
        if not text or not text.strip():
            return SemanticQualityScore(
                relevance_score=0.0,
                clarity_score=0.0,
                is_off_topic=False,
                is_vague=True,
                missing_slots=["complete_answer"],
                follow_up_needed=True,
            )

        lower = text.lower()
        is_off_topic = primary_intent == CandidateIntent.OFF_TOPIC
        is_vague = primary_intent == CandidateIntent.VAGUE_ANSWER

        relevance = 0.20 if is_off_topic else 0.95
        clarity = 0.35 if is_vague else 0.90

        missing_slots: List[str] = []
        cat_norm = (question_category or "").lower()

        # Slot completeness audit
        if "salary" in cat_norm:
            has_num = bool(re.search(r"\b\d+(?:\.\d+)?\b", lower))
            if not has_num:
                missing_slots.append("expected_ctc_lpa")
                clarity -= 0.30
                is_vague = True

        elif "notice" in cat_norm or "availab" in cat_norm:
            has_days = any(k in lower for k in ["day", "month", "week", "immediate", "ready"])
            if not has_days:
                missing_slots.append("notice_period_duration")
                clarity -= 0.30
                is_vague = True

        elif "experience" in cat_norm:
            has_exp_metric = bool(re.search(r"\b\d+\b", lower)) or any(k in lower for k in ["year", "yr", "month"])
            if not has_exp_metric:
                missing_slots.append("total_experience_years")
                clarity -= 0.25

        elif "skill" in cat_norm or "tech" in cat_norm:
            has_tech = any(re.search(pat, lower) for pat in TECHNICAL_SKILL_PATTERNS.values())
            if not has_tech and not is_off_topic:
                missing_slots.append("specific_technical_skills")
                clarity -= 0.20

        follow_up_needed = is_off_topic or is_vague or bool(missing_slots)

        return SemanticQualityScore(
            relevance_score=round(max(0.0, min(1.0, relevance)), 2),
            clarity_score=round(max(0.0, min(1.0, clarity)), 2),
            is_off_topic=is_off_topic,
            is_vague=is_vague,
            missing_slots=missing_slots,
            follow_up_needed=follow_up_needed,
        )

    # -------------------------------------------------------------
    # 6. Generate Conversational Follow-Up Recommendation
    # -------------------------------------------------------------
    def generate_follow_up(
        self,
        intent: CandidateIntent,
        quality: SemanticQualityScore,
        question_category: Optional[str] = None,
    ) -> Optional[str]:
        """Produce dynamic conversational recovery prompts for ambiguous responses."""
        if intent == CandidateIntent.ASKING_CLARIFICATION:
            return "Certainly! Let me clarify what we are looking for in this role."

        if quality.is_off_topic:
            return "That's interesting, but could we refocus on your relevant technical background for this position?"

        if "expected_ctc_lpa" in quality.missing_slots:
            return "Could you provide your specific expected CTC in LPA (Lakhs Per Annum)?"

        if "notice_period_duration" in quality.missing_slots:
            return "Could you specify your official notice period duration in days or months?"

        if "total_experience_years" in quality.missing_slots:
            return "Could you clarify how many total years of relevant professional experience you have?"

        if quality.is_vague:
            return "Could you provide more concrete details or an example from your recent projects?"

        return None

    # -------------------------------------------------------------
    # 7. Comprehensive Answer Understanding Pipeline
    # -------------------------------------------------------------
    def understand_answer(
        self,
        raw_text: str,
        question_category: Optional[str] = None,
        question_prompt: Optional[str] = None,
        turn_id: Optional[str] = None,
        question_id: Optional[str] = None,
    ) -> StructuredAnswerObject:
        """
        End-to-end understanding pipeline:
        1. Classifies intent & confidence
        2. Extracts skills (with proficiency & sentiment)
        3. Extracts experience, availability, and salary
        4. Detects off-topic deflection & vagueness
        5. Compiles semantic StructuredAnswerObject
        """
        # 1. Intent Classification
        intent, conf, secondary = self.classifier.classify_intent(
            text=raw_text,
            question_category=question_category,
            question_prompt=question_prompt,
        )

        # 2. Entity Extractions
        skills = self.extract_skills(raw_text)
        experience = self.extract_experience(raw_text)
        availability = self.extract_availability(raw_text)
        salary = self.extract_salary(raw_text)

        # 3. Quality & Slot Completeness Audit
        quality = self.evaluate_quality(
            text=raw_text,
            question_category=question_category,
            question_prompt=question_prompt,
            primary_intent=intent,
        )

        # 4. Dynamic Follow-Up Prompt
        follow_up = self.generate_follow_up(intent, quality, question_category)

        return StructuredAnswerObject(
            turn_id=turn_id,
            question_id=question_id,
            question_category=question_category,
            raw_text=raw_text,
            cleaned_text=raw_text.strip(),
            primary_intent=intent,
            intent_confidence=conf,
            secondary_intents=secondary,
            extracted_skills=skills,
            experience=experience,
            availability=availability,
            salary=salary,
            quality=quality,
            follow_up_recommendation=follow_up,
        )
