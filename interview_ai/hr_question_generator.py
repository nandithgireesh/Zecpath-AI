"""
Day 33: Role-Based Question Generator & HR Question Bank
=========================================================
Implements the categorized Question Bank and adaptive question generator for:
1. Six core HR interview categories:
   - Self-introduction
   - Career journey
   - Strengths & weaknesses
   - Teamwork & culture fit
   - Career goals
   - Availability & commitment
2. Two experience tiers: Fresher vs. Experienced
3. Two role tracks: Technical vs. Non-Technical
4. Response capture and follow-up eligibility evaluator
"""

import re
from typing import List, Dict, Tuple, Optional
from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    FollowUpTriggerReason,
    HRQuestionTemplate,
    HRInterviewConfig,
)


class HRQuestionBank:
    """
    Curated repository of role- and experience-calibrated HR interview questions.
    Organized across all 6 HR categories and all 4 matrix quadrants:
      1. Fresher x Technical
      2. Fresher x Non-Technical
      3. Experienced x Technical
      4. Experienced x Non-Technical
    """

    def __init__(self):
        self._bank: List[HRQuestionTemplate] = []
        self._load_default_bank()

    def _load_default_bank(self):
        """Populates the comprehensive 24-question default question bank."""
        
        # -------------------------------------------------------------
        # 1. SELF-INTRODUCTION (Phase: INTRODUCTION)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-INTRO-F-TECH-01",
            category=HRCategory.SELF_INTRODUCTION,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.INTRODUCTION,
            prompt_text="Welcome to the interview! Could you please introduce yourself, your academic background, and what initially sparked your passion for software and technology?",
            follow_up_prompt="That's great! Could you highlight one specific technical project or coding challenge you recently enjoyed working on during your studies?",
            evaluation_criteria=["Clarity of communication", "Genuine enthusiasm for tech", "Structured self-presentation"],
            expected_competencies=["Self-awareness", "Communication", "Technical Interest"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-INTRO-F-NONTECH-01",
            category=HRCategory.SELF_INTRODUCTION,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.INTRODUCTION,
            prompt_text="Welcome! To begin our conversation, please introduce yourself, your educational background, and what motivated you to pursue a career in this field.",
            follow_up_prompt="Thank you! Could you share an extracurricular activity or college initiative that best showcases your interpersonal strengths?",
            evaluation_criteria=["Confidence", "Articulate storytelling", "Clarity of purpose"],
            expected_competencies=["Interpersonal Presence", "Initiative", "Communication"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-INTRO-E-TECH-01",
            category=HRCategory.SELF_INTRODUCTION,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.INTRODUCTION,
            prompt_text="Hello! Thank you for joining us today. Could you walk us through an executive summary of your professional background, your primary engineering domains, and what excites you about this role?",
            follow_up_prompt="Understood. What was the most technologically demanding system or architectural paradigm you spearheaded in your recent experience?",
            evaluation_criteria=["Executive presence", "Concise career synthesis", "Domain alignment"],
            expected_competencies=["Professional Maturity", "Strategic Alignment", "Communication"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-INTRO-E-NONTECH-01",
            category=HRCategory.SELF_INTRODUCTION,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.INTRODUCTION,
            prompt_text="Welcome! We're glad to connect with you. Could you share an overview of your career to date, key business milestones you've driven, and what drew you to this opportunity?",
            follow_up_prompt="Could you briefly mention the scale of business impact, team size, or revenue growth associated with that milestone?",
            evaluation_criteria=["Executive presentation", "Value proposition articulation", "Professional poise"],
            expected_competencies=["Business Acumen", "Stakeholder Presentation", "Drive"],
        ))

        # -------------------------------------------------------------
        # 2. STRENGTHS & WEAKNESSES (Phase: CORE_HR)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-STRENGTH-F-TECH-01",
            category=HRCategory.STRENGTHS_AND_WEAKNESSES,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="What do you consider your greatest personal strength when learning new programming tools, and what is one technical area you currently find challenging and are working to improve?",
            follow_up_prompt="What specific learning routine, courses, or practice habits are you using to overcome that challenge?",
            evaluation_criteria=["Honest self-awareness", "Growth mindset", "Constructive remediation plan"],
            expected_competencies=["Self-reflection", "Learning Agility", "Continuous Improvement"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-STRENGTH-F-NONTECH-01",
            category=HRCategory.STRENGTHS_AND_WEAKNESSES,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="When working on group deliverables, what personal strength do you naturally rely on most, and what is one professional area you are actively developing?",
            follow_up_prompt="Can you give an example of feedback a professor or mentor gave you that helped you recognize this area of growth?",
            evaluation_criteria=["Receptivity to feedback", "Emotional intelligence", "Self-awareness"],
            expected_competencies=["Coachability", "Self-awareness", "Resilience"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-STRENGTH-E-TECH-01",
            category=HRCategory.STRENGTHS_AND_WEAKNESSES,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="Looking back at your senior engineering tenure, what technical or leadership strength sets you apart, and what is a critical feedback point you received that shifted how you approach team deliverables?",
            follow_up_prompt="How did you operationalize that feedback across your sprint planning or code review processes?",
            evaluation_criteria=["Authentic vulnerability", "Leadership maturity", "Actionable behavior change"],
            expected_competencies=["Leadership Maturity", "Introspection", "Adaptability"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-STRENGTH-E-NONTECH-01",
            category=HRCategory.STRENGTHS_AND_WEAKNESSES,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="As a seasoned professional, what core capability enables you to consistently drive organizational results, and what is one developmental area you've had to consciously manage?",
            follow_up_prompt="How do you structure your daily operations to ensure that developmental area does not impede business outcomes?",
            evaluation_criteria=["Executive self-awareness", "Self-management systems", "Accountability"],
            expected_competencies=["Strategic Self-Awareness", "Discipline", "Accountability"],
        ))

        # -------------------------------------------------------------
        # 3. TEAMWORK & CULTURE FIT (Phase: CORE_HR)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-TEAM-F-TECH-01",
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="Tell us about a time during a college project, hackathon, or internship where team members disagreed on a technical choice or task assignment. How did you handle it?",
            follow_up_prompt="What was the final consensus reached, and what did you learn about collaboration under deadline pressure?",
            evaluation_criteria=["Conflict resolution", "Empathy", "Dedication to team outcome"],
            expected_competencies=["Collaboration", "Patience", "Team Spirit"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-TEAM-F-NONTECH-01",
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="Describe a situation where a group member was not pulling their weight or missed a deadline. How did you communicate with them and ensure the project succeeded?",
            follow_up_prompt="How did you maintain a positive interpersonal relationship with that teammate afterward?",
            evaluation_criteria=["Tactful confrontation", "Accountability", "Relationship building"],
            expected_competencies=["Diplomacy", "Accountability", "Interpersonal Sensitivity"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-TEAM-E-TECH-01",
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="Can you describe a scenario where you faced strong technical pushback from product managers or peer architects regarding an architectural trade-off? How did you bridge the gap?",
            follow_up_prompt="How did you balance long-term technical debt against immediate time-to-market business pressures in that decision?",
            evaluation_criteria=["Cross-functional alignment", "Pragmatic compromise", "Stakeholder empathy"],
            expected_competencies=["Influence without Authority", "Negotiation", "Culture Champion"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-TEAM-E-NONTECH-01",
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CORE_HR,
            prompt_text="In senior cross-departmental initiatives, conflicts frequently arise between competing priorities like sales, operations, and compliance. Can you share an example of how you navigated such conflict?",
            follow_up_prompt="What governance or communication framework did you establish to prevent recurrence?",
            evaluation_criteria=["Conflict mediation", "Strategic diplomacy", "Cultural cohesion"],
            expected_competencies=["Stakeholder Diplomacy", "Executive Alignment", "Organizational Savvy"],
        ))

        # -------------------------------------------------------------
        # 4. CAREER JOURNEY (Phase: ROLE_BASED_EVALUATION)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-JOURNEY-F-TECH-01",
            category=HRCategory.CAREER_JOURNEY,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.ROLE_BASED_EVALUATION,
            prompt_text="Looking back at your academic journey and project work, what was the most significant technical problem you independently researched and resolved?",
            follow_up_prompt="What specific debugging techniques, documentation, or developer communities did you leverage to get unstuck?",
            evaluation_criteria=["Problem-solving methodology", "Resourcefulness", "Technical curiosity"],
            expected_competencies=["Analytical Rigor", "Resourcefulness", "Perseverance"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-JOURNEY-F-NONTECH-01",
            category=HRCategory.CAREER_JOURNEY,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.ROLE_BASED_EVALUATION,
            prompt_text="Can you describe an initiative or event during your studies where you took the lead from concept to completion? What obstacles did you encounter?",
            follow_up_prompt="Looking back, is there any operational aspect you would execute differently today?",
            evaluation_criteria=["Execution ownership", "Self-critique", "Planning discipline"],
            expected_competencies=["Leadership Initiative", "Execution Drive", "Reflective Learning"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-JOURNEY-E-TECH-01",
            category=HRCategory.CAREER_JOURNEY,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.ROLE_BASED_EVALUATION,
            prompt_text="Walk us through a pivotal turning point in your engineering career where a production incident, architectural overhaul, or major migration significantly changed how you design systems.",
            follow_up_prompt="What post-mortem processes, resilience patterns, or automated testing safeguards did you institute as a result?",
            evaluation_criteria=["Production battle-testedness", "Root-cause analysis", "Engineering craftsmanship"],
            expected_competencies=["System Reliability Thinking", "Resilience Design", "Continuous Learning"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-JOURNEY-E-NONTECH-01",
            category=HRCategory.CAREER_JOURNEY,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.ROLE_BASED_EVALUATION,
            prompt_text="Could you describe a major campaign, business transformation, or organizational turnaround you led? What were the measurable outcomes?",
            follow_up_prompt="What unexpected market headwinds or operational friction did you face, and how did you pivot?",
            evaluation_criteria=["Commercial impact", "Adaptability in execution", "Strategic foresight"],
            expected_competencies=["Commercial Acumen", "Strategic Pivot", "Change Management"],
        ))

        # -------------------------------------------------------------
        # 5. CAREER GOALS (Phase: CLOSING)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-GOALS-F-TECH-01",
            category=HRCategory.CAREER_GOALS,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="Where do you see yourself developing as a software engineer over the next 2 to 3 years, and what skills are you most eager to master in our engineering environment?",
            follow_up_prompt="Are you more drawn toward technical deep-dives and systems design, or cross-functional team coordination?",
            evaluation_criteria=["Goal clarity", "Realistic ambition", "Company alignment"],
            expected_competencies=["Career Vision", "Ambition", "Role Fit"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-GOALS-F-NONTECH-01",
            category=HRCategory.CAREER_GOALS,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="What are your primary professional aspirations over the next few years, and how does this role fit into your long-term vision?",
            follow_up_prompt="What kind of mentorship or team culture do you feel would best accelerate your professional growth?",
            evaluation_criteria=["Long-term commitment", "Cultural compatibility", "Self-motivation"],
            expected_competencies=["Purposefulness", "Culture Compatibility", "Drive"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-GOALS-E-TECH-01",
            category=HRCategory.CAREER_GOALS,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="As an experienced engineer, how are you shaping your long-term career trajectory between deep technical individual contributor leadership (Staff/Principal) and engineering management?",
            follow_up_prompt="What specific challenges at our company's scale do you believe will best support that trajectory?",
            evaluation_criteria=["Strategic career clarity", "Mentorship inclination", "Long-term alignment"],
            expected_competencies=["Strategic Intentionality", "Leadership Horizon", "Retention Potential"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-GOALS-E-NONTECH-01",
            category=HRCategory.CAREER_GOALS,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="Where do you anticipate making your biggest mark over the next 3 to 5 years, and what leadership responsibilities are you looking to expand into?",
            follow_up_prompt="How do you ensure your personal growth trajectory aligns directly with organizational P&L or expansion targets?",
            evaluation_criteria=["Strategic alignment", "Visionary leadership", "Enterprise value creation"],
            expected_competencies=["Executive Ambition", "P&L Alignment", "Enterprise Vision"],
        ))

        # -------------------------------------------------------------
        # 6. AVAILABILITY & COMMITMENT (Phase: CLOSING)
        # -------------------------------------------------------------
        self._bank.append(HRQuestionTemplate(
            question_id="HR-AVAIL-F-TECH-01",
            category=HRCategory.AVAILABILITY_AND_COMMITMENT,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="To help us plan our onboarding cohort: when would you be available to join us full-time, and are you comfortable with our team's work arrangement and location?",
            follow_up_prompt="Do you have any academic semester examinations or pending project submissions that we should account for in scheduling?",
            evaluation_criteria=["Clarity of timeline", "Operational readiness", "Commitment sincerity"],
            expected_competencies=["Reliability", "Transparency", "Commitment"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-AVAIL-F-NONTECH-01",
            category=HRCategory.AVAILABILITY_AND_COMMITMENT,
            experience_tier=ExperienceTier.FRESHER,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="Could you confirm your joining availability date, and do you have any location preferences or travel readiness for client meetings?",
            follow_up_prompt="Are there any prior commitments or notice obligations we should coordinate around?",
            evaluation_criteria=["Logistical clarity", "Flexibility", "Readiness"],
            expected_competencies=["Flexibility", "Dependability", "Honesty"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-AVAIL-E-TECH-01",
            category=HRCategory.AVAILABILITY_AND_COMMITMENT,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="Could you walk us through your current contractual notice period, buyout options if applicable, and expected date of joining?",
            follow_up_prompt="Have you already initiated formal discussions with your management, or is your notice contingent on an offer in hand?",
            evaluation_criteria=["Contractual transparency", "Notice feasibility", "Professional handover discipline"],
            expected_competencies=["Professional Integrity", "Operational Reliability", "Realistic Planning"],
        ))

        self._bank.append(HRQuestionTemplate(
            question_id="HR-AVAIL-E-NONTECH-01",
            category=HRCategory.AVAILABILITY_AND_COMMITMENT,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.NON_TECHNICAL,
            phase=InterviewPhase.CLOSING,
            prompt_text="What is your contractual notice period, relocation or travel appetite, and earliest feasible start date to assume role responsibilities?",
            follow_up_prompt="Are there critical business milestones or handovers at your current organization that dictate this timeline?",
            evaluation_criteria=["Executive transition readiness", "Stakeholder handover diligence", "Commitment"],
            expected_competencies=["Transition Maturity", "Organizational Commitment", "Integrity"],
        ))

    def get_all_questions(self) -> List[HRQuestionTemplate]:
        """Returns all 24 curated questions across categories."""
        return list(self._bank)

    def filter_questions(
        self,
        experience_tier: Optional[ExperienceTier] = None,
        role_track: Optional[RoleTrack] = None,
        category: Optional[HRCategory] = None,
    ) -> List[HRQuestionTemplate]:
        """Filters questions by experience tier, role track, and/or category."""
        results = self._bank
        if experience_tier is not None:
            results = [q for q in results if q.experience_tier == experience_tier]
        if role_track is not None:
            results = [q for q in results if q.role_track == role_track]
        if category is not None:
            results = [q for q in results if q.category == category]
        return list(results)

    def find_question(
        self,
        category: HRCategory,
        experience_tier: ExperienceTier,
        role_track: RoleTrack,
    ) -> Optional[HRQuestionTemplate]:
        """Retrieves exact matching question template for a category and candidate quadrant."""
        for q in self._bank:
            if (
                q.category == category
                and q.experience_tier == experience_tier
                and q.role_track == role_track
            ):
                return q
        return None


class HRQuestionGenerator:
    """
    Adaptive question generator and response evaluator.
    Selects structured question sequences and evaluates follow-up probing eligibility.
    """

    def __init__(self, bank: Optional[HRQuestionBank] = None):
        self.bank = bank or HRQuestionBank()

    def generate_interview_plan(self, config: HRInterviewConfig) -> List[HRQuestionTemplate]:
        """
        Builds a structured 6-question path spanning all 4 phases and 6 HR categories:
          Phase 1: INTRODUCTION -> SELF_INTRODUCTION
          Phase 2: CORE_HR -> STRENGTHS_AND_WEAKNESSES, TEAMWORK_AND_CULTURE_FIT
          Phase 3: ROLE_BASED_EVALUATION -> CAREER_JOURNEY
          Phase 4: CLOSING -> CAREER_GOALS, AVAILABILITY_AND_COMMITMENT
        """
        planned_categories = [
            HRCategory.SELF_INTRODUCTION,
            HRCategory.STRENGTHS_AND_WEAKNESSES,
            HRCategory.TEAMWORK_AND_CULTURE_FIT,
            HRCategory.CAREER_JOURNEY,
            HRCategory.CAREER_GOALS,
            HRCategory.AVAILABILITY_AND_COMMITMENT,
        ]

        script: List[HRQuestionTemplate] = []
        for cat in planned_categories:
            q = self.bank.find_question(
                category=cat,
                experience_tier=config.experience_tier,
                role_track=config.role_track,
            )
            if q:
                script.append(q)

        return script

    def evaluate_follow_up_eligibility(
        self,
        question: HRQuestionTemplate,
        candidate_response: str,
    ) -> Tuple[bool, FollowUpTriggerReason]:
        """
        Analyzes the candidate's spoken response to determine whether an adaptive follow-up
        is required before moving to the next category.
        
        Triggers:
        1. TERSE_RESPONSE: Less than 15 words.
        2. SURFACE_LEVEL: Contains generic buzzwords without substantive details.
        3. VAGUE_CONTRIBUTION: Over-indexes on "we" without specifying personal role (for experienced).
        4. CONFLICT_AVOIDANCE: Explicitly states they never faced conflict or challenge.
        """
        cleaned = candidate_response.strip()
        words = re.findall(r'\b\w+\b', cleaned)
        word_count = len(words)
        lower_resp = cleaned.lower()

        # 1. Terse Answer Gate
        if word_count < 15:
            return True, FollowUpTriggerReason.TERSE_RESPONSE

        # 2. Conflict Avoidance Gate (for Teamwork & Strengths)
        if question.category in (HRCategory.TEAMWORK_AND_CULTURE_FIT, HRCategory.STRENGTHS_AND_WEAKNESSES):
            avoidance_patterns = [
                "never had any conflict", "never disagreed", "no conflict ever",
                "everything was always smooth", "we never had issues", "i don't have weaknesses",
                "no weakness", "never failed"
            ]
            if any(p in lower_resp for p in avoidance_patterns):
                return True, FollowUpTriggerReason.CONFLICT_AVOIDANCE

        # 3. Vague Contribution Gate (for Experienced candidates on Career Journey)
        if question.category == HRCategory.CAREER_JOURNEY and question.experience_tier == ExperienceTier.EXPERIENCED:
            # If they speak in abstract plural "we did" without "I", "my", "designed", "led", "implemented"
            personal_pronouns = {"i", "my", "me", "personally", "myself", "architected", "led", "spearheaded", "built"}
            has_personal = any(p in words for p in personal_pronouns)
            if not has_personal and word_count < 35:
                return True, FollowUpTriggerReason.VAGUE_CONTRIBUTION

        # 4. Surface Level Gate (generic short responses)
        generic_platitudes = ["i am hardworking", "i am a quick learner", "i like technology", "good team player"]
        if word_count < 22 and any(p in lower_resp for p in generic_platitudes):
            return True, FollowUpTriggerReason.SURFACE_LEVEL

        return False, FollowUpTriggerReason.NONE
