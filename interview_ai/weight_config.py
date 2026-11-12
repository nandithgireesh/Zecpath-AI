"""
Day 37: Weight Configuration System (Deliverable 2)
===================================================
Provides dynamic configuration, validation, and management of role-specific
scoring weight profiles across Answer Relevance, Communication, Confidence,
and Narrative Consistency.
"""

import json
from typing import Dict, Optional, Any
from .hr_scoring_models import WeightProfile, RoleTrackPreset, ScoringParameter


class WeightConfigurationError(ValueError):
    """Raised when weight profile violates integrity constraints."""
    pass


class WeightConfigurationSystem:
    """Enterprise Weight Configuration System for candidate scoring."""

    DEFAULT_PROFILES: Dict[str, WeightProfile] = {
        RoleTrackPreset.TECHNICAL_ROLES.value: WeightProfile(
            profile_name="Technical Engineering Track",
            answer_relevance=0.35,
            communication=0.25,
            confidence=0.20,
            consistency=0.20,
            description="Prioritizes deep technical relevance and factual problem-solving consistency."
        ),
        RoleTrackPreset.LEADERSHIP_ROLES.value: WeightProfile(
            profile_name="Engineering Leadership & Management Track",
            answer_relevance=0.30,
            communication=0.30,
            confidence=0.25,
            consistency=0.15,
            description="Emphasizes executive communication, presence, and strategic decision relevance."
        ),
        RoleTrackPreset.CLIENT_FACING_ROLES.value: WeightProfile(
            profile_name="Client-Facing & Solutions Architecture Track",
            answer_relevance=0.25,
            communication=0.35,
            confidence=0.25,
            consistency=0.15,
            description="Heavily weights consultative fluency, active persuasion, and high composure."
        ),
        RoleTrackPreset.CAMPUS_FRESHER_ROLES.value: WeightProfile(
            profile_name="Campus Graduate & Fresher Track",
            answer_relevance=0.30,
            communication=0.30,
            confidence=0.20,
            consistency=0.20,
            description="Forgiving of initial interview anxiety while valuing conceptual clarity and honesty."
        ),
        RoleTrackPreset.STANDARD_BALANCED.value: WeightProfile(
            profile_name="Standard Enterprise Balanced Track",
            answer_relevance=0.30,
            communication=0.25,
            confidence=0.25,
            consistency=0.20,
            description="Equitable default benchmark across general roles and mid-level positions."
        ),
    }

    def __init__(self):
        self._profiles: Dict[str, WeightProfile] = dict(self.DEFAULT_PROFILES)

    def get_profile(self, preset_or_role: str) -> WeightProfile:
        """Retrieves a weight profile by preset key or role heuristic. Defaults to standard balanced."""
        key = preset_or_role.lower().strip()
        if key in self._profiles:
            return self._profiles[key]

        # Heuristic role matching
        if any(w in key for w in ["lead", "manager", "director", "head", "vp", "chief", "principal"]):
            return self._profiles[RoleTrackPreset.LEADERSHIP_ROLES.value]
        if any(w in key for w in ["sales", "consultant", "account", "solutions", "customer", "partner"]):
            return self._profiles[RoleTrackPreset.CLIENT_FACING_ROLES.value]
        if any(w in key for w in ["fresher", "intern", "junior", "graduate", "trainee"]):
            return self._profiles[RoleTrackPreset.CAMPUS_FRESHER_ROLES.value]
        if any(w in key for w in ["engineer", "developer", "backend", "frontend", "devops", "architect", "data", "qa"]):
            return self._profiles[RoleTrackPreset.TECHNICAL_ROLES.value]

        return self._profiles[RoleTrackPreset.STANDARD_BALANCED.value]

    def register_custom_profile(
        self,
        profile_key: str,
        profile_name: str,
        answer_relevance: float,
        communication: float,
        confidence: float,
        consistency: float,
        description: Optional[str] = None
    ) -> WeightProfile:
        """Validates and registers a new custom weight profile."""
        profile = WeightProfile(
            profile_name=profile_name,
            answer_relevance=round(answer_relevance, 4),
            communication=round(communication, 4),
            confidence=round(confidence, 4),
            consistency=round(consistency, 4),
            description=description or f"Custom weight profile for {profile_name}"
        )

        if not profile.validate_weights():
            total = sum(profile.as_dict().values())
            raise WeightConfigurationError(
                f"Weight configuration error: parameter weights must sum to 1.0 (current sum: {total:.4f})."
            )

        self._profiles[profile_key.lower().strip()] = profile
        return profile

    def export_profiles_json(self) -> str:
        """Serializes all registered profiles into JSON string."""
        data = {k: v.model_dump() for k, v in self._profiles.items()}
        return json.dumps(data, indent=2)

    def import_profiles_json(self, json_str: str) -> int:
        """Imports and validates profiles from JSON string."""
        raw = json.loads(json_str)
        imported_count = 0
        for k, v in raw.items():
            profile = WeightProfile(**v)
            if not profile.validate_weights():
                raise WeightConfigurationError(f"Profile '{k}' failed weight validation during import.")
            self._profiles[k.lower().strip()] = profile
            imported_count += 1
        return imported_count
