"""
Zecpath AI Automated Hiring Platform
Day 63: Demo Dataset & Simulation Environment Package
"""

from demo_dataset_ai.models import (
    JobDescription,
    CandidateResume,
    TurnResponseSet,
    SimulationStageResult,
    FullPipelineSimulationReport,
)
from demo_dataset_ai.job_descriptions import CURATED_JOB_DESCRIPTIONS
from demo_dataset_ai.resumes import CURATED_CANDIDATE_RESUMES
from demo_dataset_ai.candidate_responses import CURATED_CANDIDATE_RESPONSES
from demo_dataset_ai.simulation_environment import EndToEndSimulationEnvironment

__all__ = [
    "JobDescription",
    "CandidateResume",
    "TurnResponseSet",
    "SimulationStageResult",
    "FullPipelineSimulationReport",
    "CURATED_JOB_DESCRIPTIONS",
    "CURATED_CANDIDATE_RESUMES",
    "CURATED_CANDIDATE_RESPONSES",
    "EndToEndSimulationEnvironment",
]

