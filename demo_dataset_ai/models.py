"""
Day 63: Demo Dataset & Simulation Models
Platform: Zecpath Automated Hiring Platform
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class JobDescription:
    job_id: str
    title: str
    department: str
    min_experience_years: float
    required_skills: List[str]
    preferred_skills: List[str]
    target_competencies: Dict[str, float]
    salary_range_lpa: str


@dataclass
class CandidateResume:
    candidate_id: str
    name: str
    target_role: str
    experience_years: float
    education: str
    skills: List[str]
    work_history_summary: str
    archetype: str  # HIGH_CALIBER_SENIOR, COMPETENT_MID, JUNIOR_ASPIRANT, MISMATCHED_PROFILE


@dataclass
class TurnResponseSet:
    candidate_id: str
    technical_answer: str
    behavioral_star_answer: str
    machine_test_code: str
    formulation_pause_sec: float
    hesitation_filler_count: int


@dataclass
class SimulationStageResult:
    stage_name: str
    status: str
    score: float
    metrics: Dict[str, Any]
    feedback: str


@dataclass
class FullPipelineSimulationReport:
    candidate_id: str
    candidate_name: str
    target_role: str
    archetype: str
    stages: List[SimulationStageResult]
    final_composite_score: float
    final_verdict: str  # STRONG_HIRE, OFFER, HOLD, REJECT
    adverse_impact_ratio: float
    cryptographic_seal: str
    total_execution_ms: float

