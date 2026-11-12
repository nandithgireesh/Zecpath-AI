"""
Day 41: Cross-Round Weight System & Role-Based Adjustments (Deliverable 1)
========================================================================
Defines role-based cross-round weight distributions across:
- Round 1: ATS Resume & Skill Matching
- Round 2: Conversational Pre-Screening
- Round 3: In-Depth HR Interview & Behavioral Aptitude

Features role-based auto-detection, gating thresholds, and validation rules.
"""

from typing import Dict, Optional, List
from .models import RoleFamily, RoundType, CrossRoundWeightProfile


class WeightConfigurationError(ValueError):
    """Raised when cross-round weight profile violates mathematical invariants."""
    pass


class CrossRoundWeightSystem:
    """
    Manages and calibrates cross-round weight distributions across the three evaluation phases.
    Ensures mathematical normalization (weights sum to exactly 1.0) and enforces role-specific gates.
    """

    PRESETS: Dict[RoleFamily, CrossRoundWeightProfile] = {
        RoleFamily.TECHNICAL_ENGINEERING: CrossRoundWeightProfile(
            role_family=RoleFamily.TECHNICAL_ENGINEERING,
            display_name="Technical & Engineering Track",
            ats_weight=0.25,
            screening_weight=0.30,
            hr_interview_weight=0.45,
            minimum_thresholds={
                RoundType.ATS_RESUME: 50.0,
                RoundType.CONVERSATIONAL_SCREENING: 50.0,
                RoundType.HR_INTERVIEW: 55.0,
            },
            rationale=(
                "Emphasizes deep technical reasoning, CAP theorem trade-offs, and STAR architecture "
                "in Round 3 (45%), while validating core eligibility in Round 2 (30%) and resume tech stack in Round 1 (25%)."
            ),
        ),
        RoleFamily.LEADERSHIP_MANAGEMENT: CrossRoundWeightProfile(
            role_family=RoleFamily.LEADERSHIP_MANAGEMENT,
            display_name="Leadership & Executive Management Track",
            ats_weight=0.20,
            screening_weight=0.25,
            hr_interview_weight=0.55,
            minimum_thresholds={
                RoundType.ATS_RESUME: 55.0,
                RoundType.CONVERSATIONAL_SCREENING: 60.0,
                RoundType.HR_INTERVIEW: 65.0,
            },
            rationale=(
                "Heavily weights executive presence, cross-functional consensus, blameless post-mortem ownership, "
                "and composure under crisis in Round 3 (55%), backed by foundational track record in Rounds 1 & 2."
            ),
        ),
        RoleFamily.SALES_CUSTOMER_FACING: CrossRoundWeightProfile(
            role_family=RoleFamily.SALES_CUSTOMER_FACING,
            display_name="Sales & Customer Success Track",
            ats_weight=0.15,
            screening_weight=0.40,
            hr_interview_weight=0.45,
            minimum_thresholds={
                RoundType.ATS_RESUME: 45.0,
                RoundType.CONVERSATIONAL_SCREENING: 65.0,
                RoundType.HR_INTERVIEW: 60.0,
            },
            rationale=(
                "Prioritizes conversational articulation, verbal fluency, and persuasion in screening (40%), "
                "combined with objection handling, customer empathy, and ethical negotiation in HR interview (45%)."
            ),
        ),
        RoleFamily.EARLY_CAREER_FRESHER: CrossRoundWeightProfile(
            role_family=RoleFamily.EARLY_CAREER_FRESHER,
            display_name="Early Career & Graduate Fresher Track",
            ats_weight=0.15,
            screening_weight=0.40,
            hr_interview_weight=0.45,
            minimum_thresholds={
                RoundType.ATS_RESUME: 40.0,
                RoundType.CONVERSATIONAL_SCREENING: 45.0,
                RoundType.HR_INTERVIEW: 45.0,
            },
            rationale=(
                "Reduces tenure penalty on resume ATS (15%), focusing heavily on learning agility, communication potential "
                "in screening (40%), and fundamental problem-solving curiosity in HR interview (45%)."
            ),
        ),
        RoleFamily.OPERATIONS_SUPPORT: CrossRoundWeightProfile(
            role_family=RoleFamily.OPERATIONS_SUPPORT,
            display_name="Operations & Mission-Critical Support Track",
            ats_weight=0.25,
            screening_weight=0.40,
            hr_interview_weight=0.35,
            minimum_thresholds={
                RoundType.ATS_RESUME: 50.0,
                RoundType.CONVERSATIONAL_SCREENING: 55.0,
                RoundType.HR_INTERVIEW: 50.0,
            },
            rationale=(
                "Balances procedural accuracy, SLA adherence, and incident triage communication in screening (40%) "
                "with operational stress resilience and tool familiarity in ATS (25%) and HR interview (35%)."
            ),
        ),
    }

    @classmethod
    def get_profile(cls, role_family: RoleFamily) -> CrossRoundWeightProfile:
        """Retrieves a standardized weight profile by role family."""
        if role_family in cls.PRESETS:
            return cls.PRESETS[role_family]
        return cls.PRESETS[RoleFamily.TECHNICAL_ENGINEERING]

    @classmethod
    def resolve_profile_for_role(cls, role_title: str) -> CrossRoundWeightProfile:
        """
        Auto-detects the most suitable RoleFamily and weight profile based on job role keywords.
        """
        lower = role_title.lower()

        # Sales / Customer-facing keywords (checked first to capture 'account executive')
        if any(w in lower for w in [
            "account executive", "sales executive", "sales", "business development", "bdr", "sdr",
            "customer success", "client partner", "marketing", "evangelist"
        ]):
            return cls.get_profile(RoleFamily.SALES_CUSTOMER_FACING)

        # Leadership / Executive keywords
        if any(w in lower for w in [
            "lead", "manager", "head", "director", "vp", "vice president",
            "principal", "staff architect", "chief", "executive director", "c-level", "founder"
        ]):
            return cls.get_profile(RoleFamily.LEADERSHIP_MANAGEMENT)

        # Early Career / Fresher keywords
        if any(w in lower for w in [
            "intern", "trainee", "fresher", "graduate", "junior", "associate 1",
            "entry level", "apprentice"
        ]):
            return cls.get_profile(RoleFamily.EARLY_CAREER_FRESHER)

        # Operations / Support keywords
        if any(w in lower for w in [
            "support", "operations", "sysadmin", "it specialist", "helpdesk",
            "noc engineer", "soc analyst", "service desk"
        ]):
            return cls.get_profile(RoleFamily.OPERATIONS_SUPPORT)

        # Default: Technical & Engineering
        return cls.get_profile(RoleFamily.TECHNICAL_ENGINEERING)

    @classmethod
    def create_custom_profile(
        cls,
        display_name: str,
        ats_weight: float,
        screening_weight: float,
        hr_interview_weight: float,
        minimum_thresholds: Optional[Dict[RoundType, float]] = None,
        rationale: str = "Enterprise custom weight distribution.",
    ) -> CrossRoundWeightProfile:
        """
        Constructs and validates a custom cross-round weight configuration.
        Enforces that weights sum to exactly 1.0 (tolerance 1e-4) and all weights > 0.
        """
        if any(w < 0.0 for w in [ats_weight, screening_weight, hr_interview_weight]):
            raise WeightConfigurationError("All round weights must be non-negative.")

        total_weight = ats_weight + screening_weight + hr_interview_weight
        if abs(total_weight - 1.0) > 1e-4:
            raise WeightConfigurationError(
                f"Cross-round weights must sum to exactly 1.0 (current sum: {total_weight:.4f})."
            )

        thresholds = minimum_thresholds or {
            RoundType.ATS_RESUME: 50.0,
            RoundType.CONVERSATIONAL_SCREENING: 50.0,
            RoundType.HR_INTERVIEW: 50.0,
        }

        return CrossRoundWeightProfile(
            role_family=RoleFamily.CUSTOM_ENTERPRISE,
            display_name=display_name,
            ats_weight=round(ats_weight, 4),
            screening_weight=round(screening_weight, 4),
            hr_interview_weight=round(hr_interview_weight, 4),
            minimum_thresholds=thresholds,
            rationale=rationale,
        )

    @classmethod
    def list_all_profiles(cls) -> List[CrossRoundWeightProfile]:
        """Returns all registered standard cross-round profiles."""
        return list(cls.PRESETS.values())
