"""
Day 28: Sample Screening Reports Generator
==========================================
Provides 4 diverse, realistic candidate screening reports demonstrating all
recommendation tiers (STRONG_HIRE, HIRE, PROCEED_WITH_CAUTION, NO_HIRE) and edge cases.
"""

from typing import List, Dict
from .report_models import ScreeningReport, HiringRecommendation
from .report_builder import ScreeningReportBuilder


def generate_sample_reports() -> Dict[str, ScreeningReport]:
    """Generates 4 diverse, production-fidelity sample screening reports."""
    builder = ScreeningReportBuilder()
    reports = {}

    # -------------------------------------------------------------------------
    # Sample 1: Senior Cloud & Backend Architect (STRONG_HIRE)
    # -------------------------------------------------------------------------
    s1_evaluations = [
        {
            "question_id": "Q1",
            "question_category": "Technical",
            "question_text": "How do you design an event-driven system handling 50,000 requests per second?",
            "raw_answer": "We decoupled ingest with Apache Kafka partitions, processed via Go worker pools with Redis caching, and persisted asynchronously to PostgreSQL.",
            "weighted_question_score": 96.0,
            "grade": "EXCELLENT",
            "strengths": ["Demonstrated deep understanding of Kafka partitioning and asynchronous write-back."],
            "explanation": "Clear, concise architecture walkthrough covering backpressure and caching.",
            "relevance_score": 95.0,
        },
        {
            "question_id": "Q2",
            "question_category": "System Design",
            "question_text": "Explain your approach to database connection pooling and failover in Kubernetes.",
            "raw_answer": "We deploy PgBouncer sidecars in Kubernetes to manage pooling and run CrunchyData Postgres operator for automated patroni-based leader failover.",
            "weighted_question_score": 94.0,
            "grade": "EXCELLENT",
            "strengths": ["Strong production expertise with PgBouncer and automated stateful operators."],
            "explanation": "Authoritative explanation of connection management in ephemeral environments.",
            "relevance_score": 95.0,
        },
        {
            "question_id": "Q3",
            "question_category": "Experience",
            "question_text": "Describe a major production outage you resolved under pressure.",
            "raw_answer": "During Black Friday, Redis memory spiked causing connection timeouts. I triaged using Grafana metrics, scaled the cluster shards, and patched an unindexed cache key.",
            "weighted_question_score": 92.0,
            "grade": "EXCELLENT",
            "strengths": ["Calm incident response mindset and data-driven observability approach."],
            "explanation": "Effective root cause analysis and proactive mitigation.",
            "relevance_score": 90.0,
        },
    ]

    r1 = builder.build_report(
        candidate_id="CAND-901",
        candidate_name="Aarav Sharma",
        job_id="JOB-CLOUD-01",
        role_name="Senior Cloud & Backend Architect",
        candidate_data={
            "current_ctc_lpa": 22.0,
            "expected_ctc_lpa": 26.0,
            "ctc_negotiable": True,
            "notice_period_days": 30,
            "is_immediate_joiner": False,
            "earliest_start_date": "Within 30 days of offer",
            "current_location": "Bengaluru, India",
            "skills_confirmed": ["Python", "Go", "Kubernetes", "AWS", "Kafka", "PostgreSQL", "Redis", "Docker"],
        },
        question_evaluations=s1_evaluations,
        role_mandatory_skills=["Python", "Kubernetes", "AWS", "Kafka", "PostgreSQL"],
        role_bonus_skills=["Go", "Redis"],
        budget_max_lpa=30.0,
        budget_min_lpa=24.0,
        max_acceptable_notice_days=60,
        behavioral_summary={
            "communication_score": 92.0,
            "confidence_score": 96.0,
            "average_wpm": 146.0,
            "sentiment": "POSITIVE",
            "is_defensive": False,
        },
    )
    reports["sample_1_strong_hire"] = r1

    # -------------------------------------------------------------------------
    # Sample 2: Lead Platform & DevOps Engineer (HIRE)
    # -------------------------------------------------------------------------
    s2_evaluations = [
        {
            "question_id": "Q1",
            "question_category": "Technical",
            "question_text": "Walk me through how you implement zero-downtime canary deployments in Kubernetes.",
            "raw_answer": "We use Argo Rollouts integrated with Prometheus metrics to shift 10% traffic, monitor HTTP 5xx rates, and promote automatically.",
            "weighted_question_score": 86.0,
            "grade": "STRONG",
            "strengths": ["Hands-on GitOps experience with Argo Rollouts."],
            "explanation": "Solid explanation of automated metrics analysis and traffic shifting.",
            "relevance_score": 88.0,
        },
        {
            "question_id": "Q2",
            "question_category": "Technical",
            "question_text": "How do you enforce security guardrails in your Terraform infrastructure as code?",
            "raw_answer": "We enforce OPA tfsec checks and Checkov in our GitHub Actions pipeline, blocking PRs that fail CIS benchmarks.",
            "weighted_question_score": 84.0,
            "grade": "STRONG",
            "strengths": ["Strong DevSecOps posture using policy as code."],
            "explanation": "Practical implementation of shift-left security.",
            "relevance_score": 85.0,
        },
    ]

    r2 = builder.build_report(
        candidate_id="CAND-902",
        candidate_name="Priya Nair",
        job_id="JOB-DEVOPS-02",
        role_name="Lead Platform & DevOps Engineer",
        candidate_data={
            "current_ctc_lpa": 19.5,
            "expected_ctc_lpa": 24.0,
            "ctc_negotiable": True,
            "notice_period_days": 45,
            "is_immediate_joiner": False,
            "earliest_start_date": "Within 45 days",
            "current_location": "Hyderabad, India",
            "skills_confirmed": ["Terraform", "Docker", "Kubernetes", "AWS", "CI/CD", "Prometheus"],
        },
        question_evaluations=s2_evaluations,
        role_mandatory_skills=["Terraform", "Kubernetes", "AWS", "CI/CD"],
        role_bonus_skills=["ArgoCD", "Python"],
        budget_max_lpa=24.0,
        budget_min_lpa=20.0,
        max_acceptable_notice_days=60,
        behavioral_summary={
            "communication_score": 82.0,
            "confidence_score": 85.0,
            "average_wpm": 138.0,
            "sentiment": "POSITIVE",
            "is_defensive": False,
        },
    )
    reports["sample_2_hire"] = r2

    # -------------------------------------------------------------------------
    # Sample 3: Fullstack React / Python Developer (PROCEED_WITH_CAUTION)
    # -------------------------------------------------------------------------
    s3_evaluations = [
        {
            "question_id": "Q1",
            "question_category": "Technical",
            "question_text": "Explain how you optimize rendering performance in large React applications.",
            "raw_answer": "I use React.memo, useMemo, useCallback, and implement virtualized lists with react-window to avoid unnecessary re-renders.",
            "weighted_question_score": 82.0,
            "grade": "STRONG",
            "strengths": ["Good understanding of React virtual DOM optimization."],
            "explanation": "Solid frontend competency.",
            "relevance_score": 85.0,
        },
        {
            "question_id": "Q2",
            "question_category": "Technical",
            "question_text": "How do you scale database read and write traffic in Django/Python?",
            "raw_answer": "Um... well... I think we used multiple database routers, but mostly my senior team handled the sharding and replication logic.",
            "weighted_question_score": 58.0,
            "grade": "MODERATE",
            "strengths": ["Honest acknowledgment of team role."],
            "explanation": "Superficial backend knowledge with noticeable hesitation and epistemic hedging.",
            "relevance_score": 65.0,
        },
    ]

    r3 = builder.build_report(
        candidate_id="CAND-903",
        candidate_name="Rohan Varma",
        job_id="JOB-FULLSTACK-03",
        role_name="Fullstack Software Engineer",
        candidate_data={
            "current_ctc_lpa": 12.0,
            "expected_ctc_lpa": 16.0,
            "ctc_negotiable": True,
            "notice_period_days": 90,  # Long notice period
            "is_immediate_joiner": False,
            "current_location": "Pune, India",
            "skills_confirmed": ["React", "TypeScript", "Python", "Django", "PostgreSQL"],
        },
        question_evaluations=s3_evaluations,
        role_mandatory_skills=["React", "Python", "Docker", "AWS"],  # Docker and AWS missing
        role_bonus_skills=["TypeScript"],
        budget_max_lpa=14.0,  # Over budget (16 vs 14)
        budget_min_lpa=11.0,
        max_acceptable_notice_days=60,
        behavioral_summary={
            "communication_score": 68.0,
            "confidence_score": 64.0,
            "average_wpm": 125.0,
            "sentiment": "NEUTRAL",
            "is_defensive": False,
        },
    )
    reports["sample_3_proceed_with_caution"] = r3

    # -------------------------------------------------------------------------
    # Sample 4: Evading / High-Risk Candidate (NO_HIRE)
    # -------------------------------------------------------------------------
    s4_evaluations = [
        {
            "question_id": "Q1",
            "question_category": "Technical",
            "question_text": "How do you handle API rate limiting and DDoS protection at the gateway level?",
            "raw_answer": "Why are you asking me these theoretical questions? Everything is in my resume, you can just read that.",
            "weighted_question_score": 30.0,
            "grade": "UNSATISFACTORY",
            "strengths": [],
            "explanation": "Combative and defensive response; complete refusal to demonstrate technical competence.",
            "relevance_score": 25.0,
        },
        {
            "question_id": "Q2",
            "question_category": "Experience",
            "question_text": "Can you describe a challenge you faced during database migration?",
            "raw_answer": "I don't remember, that was done long back by another contractor.",
            "weighted_question_score": 42.0,
            "grade": "POOR",
            "strengths": [],
            "explanation": "Evasive answer showing no ownership or accountability.",
            "relevance_score": 45.0,
        },
    ]

    r4 = builder.build_report(
        candidate_id="CAND-904",
        candidate_name="Vikram Malhotra",
        job_id="JOB-BACKEND-04",
        role_name="Senior Backend Engineer",
        candidate_data={
            "current_ctc_lpa": None,
            "expected_ctc_lpa": None,  # Undisclosed
            "ctc_negotiable": False,
            "notice_period_days": None,  # Missing
            "is_immediate_joiner": False,
            "current_location": None,
            "skills_confirmed": ["Java"],
        },
        question_evaluations=s4_evaluations,
        role_mandatory_skills=["Python", "Microservices", "Kafka", "AWS"],
        role_bonus_skills=["Java"],
        budget_max_lpa=25.0,
        budget_min_lpa=18.0,
        max_acceptable_notice_days=60,
        behavioral_summary={
            "communication_score": 45.0,
            "confidence_score": 52.0,
            "average_wpm": 105.0,
            "sentiment": "DEFENSIVE",
            "is_defensive": True,
            "defensive_quotes": ["Why are you asking me these theoretical questions?"],
        },
    )
    reports["sample_4_no_hire"] = r4

    return reports
