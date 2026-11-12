# Day 59 – Deliverable 2: API Mapping Diagram
**Zecpath-AI Automated Hiring Platform**  
*System Interaction Topology & Data Flow Specification*  
**Author:** Nandith Gireesh | **Organization:** Zecser Business LLP | **Date:** October 2026 | **Status:** Production Verified

---

## 1. System Interaction Topology Overview

Day 59 Deliverable 2 formalizes the end-to-end **API Mapping Diagram** and system communication topology of the **Zecpath AI Automated Hiring Platform**.

Operating as an enterprise-grade automated hiring platform, the integration gateway routes events between:
1. **Client / Portal Ingestion Layer:** Recruiter Dashboard, Candidate Application Portal, Live WebRTC Interview Client.
2. **Gateway Tier:** FastAPI gateway performing token-bucket rate limiting (100 req/min), dual authentication (Bearer JWT & HMAC-SHA256), and 24-hour cryptographic idempotency deduplication.
3. **Execution Tier:** Asynchronous Celery worker queues (Redis broker) for compute-intensive extraction and scoring vs. sub-50ms synchronous streaming for conversational screening and interview turn-taking.
4. **Persistence & Compliance Tier:** PostgreSQL relational tables, Redis in-memory session stores, AWS S3 encrypted document vaults, and cryptographic audit trail logs.

---

## 2. End-to-End Sequence & Interaction Flow

```
+-----------------------------------------------------------------------------------------------------------------------+
|                                    END-TO-END SYSTEM INTERACTION TOPOLOGY                                             |
|                                                                                                                       |
|  [Client / Frontend]         [FastAPI Gateway]            [Message Queue / Cache]       [AI Subsystem Engines]        |
|          |                            |                              |                            |                   |
|          | 1. POST Resume (PDF)       |                              |                            |                   |
|          |--------------------------->|                              |                            |                   |
|          |                            | 2. Enqueue Job               |                            |                   |
|          |                            |----------------------------->|                            |                   |
|          | 3. HTTP 202 Accepted       |                              |                            |                   |
|          |<---------------------------|                              | 4. Claim Task              |                   |
|          |                            |                              |--------------------------->|                   |
|          |                            |                              |                            | 5. Parse Skills   |
|          |                            |                              |                            |    & Redact PII   |
|          |                            |                              |                            |-----------------> |
|          |                            |                              | 6. Complete Job Payload    |  (PostgreSQL &    |
|          |                            |                              |<---------------------------|   S3 Vault)       |
|          | 7. Webhook / Poll 200 OK   |                              |                            |                   |
|          |<---------------------------|                              |                            |                   |
|          |                            |                              |                            |                   |
|          | 8. Start Live Interview    |                              |                            |                   |
|          |--------------------------->|                              |                            |                   |
|          |                            | 9. Init Stateful Session     |                            |                   |
|          |                            |----------------------------->| (Redis Session Cache)      |                   |
|          | 10. Candidate Turn Stream  |                              |                            |                   |
|          |--------------------------->|                              |                            |                   |
|          |                            | 11. Execute Turn Inference (<50ms)                        |                   |
|          |                            |---------------------------------------------------------->|                   |
|          |                            |                                                           | 12. Pacing, Score |
|          |                            | 13. Synchronous Turn Response                             |     & Follow-Up   |
|          | 14. Real-Time Feedback     |<----------------------------------------------------------|                   |
|          |<---------------------------|                              |                            |                   |
|          |                            |                              |                            |                   |
|          | 15. Trigger Arbitration   |                              |                            |                   |
|          |--------------------------->| (HMAC-SHA256 Signed Request) |                            |                   |
|          |                            | 16. Multi-Round Consensus                                 |                   |
|          |                            |---------------------------------------------------------->|                   |
|          | 17. Final Hiring Decision  |                                                           | 18. Audit Trail   |
|          |<---------------------------|                                                           |     Hash Logged   |
+-----------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Subsystem Interaction Matrix

| Subsystem API | Ingestion Trigger | Core AI Engine | Primary Persistence Target | Processing Mode & SLA |
| :--- | :--- | :--- | :--- | :--- |
| **API-01: Resume Parse** | Candidate document upload on portal or recruiter ATS webhook. | `parsers.resume_parser` & `parsers.academic_profile` | PostgreSQL (`candidate_resumes`) & S3 Encrypted Vault | **ASYNC (Celery)**<br/>Target: $< 3.0\text{ s}$ (P95) |
| **API-02: ATS Scoring** | Recruiter shortlist batch trigger or post-parsing event bus. | `parsers.semantic_matching_engine` & `parsers.similarity_scorer` | PostgreSQL (`ats_evaluations`, `job_requisitions`) | **ASYNC (Celery)**<br/>Target: $< 1.5\text{ s}$ (P95) |
| **API-03: Screening AI** | Real-time candidate audio/text utterance during screening call. | `screening_ai.call_flow_engine` & `screening_ai.eligibility_engine` | In-memory Redis (`screening_active_sessions`) & PostgreSQL | **SYNC (REST/WS)**<br/>Target: $< 80\text{ ms}$ (P99) |
| **API-04: Interview AI** | Candidate speech utterance or code submission in sandbox. | `interview_ai.turn_evaluator` & `interview_ai.communication_evaluator` | Redis (`interview_turn_state`) & PostgreSQL (`interview_turns`) | **SYNC (REST/WS)**<br/>Target: $< 50\text{ ms}$ (P99) |
| **API-05: Decision AI** | Concluded interview event or recruiter final arbitration trigger. | `final_recommendation_ai.arbitration_engine` | PostgreSQL (`hiring_decisions`) & Immutable Audit Vault | **SYNC (HMAC Hybrid)**<br/>Target: $< 500\text{ ms}$ (P95) |

---

## 4. Pipeline Decoupling: Asynchronous vs. Synchronous Flow

### 4.1. Asynchronous Ingestion & Extraction Pipeline
1. **Idempotency Check:** Client sends request with `X-Idempotency-Key`. The gateway looks up the key in the 24-hour cache. If matched, the previously generated `AsyncJobResponse` is returned immediately without re-enqueuing.
2. **Job Enqueueing:** For new requests, an asynchronous job record is initialized with status `QUEUED` and stored in Redis. An HTTP `202 Accepted` response is returned with the status check route (`/api/v1/ai/jobs/{job_id}`).
3. **Worker Execution:** Celery workers claim tasks from the queue, transition the status to `PROCESSING`, execute heavy NLP tokenization and skill extraction, and persist the structured output to PostgreSQL.
4. **Completion & Notification:** The job status updates to `COMPLETED`, storing the `ResumeParserResult`, and an asynchronous webhook is emitted to notify downstream services.

### 4.2. Synchronous Low-Latency Turn Scoring Pipeline
1. **Session Buffering:** During screening calls and live technical interviews, candidate session context is maintained in Redis with a 2-hour sliding TTL.
2. **Instant Turn Processing:** Speech and code turns are processed by the turn evaluation engine in $< 18.5\text{ ms}$, extracting technical accuracy, behavioral composure, speech pacing (WPM), and generating dynamic Socratic follow-up probes.
3. **Audit Trail Logging:** Concluded turns are synchronously logged to PostgreSQL and hashed for cryptographic audit integrity.
