"""
Day 35: Communication Skill Evaluation Engine
=============================================
Provides deterministic, objective evaluation of candidate communication skills across 6 core dimensions:
1. Fluency (sentence continuity, clause flow, transition density)
2. Grammar Quality (tense consistency, grammatical agreement, punctuation health)
3. Vocabulary Range (length-damped RTTR, lexical sophistication, repetition penalty)
4. Clarity of Explanation (idea density, readability, vagueness penalty)
5. Filler Word Detection (pure disfluencies and discourse crutches)
6. Answer Structure (STAR framework alignment for behavioral answers, PREP for technical claims)

Includes Bias-Reduction Normalization:
- ESL / Non-Native English speaker fairness adjustment (prioritizes clarity and structure over idiom flair)
- Length-invariance scaling (prevents penalizing concise answers or rewarding rambling verbosity)
- Role-track weighting adjustment (Technical vs Non-Technical expectations)
"""

import re
import math
from typing import Dict, List, Any, Tuple, Optional
from interview_ai.hr_models import (
    HRCategory,
    RoleTrack,
    CommunicationScoreBreakdown,
)


class FluencyAnalyzer:
    """
    Evaluates sentence continuity, syntactic flow, and discourse connectivity.
    """

    TRANSITION_CONNECTORS = [
        # Cause & Result
        "therefore", "consequently", "as a result", "because", "thus", "hence", "accordingly",
        # Contrast & Nuance
        "however", "on the other hand", "nevertheless", "although", "yet", "despite", "whereas",
        # Addition & Elaboration
        "furthermore", "in addition", "moreover", "specifically", "for instance", "for example",
        "subsequently", "firstly", "secondly", "finally", "in particular", "additionally"
    ]

    def analyze(self, text: str) -> Tuple[float, List[str], Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 0.0, [], {"sentence_count": 0, "avg_sentence_len": 0}

        # Sentence segmentation
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if s.strip()]
        if not raw_sentences:
            raw_sentences = [cleaned]

        words = cleaned.split()
        total_words = len(words)
        sentence_count = len(raw_sentences)
        avg_sentence_len = total_words / max(1, sentence_count)

        lower = cleaned.lower()
        matched_connectors = [c for c in self.TRANSITION_CONNECTORS if re.search(r'\b' + re.escape(c) + r'\b', lower)]

        # Baseline score
        score = 75.0

        # 1. Sentence continuity & length health (ideal: 10 - 28 words per sentence)
        if 10 <= avg_sentence_len <= 28:
            score += 12.0
        elif avg_sentence_len < 6:
            score -= 15.0  # Excessive fragmentation
        elif avg_sentence_len > 45:
            score -= 15.0  # Run-on sentences lacking punctuation

        # 2. Transition density bonus
        connector_ratio = len(matched_connectors) / max(1, sentence_count)
        if connector_ratio >= 0.5:
            score += 15.0
        elif connector_ratio >= 0.25:
            score += 8.0

        # 3. Severe fragmentation check (e.g. ellipses, broken fragments)
        fragment_count = len(re.findall(r'\.\.\.', cleaned))
        score -= min(15.0, fragment_count * 5.0)

        # 4. Ultra-terse penalty
        if total_words < 12:
            score -= 20.0

        score = max(10.0, min(100.0, round(score, 1)))

        diagnostics = {
            "sentence_count": sentence_count,
            "avg_sentence_len": round(avg_sentence_len, 1),
            "transition_count": len(matched_connectors),
            "matched_connectors": matched_connectors,
        }
        return score, matched_connectors, diagnostics


class GrammarQualityAnalyzer:
    """
    Evaluates grammatical agreement, tense consistency, and structural punctuation.
    """

    GRAMMATICAL_ANTI_PATTERNS = [
        # Subject-Verb mismatches
        (r'\b(we|they|you)\s+was\b', "Subject-verb mismatch ('was' with plural subject)"),
        (r'\b(he|she|it)\s+were\b', "Subject-verb mismatch ('were' with singular subject)"),
        (r'\b(he|she|it)\s+don\'t\b', "Subject-verb mismatch ('don't' instead of 'doesn't')"),
        (r'\b(i)\s+(is|are)\b', "Subject-verb mismatch ('I is/are')"),
        # Double past tense / modal corruptions
        (r'\b(did not|didn\'t)\s+(went|had|saw|built|wrote|fixed)\b', "Double past tense with auxiliary 'did'"),
        (r'\b(could|should|would)\s+of\b', "Modal corruption ('of' instead of 'have')"),
        (r'\b(haven\'t|hasn\'t)\s+no\b', "Double negative"),
    ]

    def analyze(self, text: str) -> Tuple[float, List[str], Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 0.0, [], {"errors": 0}

        words = cleaned.split()
        total_words = len(words)
        lower = cleaned.lower()

        detected_errors = []
        for pattern, explanation in self.GRAMMATICAL_ANTI_PATTERNS:
            if re.search(pattern, lower):
                detected_errors.append(explanation)

        score = 95.0

        # Penalty per detected anti-pattern
        error_deduction = len(detected_errors) * 12.0
        score -= error_deduction

        # Punctuation check
        has_terminal_punct = bool(re.search(r'[.!?]$', cleaned))
        if not has_terminal_punct and total_words > 10:
            score -= 6.0

        # Capitalization at start
        if cleaned and not cleaned[0].isupper():
            score -= 4.0

        # Isolated lowercase 'i' check
        lowercase_i_count = len(re.findall(r'\bi\b', text))
        if lowercase_i_count > 0:
            score -= min(10.0, lowercase_i_count * 3.0)

        score = max(15.0, min(100.0, round(score, 1)))
        diagnostics = {
            "error_count": len(detected_errors),
            "errors": detected_errors,
            "has_terminal_punct": has_terminal_punct,
        }
        return score, detected_errors, diagnostics


class VocabularyAnalyzer:
    """
    Evaluates vocabulary range using length-damped Root Type-Token Ratio (RTTR)
    and domain-specific lexical sophistication.
    """

    TECHNICAL_VOCABULARY = {
        "architected", "concurrency", "distributed", "throughput", "latency", "scalability",
        "microservices", "pipeline", "cache", "redis", "kafka", "docker", "kubernetes",
        "postgres", "nosql", "idempotent", "middleware", "sharding", "replica", "framework",
        "refactored", "benchmarked", "asynchronous", "algorithm", "optimization", "telemetry",
        "regression", "fixtures", "integration", "graphql", "grpc", "containerization"
    }

    BUSINESS_VOCABULARY = {
        "stakeholder", "governance", "turnaround", "strategic", "operational", "consensus",
        "alignment", "kpi", "milestone", "prioritization", "cross-functional", "deliverables",
        "leadership", "synergy", "procurement", "enablement", "facilitate", "negotiation",
        "post-mortem", "retrospective", "compromise", "framework", "continuity", "roadmap"
    }

    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by",
        "from", "up", "about", "into", "over", "after", "is", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "i", "we", "you", "they",
        "it", "he", "she", "this", "that", "these", "those", "my", "our", "your", "their"
    }

    def analyze(self, text: str, role_track: RoleTrack = RoleTrack.TECHNICAL) -> Tuple[float, Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 0.0, {"rttr": 0.0, "total_words": 0, "unique_words": 0}

        tokens = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned.lower())
        total_tokens = len(tokens)
        if total_tokens == 0:
            return 20.0, {"rttr": 0.0, "total_tokens": 0}

        unique_tokens = set(tokens)
        unique_count = len(unique_tokens)

        # 1. Length-Damped Root TTR: RTTR = unique / sqrt(total)
        # Prevents penalizing longer answers for natural function word recurrence
        rttr = unique_count / math.sqrt(total_tokens)

        # Baseline calculation from RTTR (ideal conversational RTTR: 3.5 to 6.5)
        # RTTR of 5.0 -> ~80 baseline
        score = min(88.0, rttr * 16.5)

        # 2. Domain sophistication bonus
        target_lexicon = self.TECHNICAL_VOCABULARY if role_track == RoleTrack.TECHNICAL else self.BUSINESS_VOCABULARY
        matched_domain = [t for t in unique_tokens if t in target_lexicon]
        score += min(15.0, len(matched_domain) * 4.0)

        # 3. Excessive word repetition penalty (excluding common stopwords)
        content_tokens = [t for t in tokens if t not in self.STOPWORDS]
        counts = {}
        for ct in content_tokens:
            counts[ct] = counts.get(ct, 0) + 1

        repetition_penalties = 0.0
        for word, count in counts.items():
            if count >= 4 and total_tokens < 60:
                repetition_penalties += (count - 3) * 3.0
            elif count >= 6:
                repetition_penalties += (count - 5) * 2.5
        score -= min(15.0, repetition_penalties)

        score = max(20.0, min(100.0, round(score, 1)))

        diagnostics = {
            "total_tokens": total_tokens,
            "unique_tokens": unique_count,
            "rttr": round(rttr, 2),
            "matched_domain_terms": matched_domain,
            "domain_count": len(matched_domain),
        }
        return score, diagnostics


class ClarityAnalyzer:
    """
    Evaluates explanation clarity, idea density, and vagueness penalties.
    """

    VAGUE_MARKERS = [
        "and all", "and stuff", "stuff like that", "things like that", "kind of like",
        "sort of like", "basically just", "more or less", "somehow", "etc etc"
    ]

    def analyze(self, text: str) -> Tuple[float, List[str], Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 0.0, [], {"idea_density": 0.0}

        words = cleaned.split()
        total_words = len(words)
        lower = cleaned.lower()

        # 1. Vagueness check
        vague_hits = [m for m in self.VAGUE_MARKERS if m in lower]

        # 2. Content word density (nouns, lexical verbs vs filler stopwords)
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', lower)
        stopwords = VocabularyAnalyzer.STOPWORDS
        content_words = [t for t in tokens if t not in stopwords]
        idea_density = len(content_words) / max(1, len(tokens))

        score = 80.0

        # High content density reward (only if clean of hand-waving)
        if not vague_hits:
            if idea_density >= 0.55:
                score += 14.0
            elif idea_density >= 0.42:
                score += 8.0
            elif idea_density < 0.30:
                score -= 15.0
        else:
            # Vagueness penalty: suppress content density bonus and deduct for hand-waving
            score -= (10.0 + len(vague_hits) * 12.0)

        # Terse brevity penalty
        if total_words < 12:
            score -= 18.0

        score = max(10.0, min(100.0, round(score, 1)))

        diagnostics = {
            "idea_density": round(idea_density, 2),
            "vague_hits": vague_hits,
            "vagueness_count": len(vague_hits),
        }
        return score, vague_hits, diagnostics


class FillerWordDetector:
    """
    Detects pure disfluencies and conversational discourse crutches.
    Computes filler density percentage and exponential decay score.
    """

    PURE_FILLERS = [
        "um", "uh", "er", "ah", "erm", "umm", "uhh"
    ]

    DISCOURSE_FILLERS = [
        "like", "you know", "i mean", "basically", "literally", "actually",
        "sort of", "kind of", "right?", "you see"
    ]

    CRUTCH_PHRASES = [
        "to be honest", "at the end of the day", "honestly speaking"
    ]

    def analyze(self, text: str) -> Tuple[float, Dict[str, int], Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 100.0, {}, {"total_fillers": 0, "filler_percentage": 0.0}

        words = cleaned.split()
        total_words = len(words)
        lower = cleaned.lower()

        detected_fillers: Dict[str, int] = {}
        total_filler_instances = 0

        # 1. Pure Fillers (word boundary matching)
        for filler in self.PURE_FILLERS:
            matches = len(re.findall(r'\b' + re.escape(filler) + r'\b', lower))
            if matches > 0:
                detected_fillers[filler] = matches
                total_filler_instances += matches

        # 2. Multi-word and single-word discourse fillers
        for filler in self.DISCOURSE_FILLERS:
            # Special handling for 'like': only flag if redundant filler (e.g., "was like", "like fixing", "like basically")
            if filler == "like":
                # Matches 'like' when not used in comparative 'feel like', 'looks like', 'such as', 'would like'
                like_matches = len(re.findall(r'(?<!would\s)(?<!feel\s)(?<!looks\s)(?<!such\s)\blike\b(?!\sto\b)', lower))
                if like_matches > 1: # Permit 1 genuine conversational usage
                    excess_like = like_matches - 1
                    detected_fillers["like"] = excess_like
                    total_filler_instances += excess_like
            else:
                matches = len(re.findall(r'\b' + re.escape(filler) + r'\b', lower))
                if matches > 0:
                    detected_fillers[filler] = matches
                    total_filler_instances += matches

        # 3. Crutch phrases
        for crutch in self.CRUTCH_PHRASES:
            matches = len(re.findall(r'\b' + re.escape(crutch) + r'\b', lower))
            if matches > 0:
                detected_fillers[crutch] = matches
                total_filler_instances += matches

        filler_percentage = (total_filler_instances / max(1, total_words)) * 100.0

        # Scoring curve based on filler density
        if filler_percentage <= 1.5:
            score = 100.0 - (filler_percentage * 3.0)
        elif filler_percentage <= 4.0:
            score = 95.0 - ((filler_percentage - 1.5) * 8.0)
        elif filler_percentage <= 8.0:
            score = 75.0 - ((filler_percentage - 4.0) * 6.5)
        else:
            score = max(20.0, 50.0 - ((filler_percentage - 8.0) * 4.0))

        score = max(10.0, min(100.0, round(score, 1)))

        diagnostics = {
            "total_fillers": total_filler_instances,
            "filler_percentage": round(filler_percentage, 2),
            "detected_fillers": detected_fillers,
        }
        return score, detected_fillers, diagnostics


class AnswerStructureAnalyzer:
    """
    Evaluates logical framing and structural completeness.
    - Behavioral Answers: STAR Framework (Situation, Task, Action, Result)
    - Technical/General Answers: PREP Framework (Point, Reason, Example, Point)
    """

    STAR_PATTERNS = {
        "Situation": [
            r"\b(when i was at|in my previous role|during my project|at my former company|in our team|while working on)\b",
            r"\b(we were building|we faced|there was a situation|in my capstone|in my internship)\b"
        ],
        "Task": [
            r"\b(my objective was|the goal was|we needed to|my task was|the challenge was|our target was)\b",
            r"\b(responsible for|tasked with|needed to ensure|problem was)\b"
        ],
        "Action": [
            r"\b(i designed|i architected|i engineered|i implemented|i led|i decided|i resolved|i debugged)\b",
            r"\b(i refactored|i created|i introduced|i coordinated|my approach was|personally built)\b"
        ],
        "Result": [
            r"\b(which reduced|resulting in|as a result|improved by|successfully delivered|achieved|saved)\b",
            r"\b(increased by|decreased|outcome was|p99|latency|qps|percent|revenue|production)\b",
            r"\b\d+([%kmb]|ms|seconds|hours)\b"
        ]
    }

    PREP_PATTERNS = {
        "Point": [
            r"\b(in my view|i believe that|my core philosophy|the primary aspect|in general|fundamentally)\b",
            r"\b(my strength is|my approach to|i specialize in|i focus on)\b"
        ],
        "Reason": [
            r"\b(because|due to the fact|the reason is|this is critical since|underlying cause)\b",
            r"\b(this allows|to ensure that|in order to|so that)\b"
        ],
        "Example": [
            r"\b(for example|for instance|specifically|such as|in one scenario|illustrated by)\b",
            r"\b(using redis|using kafka|with pytest|in python|in go)\b"
        ],
        "Point_Summary": [
            r"\b(ultimately|in summary|in conclusion|that is why|this approach ensures|overall)\b",
            r"\b(therefore|moving forward)\b"
        ]
    }

    def analyze(self, text: str, category: HRCategory) -> Tuple[float, str, List[str], Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return 0.0, "UNSTRUCTURED", [], {"elements_matched": 0}

        lower = cleaned.lower()
        words = cleaned.split()
        total_words = len(words)

        # Detect STAR elements
        star_matched = []
        for element, patterns in self.STAR_PATTERNS.items():
            if any(re.search(p, lower) for p in patterns):
                star_matched.append(element)

        # Detect PREP elements
        prep_matched = []
        for element, patterns in self.PREP_PATTERNS.items():
            if any(re.search(p, lower) for p in patterns):
                prep_matched.append(element)

        # Decide framework relevance based on HRCategory and matches
        is_behavioral_cat = category in [
            HRCategory.CAREER_JOURNEY,
            HRCategory.TEAMWORK_AND_CULTURE_FIT,
            HRCategory.STRENGTHS_AND_WEAKNESSES,
        ]

        if len(star_matched) >= len(prep_matched) or is_behavioral_cat:
            framework = "STAR"
            matched_elements = star_matched
            match_count = len(star_matched)
            # STAR scoring (4 elements total)
            if match_count == 4:
                score = 98.0
            elif match_count == 3:
                score = 85.0
            elif match_count == 2:
                score = 70.0
            elif match_count == 1:
                score = 50.0
            else:
                score = 30.0
        else:
            framework = "PREP"
            matched_elements = prep_matched
            match_count = len(prep_matched)
            # PREP scoring (4 elements total)
            if match_count >= 3:
                score = 92.0
            elif match_count == 2:
                score = 75.0
            elif match_count == 1:
                score = 55.0
            else:
                score = 35.0

        if match_count == 0 and total_words >= 15:
            framework = "UNSTRUCTURED"
            score = 35.0

        # Terse responses cannot demonstrate structure
        if total_words < 12:
            score = min(score, 30.0)

        score = max(10.0, min(100.0, round(score, 1)))

        diagnostics = {
            "framework": framework,
            "matched_elements": matched_elements,
            "element_count": len(matched_elements),
            "star_matches": star_matched,
            "prep_matches": prep_matched,
        }
        return score, framework, matched_elements, diagnostics


class CommunicationEvaluator:
    """
    Master Day 35 Communication Skill Evaluation Engine.
    Coordinates all dimension sub-analyzers, calculates composite scores,
    and applies bias-reduction normalization.
    """

    # Baseline dimension weighting matrix
    WEIGHTS_TECHNICAL = {
        "fluency": 0.20,
        "grammar": 0.15,
        "vocabulary": 0.15,
        "clarity": 0.20,
        "filler": 0.15,
        "structure": 0.15,
    }

    WEIGHTS_NON_TECHNICAL = {
        "fluency": 0.20,
        "grammar": 0.15,
        "vocabulary": 0.20,
        "clarity": 0.15,
        "filler": 0.15,
        "structure": 0.15,
    }

    def __init__(self):
        self.fluency_analyzer = FluencyAnalyzer()
        self.grammar_analyzer = GrammarQualityAnalyzer()
        self.vocabulary_analyzer = VocabularyAnalyzer()
        self.clarity_analyzer = ClarityAnalyzer()
        self.filler_detector = FillerWordDetector()
        self.structure_analyzer = AnswerStructureAnalyzer()

    def evaluate(
        self,
        text: str,
        category: HRCategory = HRCategory.CORE_COMPETENCIES_AND_STRENGTHS if hasattr(HRCategory, "CORE_COMPETENCIES_AND_STRENGTHS") else HRCategory.STRENGTHS_AND_WEAKNESSES,
        role_track: RoleTrack = RoleTrack.TECHNICAL,
    ) -> CommunicationScoreBreakdown:
        """
        Executes complete objective communication skill evaluation on candidate utterance.
        """
        cleaned = text.strip()
        words = cleaned.split()
        word_count = len(words)

        if word_count == 0:
            return CommunicationScoreBreakdown(
                fluency_score=0.0,
                grammar_score=0.0,
                vocabulary_score=0.0,
                clarity_score=0.0,
                filler_score=100.0,
                structure_score=0.0,
                raw_composite_score=0.0,
                normalized_score=0.0,
                detected_fillers={},
                filler_count=0,
                filler_percentage=0.0,
                structure_framework="UNSTRUCTURED",
                structure_elements_detected=[],
                strengths=[],
                areas_for_improvement=["No speech response detected."],
            )

        # 1. Dimension Evaluations
        s_fluency, matched_connectors, diag_fluency = self.fluency_analyzer.analyze(cleaned)
        s_grammar, detected_errors, diag_grammar = self.grammar_analyzer.analyze(cleaned)
        s_vocab, diag_vocab = self.vocabulary_analyzer.analyze(cleaned, role_track)
        s_clarity, vague_hits, diag_clarity = self.clarity_analyzer.analyze(cleaned)
        s_filler, detected_fillers, diag_filler = self.filler_detector.analyze(cleaned)
        s_structure, framework, structure_elements, diag_structure = self.structure_analyzer.analyze(cleaned, category)

        # 2. Weighted Composite Calculation
        weights = self.WEIGHTS_TECHNICAL if role_track == RoleTrack.TECHNICAL else self.WEIGHTS_NON_TECHNICAL
        raw_composite = (
            (s_fluency * weights["fluency"]) +
            (s_grammar * weights["grammar"]) +
            (s_vocab * weights["vocabulary"]) +
            (s_clarity * weights["clarity"]) +
            (s_filler * weights["filler"]) +
            (s_structure * weights["structure"])
        )

        # 3. Bias-Reduction Normalization
        # A. ESL Non-Native Speaker Fairness Adjustment:
        # If candidate demonstrates strong structural framing (STAR/PREP >= 75) and high clarity (>= 75),
        # but uses simpler vocabulary (common in second-language speakers), grant up to +6 point equity boost
        esl_boost = 0.0
        if s_structure >= 75.0 and s_clarity >= 75.0 and s_vocab < 72.0:
            esl_boost = min(7.0, (72.0 - s_vocab) * 0.45)

        # B. Length-Invariance Scaling:
        # Prevents penalizing concise answers (25-45 words) that are structurally complete
        concise_boost = 0.0
        if 20 <= word_count <= 45 and len(structure_elements) >= 3 and s_filler >= 85.0:
            concise_boost = 5.0

        normalized_score = min(100.0, max(0.0, raw_composite + esl_boost + concise_boost))

        # 4. Synthesize Strengths and Areas for Improvement
        strengths = []
        improvements = []

        if s_fluency >= 85.0:
            strengths.append("Exceptional sentence continuity with natural discourse transitions.")
        elif s_fluency < 65.0:
            improvements.append("Improve syntactic continuity; avoid abrupt fragmented sentences.")

        if s_grammar >= 90.0:
            strengths.append("High structural grammatical precision.")
        elif detected_errors:
            improvements.append(f"Review grammatical agreement: {detected_errors[0]}.")

        if s_filler >= 90.0:
            strengths.append("Crisp speech delivery free from distracting filler words.")
        elif diag_filler["filler_percentage"] > 4.0:
            filler_names = ", ".join(f"'{k}'" for k in list(detected_fillers.keys())[:3])
            improvements.append(f"Reduce reliance on verbal fillers ({filler_names}); aim for deliberate pauses.")

        if s_structure >= 85.0:
            strengths.append(f"Strong structural narrative organization ({framework} framework).")
        elif s_structure < 65.0:
            improvements.append("Ground answers in structured STAR narrative (Situation, Task, Action, Result).")

        if s_clarity >= 85.0:
            strengths.append("Clear, substantive explanations with high idea density.")
        elif vague_hits:
            improvements.append(f"Avoid vague conversational hand-waving expressions like '{vague_hits[0]}'.")

        if not strengths:
            strengths.append("Maintains basic conversational engagement.")
        if not improvements:
            improvements.append("Continue maintaining high-clarity professional articulation.")

        return CommunicationScoreBreakdown(
            fluency_score=round(s_fluency, 1),
            grammar_score=round(s_grammar, 1),
            vocabulary_score=round(s_vocab, 1),
            clarity_score=round(s_clarity, 1),
            filler_score=round(s_filler, 1),
            structure_score=round(s_structure, 1),
            raw_composite_score=round(raw_composite, 1),
            normalized_score=round(normalized_score, 1),
            detected_fillers=detected_fillers,
            filler_count=diag_filler["total_fillers"],
            filler_percentage=round(diag_filler["filler_percentage"], 1),
            structure_framework=framework,
            structure_elements_detected=structure_elements,
            strengths=strengths,
            areas_for_improvement=improvements,
        )
