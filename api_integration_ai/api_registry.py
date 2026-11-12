"""
Day 59: API & Integration Planning - API Registry & Subsystem Mapping
=====================================================================
Platform: Zecpath Enterprise Automated Hiring Platform
Catalogs all 5 AI APIs, their protocol specifications, processing modes,
and maps the Backend -> AI -> Database interaction flow.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from .models import ProcessingMode, AuthScheme


@dataclass
class APIEndpointMetadata:
    endpoint_id: str
    route_path: str
    http_method: str
    ai_subsystem: str
    processing_mode: ProcessingMode
    sla_target: str
    auth_scheme: AuthScheme
    idempotency_required: bool
    backend_trigger: str
    ai_core_engine: str
    database_destination: str
    description: str


class APICatalogRegistry:
    """
    Central catalog defining the 5 mandated AI APIs and mapping
    backend -> AI -> database interaction topology.
    """

    @staticmethod
    def get_registered_apis() -> List[APIEndpointMetadata]:
        return [
            APIEndpointMetadata(
                endpoint_id="API-01-RESUME-PARSE",
                route_path="/api/v1/ai/resume/parse",
                http_method="POST",
                ai_subsystem="RESUME_PARSER_AI",
                processing_mode=ProcessingMode.ASYNC,
                sla_target="< 3.0 Seconds (P95)",
                auth_scheme=AuthScheme.BEARER_JWT,
                idempotency_required=True,
                backend_trigger="Candidate document upload on portal / webhook ingestion",
                ai_core_engine="parsers.resume_parser & parsers.academic_profile",
                database_destination="PostgreSQL ('candidate_resumes', 'parsed_skills') & S3 Vault",
                description="Accepts document URL, queues background parsing worker, extracts structured skills, experience, and academic profile with PII tokenization."
            ),
            APIEndpointMetadata(
                endpoint_id="API-02-ATS-SCORE",
                route_path="/api/v1/ai/ats/score",
                http_method="POST",
                ai_subsystem="ATS_SCORING_AI",
                processing_mode=ProcessingMode.ASYNC,
                sla_target="< 1.5 Seconds (P95)",
                auth_scheme=AuthScheme.BEARER_JWT,
                idempotency_required=True,
                backend_trigger="Recruiter creates shortlist batch / post-parsing event trigger",
                ai_core_engine="parsers.semantic_matching_engine & parsers.similarity_scorer",
                database_destination="PostgreSQL ('ats_evaluations', 'job_requisitions')",
                description="Computes semantic vector compatibility, keyword coverage (50%), experience fit (35%), and format hygiene (15%)."
            ),
            APIEndpointMetadata(
                endpoint_id="API-03-SCREENING-AI",
                route_path="/api/v1/ai/screening/utterance",
                http_method="POST",
                ai_subsystem="SCREENING_AI",
                processing_mode=ProcessingMode.SYNC,
                sla_target="< 80 ms (P99)",
                auth_scheme=AuthScheme.BEARER_JWT,
                idempotency_required=False,
                backend_trigger="Candidate voice/text utterance received during screening call",
                ai_core_engine="screening_ai.call_flow_engine & screening_ai.eligibility_engine",
                database_destination="Redis ('screening_active_sessions') & PostgreSQL ('screening_transcripts')",
                description="Real-time intent classification, prerequisite verification (notice period, visa), and dynamic follow-up generation."
            ),
            APIEndpointMetadata(
                endpoint_id="API-04-INTERVIEW-AI",
                route_path="/api/v1/ai/interview/turn",
                http_method="POST",
                ai_subsystem="INTERVIEW_AI",
                processing_mode=ProcessingMode.SYNC,
                sla_target="< 50 ms (P99)",
                auth_scheme=AuthScheme.BEARER_JWT,
                idempotency_required=False,
                backend_trigger="Real-time candidate answer submission or code sandbox execution",
                ai_core_engine="interview_ai.dynamic_followup_engine & tech_interview.code_sandbox",
                database_destination="Redis ('interview_turn_cache') & PostgreSQL ('interview_scores')",
                description="Evaluates technical code execution safety, behavioral STAR compliance, and emits sub-50ms pacing micro-prompts."
            ),
            APIEndpointMetadata(
                endpoint_id="API-05-DECISION-AI",
                route_path="/api/v1/ai/decision/arbitrate",
                http_method="POST",
                ai_subsystem="DECISION_AI",
                processing_mode=ProcessingMode.SYNC,
                sla_target="< 40 ms (P99)",
                auth_scheme=AuthScheme.HMAC_SHA256,
                idempotency_required=True,
                backend_trigger="Completion of all assessment rounds triggering final hiring arbitration",
                ai_core_engine="cross_round_engine.arbitrator & final_recommendation_ai",
                database_destination="PostgreSQL ('final_hiring_decisions') & SHA-256 Chained Audit Vault",
                description="Synthesizes cross-round scores via Bayesian variance damping, enforces hard technical floor (50%), and generates immutable hire/reject verdict."
            )
        ]

    @staticmethod
    def get_backend_interaction_topology() -> Dict[str, Any]:
        """
        Maps the end-to-end Backend -> AI -> Database data flow architecture.
        """
        return {
            "gateway_layer": {
                "technologies": ["Kong API Gateway", "FastAPI Edge Router", "Redis Rate Limiter"],
                "responsibilities": ["TLS Termination", "JWT / HMAC Auth Validation", "Rate Limiting", "Idempotency Dedup"]
            },
            "async_message_broker": {
                "technologies": ["Celery Distributed Task Queue", "Redis Broker", "RabbitMQ / Kafka"],
                "queue_names": ["resume_parsing_queue", "ats_scoring_queue", "dead_letter_queue_dlq"],
                "retry_policy": "Exponential Backoff (1s, 2s, 4s, 8s) with Max 3 Retries"
            },
            "sync_realtime_bus": {
                "technologies": ["WebSockets SFU", "gRPC Internal Microservices", "Redis In-Memory Pub/Sub"],
                "latency_budget": "Total turnaround < 85ms end-to-end"
            },
            "persistence_layer": {
                "relational_db": "PostgreSQL 16 (Candidates, Requisitions, Scores, Transcripts)",
                "in_memory_cache": "Redis 7.2 (Active Sessions, Token Buckets, Idempotency Keys)",
                "artifact_vault": "AWS S3 / Encrypted Vault (AES-256-GCM encrypted candidate resumes)",
                "audit_ledger": "Append-Only SHA-256 Chained Cryptographic Audit Store (GDPR / EU AI Act)"
            }
        }
