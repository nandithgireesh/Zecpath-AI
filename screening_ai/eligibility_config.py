from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class EligibilityRuleConfig:
    """
    Recruiter-configurable eligibility rule parameters per job role.
    """
    role_name: str = "General Role"
    min_ats_score: float = 70.0
    review_ats_score: float = 55.0
    mandatory_skills: List[str] = field(default_factory=list)
    min_experience_years: float = 0.0
    max_experience_years: Optional[float] = None
    allowed_locations: List[str] = field(default_factory=list)
    max_notice_period_days: Optional[int] = None
    allow_remote: bool = True
    required_education_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_name": self.role_name,
            "min_ats_score": self.min_ats_score,
            "review_ats_score": self.review_ats_score,
            "mandatory_skills": self.mandatory_skills,
            "min_experience_years": self.min_experience_years,
            "max_experience_years": self.max_experience_years,
            "allowed_locations": self.allowed_locations,
            "max_notice_period_days": self.max_notice_period_days,
            "allow_remote": self.allow_remote,
            "required_education_keywords": self.required_education_keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EligibilityRuleConfig":
        if not data:
            return cls()
        return cls(
            role_name=data.get("role_name", "General Role"),
            min_ats_score=float(data.get("min_ats_score", 70.0)),
            review_ats_score=float(data.get("review_ats_score", 55.0)),
            mandatory_skills=[s.strip() for s in data.get("mandatory_skills", []) if s],
            min_experience_years=float(data.get("min_experience_years", 0.0)),
            max_experience_years=(
                float(data["max_experience_years"])
                if data.get("max_experience_years") is not None
                else None
            ),
            allowed_locations=[loc.strip() for loc in data.get("allowed_locations", []) if loc],
            max_notice_period_days=(
                int(data["max_notice_period_days"])
                if data.get("max_notice_period_days") is not None
                else None
            ),
            allow_remote=bool(data.get("allow_remote", True)),
            required_education_keywords=[
                k.strip() for k in data.get("required_education_keywords", []) if k
            ],
        )


# =========================================================
# Standard Role Rule Templates
# =========================================================

DEFAULT_ROLE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "MERN Stack Developer": {
        "role_name": "MERN Stack Developer",
        "min_ats_score": 70.0,
        "review_ats_score": 55.0,
        "mandatory_skills": ["React", "Node.js", "MongoDB", "JavaScript"],
        "min_experience_years": 1.0,
        "max_experience_years": 5.0,
        "allowed_locations": ["Bangalore", "Kerala", "Remote", "Kochi"],
        "max_notice_period_days": 30,
        "allow_remote": True,
        "required_education_keywords": ["B.Tech", "BE", "BSc", "BCA", "MCA"],
    },
    "Machine Learning Engineer": {
        "role_name": "Machine Learning Engineer",
        "min_ats_score": 75.0,
        "review_ats_score": 60.0,
        "mandatory_skills": ["Python", "TensorFlow", "Pandas", "Machine Learning"],
        "min_experience_years": 1.0,
        "max_experience_years": 6.0,
        "allowed_locations": ["Bangalore", "Hyderabad", "Remote"],
        "max_notice_period_days": 60,
        "allow_remote": True,
        "required_education_keywords": ["B.Tech", "M.Tech", "Computer Science", "Artificial Intelligence"],
    },
    "Fresher Software Engineer": {
        "role_name": "Fresher Software Engineer",
        "min_ats_score": 60.0,
        "review_ats_score": 45.0,
        "mandatory_skills": ["Python", "SQL"],
        "min_experience_years": 0.0,
        "max_experience_years": 1.5,
        "allowed_locations": ["Any", "Remote"],
        "max_notice_period_days": 15,
        "allow_remote": True,
        "required_education_keywords": ["B.Tech", "BE", "BCA", "BSc", "MCA"],
    },
}


def get_rule_config_for_role(role_name: str) -> EligibilityRuleConfig:
    """
    Retrieve rule configuration for a specific role or return default.
    """
    normalized_name = role_name.strip() if role_name else ""
    for known_role, template in DEFAULT_ROLE_TEMPLATES.items():
        if known_role.lower() in normalized_name.lower() or normalized_name.lower() in known_role.lower():
            return EligibilityRuleConfig.from_dict(template)
    
    return EligibilityRuleConfig(role_name=role_name or "General Role")
