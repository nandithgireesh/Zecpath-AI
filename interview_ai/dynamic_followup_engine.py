"""
Zecpath-AI: Dynamic Follow-Up Logic & Adaptive Questioning Engine (Day 34)
========================================================================
Implements real-time candidate response evaluation, ambiguity/vagueness detection,
three-tier follow-up triggering (Clarification, Deepening, Example-based),
difficulty adaptation (Simple -> Deeper Probe, Confident -> Scenario Challenge),
and anti-repetition / conversation state tracking guards.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    HRQuestionTemplate,
    FollowUpTriggerReason,
    FollowUpProbeCategory,
    AdaptationTier,
    InterviewTurnState,
    HRInterviewSession,
)


class VaguenessAmbiguityAnalyzer:
    """
    Evaluates candidate spoken utterances for ambiguity, brevity,
    lack of personal ownership, theoretical abstraction, and confidence levels.
    """

    # Hand-waving / ambiguous filler phrases
    VAGUE_MARKERS = [
        "and all", "etc", "etc.", "stuff", "things like that", "something like that",
        "basically", "somehow", "maybe", "kind of", "sort of", "around that",
        "and so on", "whatever", "like that only", "you know"
    ]

    # Conflict avoidance indicators
    CONFLICT_AVOIDANCE_PATTERNS = [
        "never had any conflict", "never had conflict", "no conflicts",
        "always agreed", "everyone agreed", "everybody agreed", "nobody disagreed",
        "we never fought", "no disagreement", "always on same page", "never argued"
    ]

    # Passive collective phrases avoiding first-person accountability
    PASSIVE_COLLECTIVE_PATTERNS = [
        "team did it", "we just did it", "we handled everything", "management took care",
        "it got done", "everyone participated", "we completed it together"
    ]

    # High-confidence action verbs and concrete impact markers
    CONFIDENT_MARKERS = [
        "architected", "engineered", "implemented", "spearheaded", "optimized",
        "reduced latency", "scaled to", "refactored", "benchmarked", "delivered",
        "owned the roadmap", "led the team", "decreased turnover", "increased revenue",
        "built", "developed", "deployed", "designed", "resolved", "debugged",
        "fastapi", "redis", "celery", "kafka", "docker", "kubernetes", "postgres",
        "percent", "%", "ms", "qps", "throughput", "p99", "sla", "kpi"
    ]

    # Concrete personal story & incident markers
    PERSONAL_STORY_MARKERS = [
        "when i", "in my project", "we faced", "i resolved", "i worked on", "during my",
        "at my previous", "i built", "i designed", "i completed", "i graduated",
        "internship", "capstone", "hackathon", "toastmasters", "for our client",
        "in our repository", "my final year", "my thesis", "memory leak", "toughest problem",
        "the problem was", "we had a bug", "incident", "outage", "resolving", "debugging"
    ]

    # Hesitation and low-confidence indicators
    HESITATION_MARKERS = [
        "i guess", "probably", "i think maybe", "not really sure", "don't know much",
        "cannot recall", "i suppose", "not sure if correct", "might be wrong"
    ]

    def analyze(self, text: str, category: HRCategory, is_technical: bool) -> Dict[str, Any]:
        """
        Analyzes candidate response and returns a structured diagnostic report.
        """
        cleaned = text.strip()
        words = cleaned.split()
        word_count = len(words)
        lower = cleaned.lower()

        # 1. Brevity check
        is_terse = word_count < 15
        is_ultra_terse = word_count < 6

        # 2. Vague marker count
        vague_hits = [m for m in self.VAGUE_MARKERS if m in lower]
        vagueness_score = min(1.0, (len(vague_hits) * 0.25) + (0.4 if is_terse else 0.0))

        # 3. Conflict avoidance
        has_conflict_avoidance = any(p in lower for p in self.CONFLICT_AVOIDANCE_PATTERNS)

        # 4. Personal agency / ownership check
        has_first_person = bool(re.search(r"\b(i|my|mine|myself|me|personally|built|led|resolved|debugged|designed)\b", lower))
        has_passive_collective = any(p in lower for p in self.PASSIVE_COLLECTIVE_PATTERNS)
        lacks_personal_agency = has_passive_collective or (not has_first_person and "we" in lower and word_count > 15)

        # 5. Pure theory detection (lacks numbers, metrics, or personal incidents)
        has_metrics = bool(re.search(r'\b\d+[kmb%]?\b', lower)) or bool(re.search(r'\bp\d+\b', lower)) or any(
            k in lower for k in ["percent", "times", "seconds", "hours", "days", "months", "years", "lpa", "users", "six-month", "three years"]
        )
        has_personal_story = any(k in lower for k in self.PERSONAL_STORY_MARKERS)
        is_pure_theory = (word_count >= 18) and not has_metrics and not has_personal_story

        # 6. Confidence scoring
        confident_hits = [
            m for m in self.CONFIDENT_MARKERS
            if (re.search(r'\b' + re.escape(m) + r'\b', lower) if len(m) <= 3 else m in lower)
        ]
        hesitation_hits = [m for m in self.HESITATION_MARKERS if m in lower]

        base_confidence = 0.5
        if word_count >= 25:
            base_confidence += 0.2
        elif is_terse:
            base_confidence -= 0.25

        base_confidence += min(0.35, len(confident_hits) * 0.12)
        base_confidence -= len(hesitation_hits) * 0.25
        base_confidence -= vagueness_score * 0.2
        confidence_score = max(0.0, min(1.0, round(base_confidence, 2)))

        # Confident responses warrant scenario challenge when they make advanced assertions with high scale/mechanisms
        has_advanced_claims = any(k in lower for k in ["scale", "throughput", "concurrency", "qps", "distributed", "outage", "turnaround", "post-acquisition", "spearheaded", "architected"])
        is_high_confidence = (confidence_score >= 0.70) and (word_count >= 16) and (vagueness_score <= 0.25) and has_advanced_claims

        # Simple response: basic, short, lacks metrics, lacks personal story, lacks technical specifics
        is_simple_response = (word_count >= 15) and (word_count <= 26) and not has_metrics and not has_personal_story and len(confident_hits) == 0

        return {
            "text": text,
            "word_count": word_count,
            "is_terse": is_terse,
            "is_ultra_terse": is_ultra_terse,
            "vagueness_score": round(vagueness_score, 2),
            "vague_hits": vague_hits,
            "has_conflict_avoidance": has_conflict_avoidance,
            "lacks_personal_agency": lacks_personal_agency,
            "is_pure_theory": is_pure_theory,
            "confidence_score": confidence_score,
            "is_high_confidence": is_high_confidence,
            "is_simple_response": is_simple_response,
        }


class DynamicFollowUpEngine:
    """
    Day 34 Dynamic Follow-Up Logic & Adaptive Questioning Engine.
    Coordinates trigger evaluation, difficulty adaptation, anti-repetition guards,
    and contextual probe synthesis.
    """

    MAX_FOLLOW_UP_DEPTH_PER_QUESTION = 1  # Strict depth guard to avoid interrogation loops

    def __init__(self):
        self.analyzer = VaguenessAmbiguityAnalyzer()
        self._init_probe_banks()

    def _init_probe_banks(self):
        """
        Initializes curated adaptive probe templates categorized by:
        ProbeCategory x RoleTrack x ExperienceTier
        """
        self.clarification_bank = {
            (RoleTrack.TECHNICAL, ExperienceTier.FRESHER): [
                "Could you clarify the core technical architecture or tools you personally utilized in that scenario?",
                "That was a bit high-level. Could you unpack the specific engineering problem and your exact contribution?",
                "Could you walk me through the step-by-step logic of how you implemented that solution?",
            ],
            (RoleTrack.TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Could you clarify the specific architectural trade-offs and constraints you navigated in that design?",
                "To ensure clarity: what was your direct scope of architectural ownership versus what the broader team delivered?",
                "Could you unpack the technical acronyms and core system parameters you just mentioned?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.FRESHER): [
                "Could you elaborate on the exact steps you took to achieve that outcome?",
                "To help us understand better: what was your specific individual role in that initiative?",
                "Could you clarify how you communicated with the other stakeholders during that situation?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Could you clarify the organizational governance or executive decision-making process behind that initiative?",
                "What was your personal leadership intervention versus existing company standard operating procedures?",
                "Could you specify the exact business KPIs and organizational impact delivered?",
            ],
        }

        self.deepening_bank = {
            (RoleTrack.TECHNICAL, ExperienceTier.FRESHER): [
                "Let's go one level deeper: how did you test and validate that code to ensure it was free from regressions?",
                "What underlying data structure or framework mechanism made that technical choice optimal?",
                "What was the most difficult bug or technical roadblock you encountered while building that, and how did you resolve it?",
            ],
            (RoleTrack.TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Let's dive into the technical depth: what failure modes, bottleneck thresholds, or concurrency race conditions did you architect for?",
                "How did you evaluate the performance implications and memory/compute trade-offs of that approach?",
                "If you had to re-architect that system today for 10x higher scale, what would you fundamentally redesign?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.FRESHER): [
                "Diving deeper: what interpersonal resistance or scheduling friction did you face, and how did you adapt?",
                "How did you measure whether your communication strategy actually resolved the underlying problem?",
                "What was the key lesson you took away from that experience regarding stakeholder expectations?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Going deeper into organizational dynamics: how did you secure cross-departmental buy-in when priorities directly conflicted?",
                "What change management friction did you encounter, and what structured governance prevented project derailment?",
                "How did you systematically track and de-risk operational failure points throughout that transformation?",
            ],
        }

        self.example_bank = {
            (RoleTrack.TECHNICAL, ExperienceTier.FRESHER): [
                "Can you walk me through a specific real-world project or lab incident where you had to apply this directly?",
                "Rather than general theory, tell me about a concrete bug you personally investigated and resolved.",
                "Can you share an actual project deliverable where this approach led to a measurable improvement?",
            ],
            (RoleTrack.TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Can you illustrate that with a real production outage, rollback, or migration incident you personally led?",
                "Could you share a concrete case study where that architectural pattern succeeded, including measurable throughput or latency metrics?",
                "Can you describe a specific time when that engineering approach failed, and what post-mortem remediation you drove?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.FRESHER): [
                "Could you share a specific situation from your college, internship, or team project where this exact dynamic occurred?",
                "Can you ground that in an actual event: what was the specific conflict, what did you do, and what was the result?",
                "Tell me about a concrete deadline you were at risk of missing, and the exact actions you took to deliver.",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Could you share a concrete business turnaround or high-stakes negotiation example demonstrating that strategy in action?",
                "Can you walk me through a specific quarter where targets were off-track, and the exact interventions you deployed?",
                "Can you describe an actual high-conflict stakeholder meeting you mediated, and the final compromise achieved?",
            ],
        }

        self.scenario_bank = {
            (RoleTrack.TECHNICAL, ExperienceTier.FRESHER): [
                "Here is a real engineering scenario: imagine your backend API suddenly starts returning HTTP 504 gateway timeouts 10 minutes before a major demo. What is your diagnostic checklist?",
                "Scenario challenge: your team lead asks you to ship a critical feature by 5 PM, but your unit tests are failing intermittently due to an async race condition. How do you handle this?",
                "Scenario: you pull latest main branch and your local dev build completely breaks due to a teammate's commit. How do you resolve this with your peer?",
            ],
            (RoleTrack.TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Scenario challenge: your core microservice experiences a 5x traffic surge during a marketing flash sale, causing Redis connection pool exhaustion and database CPU to spike to 98%. What is your immediate incident response and graceful degradation strategy?",
                "High-stakes scenario: Product Management insists on deploying a major database schema migration mid-day with zero downtime, but your primary DB replica is 15 seconds behind. How do you architect and execute this without data loss?",
                "Architecture dilemma: your senior engineer and principal architect reach a bitter deadlock over gRPC vs REST with GraphQL for your new microservice layer. How do you evaluate and arbitrate the trade-offs to drive consensus?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.FRESHER): [
                "Scenario challenge: a client or project stakeholder changes the entire project deliverable requirements 24 hours before the submission deadline. What are your immediate first 3 steps?",
                "Scenario: you discover that your teammate has submitted plagiarized work in your group presentation. How do you address this with tact and integrity?",
                "Scenario: your manager gives you two competing high-priority tasks that both must be finished by the end of today. How do you prioritize and communicate?",
            ],
            (RoleTrack.NON_TECHNICAL, ExperienceTier.EXPERIENCED): [
                "Executive scenario: two department heads (Head of Engineering and Head of Sales) are in a total deadlock over budget allocations, threatening to derail the company's Q4 OKRs. As an operations leader, how do you facilitate an executive compromise within 48 hours?",
                "Crisis scenario: a high-performing team lead under you threatens to resign immediately with their key engineers due to organizational restructuring. How do you intervene, stabilize the team, and protect business continuity?",
                "Change management scenario: your company mandates a complete migration to a new CRM/ERP platform, but senior managers are actively bypassing the system and using legacy spreadsheets. What governance framework do you enforce?",
            ],
        }

    def evaluate_and_generate_followup(
        self,
        current_question: HRQuestionTemplate,
        candidate_response: str,
        current_depth: int,
        session_history: Optional[List[InterviewTurnState]] = None,
        job_role: str = "Software Engineer",
    ) -> Tuple[bool, FollowUpTriggerReason, FollowUpProbeCategory, AdaptationTier, str, Dict[str, Any]]:
        """
        Master Decision Tree for Day 34 Dynamic Follow-Up Logic.

        Returns:
            (needs_follow_up, trigger_reason, probe_category, adaptation_tier, probe_prompt, diagnostics)
        """
        # Diagnostic analysis of candidate response
        is_tech = current_question.role_track == RoleTrack.TECHNICAL
        diag = self.analyzer.analyze(candidate_response, current_question.category, is_tech)

        track_tier_key = (current_question.role_track, current_question.experience_tier)

        # -------------------------------------------------------------
        # GUARD 1: Anti-Repetition & Max Depth Limit
        # -------------------------------------------------------------
        if current_depth >= self.MAX_FOLLOW_UP_DEPTH_PER_QUESTION:
            # Enforce depth cap: Do not trap candidate in an interrogation loop
            return (
                False,
                FollowUpTriggerReason.NONE,
                FollowUpProbeCategory.NONE,
                AdaptationTier.STANDARD,
                "",
                diag,
            )

        # -------------------------------------------------------------
        # GUARD 2: Phase Context Guards (Introduction & Closing)
        # -------------------------------------------------------------
        if current_question.phase == InterviewPhase.INTRODUCTION:
            # Introduction phase: Only probe if response was terse or excessively vague
            if not diag["is_terse"] and diag["vagueness_score"] < 0.50:
                return (
                    False,
                    FollowUpTriggerReason.NONE,
                    FollowUpProbeCategory.NONE,
                    AdaptationTier.STANDARD,
                    "",
                    diag,
                )

        if current_question.phase == InterviewPhase.CLOSING:
            # Closing phase (Career goals / Availability): Only probe if terse or vague
            if not diag["is_terse"] and diag["vagueness_score"] < 0.50:
                return (
                    False,
                    FollowUpTriggerReason.NONE,
                    FollowUpProbeCategory.NONE,
                    AdaptationTier.STANDARD,
                    "",
                    diag,
                )

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 1: Ambiguity & Terse Responses -> CLARIFICATION
        # -------------------------------------------------------------
        if diag["is_terse"] or diag["vagueness_score"] >= 0.50:
            reason = FollowUpTriggerReason.TERSE_RESPONSE if diag["is_terse"] else FollowUpTriggerReason.AMBIGUOUS_TERMS
            category = FollowUpProbeCategory.CLARIFICATION
            tier = AdaptationTier.DEEP_PROBE

            prompt = self._select_variant(
                self.clarification_bank.get(track_tier_key, []),
                session_history,
                fallback=current_question.follow_up_prompt,
            )
            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 2: Conflict Avoidance -> DEEPENING / GOVERNANCE
        # -------------------------------------------------------------
        if diag["has_conflict_avoidance"]:
            reason = FollowUpTriggerReason.CONFLICT_AVOIDANCE
            category = FollowUpProbeCategory.DEEPENING
            tier = AdaptationTier.DEEP_PROBE

            if is_tech:
                prompt = "In engineering, disagreements on architecture or code review priorities are natural and healthy. Can you walk me through a real instance where you had a constructive technical disagreement with a peer, and how you resolved it without compromising code quality?"
            else:
                prompt = "In real business environments, differing priorities between teams are inevitable. Can you share a genuine instance where you and a colleague disagreed on a timeline or decision, and what structured communication you used to find common ground?"

            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 3: Lack of Personal Agency / Ownership -> CLARIFICATION / STAR
        # -------------------------------------------------------------
        if diag["lacks_personal_agency"]:
            reason = FollowUpTriggerReason.VAGUE_CONTRIBUTION
            category = FollowUpProbeCategory.EXAMPLE_BASED
            tier = AdaptationTier.DEEP_PROBE

            prompt = "You mentioned what the broader team accomplished, but I'd like to understand your personal ownership. What was your specific individual task, decision, and deliverable in that initiative?"
            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 4: Difficulty Adaptation - High Confidence -> SCENARIO_CHALLENGE
        # -------------------------------------------------------------
        if diag["is_high_confidence"]:
            reason = FollowUpTriggerReason.HIGH_CONFIDENCE
            category = FollowUpProbeCategory.SCENARIO_CHALLENGE
            tier = AdaptationTier.SCENARIO_CHALLENGE

            prompt = self._select_variant(
                self.scenario_bank.get(track_tier_key, []),
                session_history,
                fallback="That demonstrates strong foundational grasp. Let's elevate this: how would you handle a critical system failure under peak load with incomplete data?",
            )
            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 5: Pure Theory Lacking Concrete Experience -> EXAMPLE_BASED
        # -------------------------------------------------------------
        if diag["is_pure_theory"]:
            reason = FollowUpTriggerReason.THEORETICAL_ONLY
            category = FollowUpProbeCategory.EXAMPLE_BASED
            tier = AdaptationTier.STANDARD

            prompt = self._select_variant(
                self.example_bank.get(track_tier_key, []),
                session_history,
                fallback=current_question.follow_up_prompt,
            )
            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DECISION TREE BRANCH 6: Difficulty Adaptation - Simple / Surface-level -> DEEP_PROBE
        # -------------------------------------------------------------
        if diag["is_simple_response"]:
            reason = FollowUpTriggerReason.SURFACE_LEVEL
            category = FollowUpProbeCategory.DEEPENING
            tier = AdaptationTier.DEEP_PROBE

            prompt = self._select_variant(
                self.deepening_bank.get(track_tier_key, []),
                session_history,
                fallback=current_question.follow_up_prompt,
            )
            return (True, reason, category, tier, prompt, diag)

        # -------------------------------------------------------------
        # DEFAULT: Response meets quality thresholds -> Advance turn
        # -------------------------------------------------------------
        return (
            False,
            FollowUpTriggerReason.NONE,
            FollowUpProbeCategory.NONE,
            AdaptationTier.STANDARD,
            "",
            diag,
        )

    def _select_variant(
        self,
        variants: List[str],
        session_history: Optional[List[InterviewTurnState]],
        fallback: str,
    ) -> str:
        """
        Anti-Repetition Prompt Selector:
        Selects a prompt variation that has not been dispatched in the current session.
        """
        if not variants:
            return fallback

        if not session_history:
            return variants[0]

        # Collect past prompts used in session
        past_prompts = {t.ai_prompt for t in session_history}

        for v in variants:
            if v not in past_prompts:
                return v

        # If all were somehow used, return the first variant
        return variants[0]
