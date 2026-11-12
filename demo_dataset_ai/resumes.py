"""
Day 63: Varied Quality Candidate Resumes Dataset
Platform: Zecpath Automated Hiring Platform
"""

from typing import Dict, List
from demo_dataset_ai.models import CandidateResume

CURATED_CANDIDATE_RESUMES: Dict[str, CandidateResume] = {
    "CAND-ARCH-01": CandidateResume(
        candidate_id="CAND-ARCH-01",
        name="Aditi Rao",
        target_role="Senior Backend Systems Architect",
        experience_years=7.5,
        education="M.Tech in Distributed Systems, IIT Bombay",
        skills=["Python", "FastAPI", "Kubernetes", "Kafka", "PostgreSQL", "Docker", "Redis", "gRPC"],
        work_history_summary=(
            "Principal Platform Engineer at FinTech Global. Designed event-driven payment reconciliation "
            "pipeline processing 45,000 TPS on Apache Kafka with sub-25ms P99 latency. Implemented Kubernetes "
            "multi-AZ clusters with automated failover and zero data loss."
        ),
        archetype="HIGH_CALIBER_SENIOR",
    ),
    "CAND-MID-02": CandidateResume(
        candidate_id="CAND-MID-02",
        name="Rohan Verma",
        target_role="Senior Backend Systems Architect",
        experience_years=4.0,
        education="B.Tech in Computer Science, NIT Trichy",
        skills=["Python", "FastAPI", "Docker", "PostgreSQL", "REST APIs", "Git"],
        work_history_summary=(
            "Software Engineer at SaaS Logistics. Built asynchronous task queues using Celery and Redis. "
            "Migrated legacy monolithic endpoints to FastAPI microservices, reducing API response times by 35%."
        ),
        archetype="COMPETENT_MID",
    ),
    "CAND-JUNIOR-03": CandidateResume(
        candidate_id="CAND-JUNIOR-03",
        name="Kavita Menon",
        target_role="Senior Backend Systems Architect",
        experience_years=1.2,
        education="B.Sc in Information Technology",
        skills=["Python", "HTML", "CSS", "Basic SQL", "Flask"],
        work_history_summary=(
            "Junior Developer Intern at WebTech Solutions. Assisted in building small internal Flask tools "
            "and writing automated unit test scripts. Managed basic CRUD operations on SQLite."
        ),
        archetype="JUNIOR_ASPIRANT",
    ),
    "CAND-MISMATCH-04": CandidateResume(
        candidate_id="CAND-MISMATCH-04",
        name="Vikram Singh",
        target_role="Senior Backend Systems Architect",
        experience_years=6.0,
        education="B.A. in Graphic Design & Digital Media",
        skills=["Adobe Photoshop", "Illustrator", "Figma", "WordPress", "UI/UX Prototyping"],
        work_history_summary=(
            "Lead Visual Designer at Creative Spark. Directed brand identity, marketing collaterals, and "
            "WordPress portal layouts for consumer enterprise clients."
        ),
        archetype="MISMATCHED_PROFILE",
    ),
}

