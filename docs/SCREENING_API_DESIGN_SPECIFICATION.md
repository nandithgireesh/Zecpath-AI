# Zecpath-AI: Screening System API Design Specification
## Developer & Integration Guide for Telephony Gateways & ATS Platforms

---

## 1. API Architecture Overview

The Zecpath-AI Screening API is a high-performance RESTful API built with **FastAPI** and **Pydantic v2**. It serves as the bridge between external telephony gateways (WebRTC, SIP, Twilio, Asterisk) and enterprise Applicant Tracking Systems (ATS) such as Greenhouse, Lever, and Workday.

### Core Protocol Attributes:
- **Base URL:** `https://api.zecpath.ai/v1` (Local development: `http://127.0.0.1:8000`)
- **Protocol:** HTTP/1.1 and HTTP/2 over TLS 1.3
- **Data Exchange Format:** `application/json`
- **Schema Standard:** JSON Schema Draft-07 compliant
- **Latency SLAs:** `< 50ms` turn processing, `< 200ms` report generation
- **Idempotency:** Supported on session start and turn execution via `X-Idempotency-Key`

---

## 2. Telephony & ATS Webhook Integration Architecture

```
+------------------------------------------------------------------------------------+
|                         TELEPHONY & ATS INTEGRATION FLOW                           |
+------------------------------------------------------------------------------------+
| [ATS (Workday / Greenhouse)]                                                       |
|       |                                                                            |
|       | 1. Trigger Screening Call: POST /screening/production/session/start        |
|       v                                                                            |
| [Zecpath-AI API]                                                                   |
|       |                                                                            |
|       | 2. Outbound Dial via SIP / Twilio Trunk: Return session_id & initial_prompt|
|       v                                                                            |
| [Candidate Phone Line]                                                             |
|       |                                                                            |
|       | 3. Candidate Spoken Turn (Audio Telemetry + Transcript)                    |
|       v                                                                            |
| [Telephony Gateway (Twilio / Asterisk)]                                            |
|       |                                                                            |
|       | 4. Turn Webhook: POST /screening/production/session/turn                   |
|       v                                                                            |
| [Zecpath-AI Production Orchestrator]                                               |
|       | (Acoustic check -> Hinglish normalization -> State machine -> Scorer)      |
|       |                                                                            |
|       | 5. Return ai_spoken_prompt for TTS playback                                |
|       v                                                                            |
| [Candidate Phone Line]                                                             |
|       |                                                                            |
|       | 6. Final Turn Reached: POST /screening/production/session/finalize         |
|       v                                                                            |
| [Zecpath-AI API]                                                                   |
|       |                                                                            |
|       | 7. ATS Webhook Callback: POST {ats_webhook_url} with full hiring report   |
|       v                                                                            |
| [ATS Recruiter Dashboard]                                                          |
+------------------------------------------------------------------------------------+
```

---

## 3. Production Endpoint Reference

### 3.1. System Health & Monitoring
- **`GET /screening/production/health`**
  - **Purpose:** Diagnostic liveness and readiness probe for Kubernetes/Docker ingress.
  - **Response:**
    ```json
    {
      "status": "HEALTHY",
      "timestamp": "2026-09-20T12:00:00Z",
      "version": "1.0.0-prod",
      "uptime_status": "OPERATIONAL",
      "subsystems": [
        {"subsystem_name": "EligibilityDecisionEngine", "status": "HEALTHY", "latency_ms": 1.2},
        {"subsystem_name": "AudioConditionHandler", "status": "HEALTHY", "latency_ms": 2.1},
        {"subsystem_name": "LanguageMixingNormalizer", "status": "HEALTHY", "latency_ms": 3.4},
        {"subsystem_name": "ScreeningScoringEngine", "status": "HEALTHY", "latency_ms": 2.0}
      ],
      "active_sessions_count": 4
    }
    ```

- **`GET /screening/production/manifest`**
  - **Purpose:** Complete engineering handover inventory of all 12 days of AI screening modules.

---

### 3.2. Session Lifecycle Endpoints

#### `POST /screening/production/session/start`
- **Purpose:** Initializes a screening call for an applicant, binds job requirements, loads questions, and returns the opening greeting.
- **Request Payload:**
  ```json
  {
    "candidate_id": "cand_1048",
    "candidate_name": "Anita Roy",
    "job_role": "Senior Cloud Infrastructure Engineer",
    "target_experience_years": 4.0,
    "max_budget_lpa": 32.0,
    "max_notice_days": 60,
    "required_skills": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"],
    "apply_threshold_optimization": true,
    "enable_acoustic_fairness_buffer": true,
    "enable_hinglish_normalization": true
  }
  ```
- **Response Payload:**
  ```json
  {
    "session_id": "sess_prod_a1b2c3d4e5f6",
    "candidate_id": "cand_1048",
    "candidate_name": "Anita Roy",
    "job_role": "Senior Cloud Infrastructure Engineer",
    "status": "ACTIVE",
    "current_state": "GREETING",
    "initial_ai_prompt": "Hello Anita Roy, this is Zecpath AI calling regarding your application for the Senior Cloud Infrastructure Engineer position. Are you ready for a brief technical discussion?",
    "created_at": "2026-09-20T12:05:00Z"
  }
  ```

#### `POST /screening/production/session/turn`
- **Purpose:** Ingests the candidate's spoken utterance alongside real-time acoustic telemetry, performs multi-stage resilient processing, and returns the next AI prompt.
- **Request Payload:**
  ```json
  {
    "session_id": "sess_prod_a1b2c3d4e5f6",
    "turn_index": 2,
    "candidate_speech": "Maine paanch saal Celery aur Redis use kiya tha async processing ke liye.",
    "snr_db": 24.5,
    "amplitude_dbfs": -16.0,
    "packet_loss_rate": 0.0,
    "clipping_events": 0,
    "response_time_seconds": 2.1
  }
  ```
- **Response Payload:**
  ```json
  {
    "session_id": "sess_prod_a1b2c3d4e5f6",
    "turn_index": 2,
    "current_state": "TECHNICAL_QUESTIONING",
    "ai_spoken_prompt": "That's very clear. How did you handle database transaction isolation and caching under high concurrent read traffic?",
    "detected_intent": "CONFIRMING_SKILL",
    "normalized_speech": "I 5 years Celery and Redis used for async processing because.",
    "extracted_entities": {
      "technologies": ["celery", "redis"]
    },
    "acoustic_discount": 0.0,
    "safety_tier": "NORMAL_FLOW",
    "is_terminal": false
  }
  ```

#### `POST /screening/production/session/finalize`
- **Purpose:** Concludes the call, computes calibrated multi-factor scores, determines hiring band, and generates the executive report.
- **Request Payload:**
  ```json
  {
    "session_id": "sess_prod_a1b2c3d4e5f6"
  }
  ```
- **Response Payload:**
  ```json
  {
    "session_id": "sess_prod_a1b2c3d4e5f6",
    "candidate_id": "cand_1048",
    "candidate_name": "Anita Roy",
    "job_role": "Senior Cloud Infrastructure Engineer",
    "completed_at": "2026-09-20T12:12:00Z",
    "eligibility_verified": true,
    "final_score": 84.5,
    "decision": "STRONG_HIRE",
    "score_breakdown": {
      "technical_competence": 85.0,
      "communication_clarity": 84.0,
      "confidence_sentiment": 85.0
    },
    "technologies_verified": ["python", "celery", "redis", "docker", "kubernetes"],
    "brevity_protection_applied": true,
    "false_rejection_risk": "0.0%"
  }
  ```

---

## 4. Status Codes & Error Handling

All error responses adhere to standard HTTP status conventions with a descriptive error envelope:

| HTTP Status | Meaning | Typical Scenario |
|---|---|---|
| **200 OK** | Success | Standard request completed successfully. |
| **400 Bad Request** | Validation Error | Missing mandatory candidate fields or invalid audio payload. |
| **404 Not Found** | Resource Missing | Specified `session_id` does not exist or has expired from cache. |
| **422 Unprocessable** | Semantic Failure | Unrecognized enum or schema violation. |
| **500 Internal Error** | Server Error | Unhandled engine exception (logged to ELK stack). |
| **503 Unavailable** | Circuit Breaker Active | System undergoing maintenance or emergency handoff trip. |
