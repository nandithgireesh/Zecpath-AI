"""
Day 63: Curated Job Descriptions Dataset
Platform: Zecpath Automated Hiring Platform
"""

from typing import Dict, List
from demo_dataset_ai.models import JobDescription

CURATED_JOB_DESCRIPTIONS: Dict[str, JobDescription] = {
    "JOB-BACKEND-SR": JobDescription(
        job_id="JOB-BACKEND-SR",
        title="Senior Backend Systems Architect",
        department="Core Infrastructure Engineering",
        min_experience_years=5.0,
        required_skills=["Python", "FastAPI", "Docker", "PostgreSQL", "Kubernetes", "Kafka"],
        preferred_skills=["Distributed Systems", "Redis", "gRPC", "CI/CD", "AWS"],
        target_competencies={
            "system_design": 0.40,
            "code_quality": 0.30,
            "communication": 0.15,
            "problem_solving": 0.15,
        },
        salary_range_lpa="32 - 45 LPA",
    ),
    "JOB-DEVOPS-LEAD": JobDescription(
        job_id="JOB-DEVOPS-LEAD",
        title="Lead Cloud & Site Reliability Engineer",
        department="Platform Reliability & Operations",
        min_experience_years=6.0,
        required_skills=["Kubernetes", "Terraform", "Docker", "AWS", "Prometheus", "CI/CD"],
        preferred_skills=["Linux Kernel", "Helm", "Kafka", "Python", "Grafana"],
        target_competencies={
            "cloud_architecture": 0.45,
            "incident_response": 0.25,
            "automation": 0.20,
            "security": 0.10,
        },
        salary_range_lpa="35 - 50 LPA",
    ),
    "JOB-FULLSTACK-MID": JobDescription(
        job_id="JOB-FULLSTACK-MID",
        title="Fullstack Product Engineer",
        department="Product Applications",
        min_experience_years=2.5,
        required_skills=["React", "TypeScript", "Python", "REST APIs", "PostgreSQL"],
        preferred_skills=["TailwindCSS", "Next.js", "Docker", "GraphQL"],
        target_competencies={
            "frontend_ui": 0.35,
            "backend_api": 0.35,
            "clean_code": 0.20,
            "speed": 0.10,
        },
        salary_range_lpa="18 - 26 LPA",
    ),
}

