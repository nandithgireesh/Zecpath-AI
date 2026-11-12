# Zecpath-AI: HR Interview AI API Specification
**Deliverable 2 — OpenAPI 3.1.0 REST API Reference & Data Contracts**
*Candidate: Nandith Gireesh | Organization: Zecser Business LLP | Curriculum: Day 44 of 100*

---

## 1. API Architecture & Standards
The Zecpath-AI API adheres to RESTful design patterns, **OpenAPI 3.1.0** specifications, and ISO/IEC 27001 data protection protocols.

- **Base URL:** `https://api.zecpath.ai/api/v1/interview`
- **Data Exchange Format:** `application/json` (UTF-8)
- **Authentication:** Standard HTTP Bearer Token (`Authorization: Bearer <TOKEN>`)
- **Tracing Header:** `X-Correlation-ID` (UUIDv4 propagated across all asynchronous spans)
- **Idempotency Header:** `Idempotency-Key` (Supported on `/sessions` and `/gdpr/purge`)

---

## 2. Endpoint Summary Table

| HTTP Verb | Path | Summary & Scope | Success Code | Error Codes |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/sessions` | Initialize interview session, statutory consent, opening question | `201 Created` | `400`, `403` |
| `POST` | `/turns` | Process utterance, clean ASR, scrub bias, follow-up probe | `200 OK` | `400`, `404`, `422` |
| `POST` | `/score` | Compute calibrated scoring, apply CDR credit, explainability | `200 OK` | `400`, `404` |
| `POST` | `/gdpr/purge` | Execute GDPR Art. 17 instant Right-to-Erasure | `200 OK` | `401`, `404` |
| `GET` | `/health` | Live subsystem health, latency diagnostics, compliance mode | `200 OK` | `503` |

---

## 3. Detailed Endpoint Contracts

### 3.1 `POST /sessions` — Initialize Interview Session
Initializes an interview session, verifies statutory pre-flight disclosures (NYC LL144 / BIPA), registers candidate pseudonym, and outputs calibrated opening question.

#### Request Payload
```json
{
  "candidate_id": "CAND-43-ADITI",
  "role_id": "DATA_INFRA_ENG",
  "target_seniority": "SENIOR",
  "explicit_opt_in": true,
  "locale": "en-US"
}
```

#### Response Payload (`201 Created`)
```json
{
  "session_id": "sess-8f92a10b-43c1",
  "candidate_pseudonym": "PSEUDO-5C49A2314C",
  "consent_status": "EXPLICIT_OPT_IN",
  "consent_receipt_sha256": "ced23a7224d8b495e015fdfa8e53a1f458140f91eee270ea679110bb112f7fa5",
  "initial_question": "Can you describe the architectural design and replication strategy for a mission-critical distributed data pipeline you maintained?",
  "ttl_expiry_utc": "2027-01-03T12:00:00Z"
}
```

---

### 3.2 `POST /turns` — Process Candidate Conversational Turn
Cleans raw ASR transcript tags, neutralizes demographic proxy variables (names, pronouns, graduation years), computes speech velocity, and executes follow-up state machine.

#### Request Payload
```json
{
  "session_id": "sess-8f92a10b-43c1",
  "turn_index": 1,
  "raw_transcript": "My name is Aditi Rao. As a woman in tech, she told me that Harvard and Stanford grads get priority.",
  "speech_latency_seconds": 3.8,
  "audio_duration_seconds": 12.5
}
```

#### Response Payload (`200 OK`)
```json
{
  "session_id": "sess-8f92a10b-43c1",
  "turn_index": 1,
  "cleaned_transcript": "My name is Aditi Rao. As a woman in tech, she told me that Harvard and Stanford grads get priority.",
  "scrubbed_transcript": "My name is [CANDIDATE] [CANDIDATE]. as an engineer in tech, they told me that [ACCREDITED_INSTITUTION] and [ACCREDITED_INSTITUTION] grads get priority.",
  "redaction_telemetry": {
    "total_redactions": 6,
    "name_tokens_redacted": 2,
    "gender_pronouns_neutralized": 2,
    "age_grad_proxies_redacted": 0,
    "institution_proxies_normalized": 2,
    "geo_dialects_normalized": 0
  },
  "cognitive_deliberation_ratio": 22.4,
  "followup_action": "PROBE_DEEPER",
  "followup_question": "You mentioned architectural trade-offs; how did you configure quorum and partition tolerance?",
  "is_concluded": false
}
```

---

### 3.3 `POST /score` — Compute Calibrated Scoring & Explainability
Evaluates the candidate session across 4 competency dimensions, applies Cognitive Deliberation Ratio hesitation discounts, enforces anti-double-dipping deduction limits, and returns an EU AI Act transparency dossier.

#### Request Payload
```json
{
  "session_id": "sess-8f92a10b-43c1",
  "include_explainability": true,
  "apply_deliberation_discount": true
}
```

#### Response Payload (`200 OK`)
```json
{
  "session_id": "sess-8f92a10b-43c1",
  "candidate_pseudonym": "PSEUDO-5C49A2314C",
  "composite_score": 69.2,
  "decision": "LEAN_HIRE",
  "leveling_recommendation": "MID",
  "overqualification_index": 0.415,
  "factors": [
    {"factor_name": "Semantic Relevance", "weight": 0.30, "raw_score": 72.0, "weighted_contribution": 21.6},
    {"factor_name": "Articulation & Fluency", "weight": 0.25, "raw_score": 68.0, "weighted_contribution": 17.0},
    {"factor_name": "Composure & Delivery", "weight": 0.20, "raw_score": 74.9, "weighted_contribution": 15.0},
    {"factor_name": "Technical Consistency", "weight": 0.25, "raw_score": 74.0, "weighted_contribution": 18.5}
  ],
  "deductions": [
    {
      "category": "linguistic",
      "points_deducted": 2.0,
      "rationale": "Speech onset delay slightly exceeded baseline, indicating deliberation.",
      "is_bounded": true
    }
  ],
  "total_deduction_points": 2.0,
  "explainability": {
    "transparency_framework": "EU AI Act Articles 13 & 14",
    "deliberation_credit_applied": true,
    "credit_points_restored": 4.2,
    "counterfactual_guidance": "Candidate is currently at LEAN_HIRE (69.2 pts). Raising technical depth from 72.0 to 82.0+ elevates net score to 78.5+, securing a definitive STRONG_HIRE recommendation.",
    "human_oversight_notice": "Final hiring decision remains subject to certified human bar raiser review pursuant to EU AI Act Article 14."
  }
}
```

---

### 3.4 `POST /gdpr/purge` — Execute GDPR Article 17 Right-to-Erasure
Instantly shreds candidate audio, cleaned transcripts, and scoring dossiers, issuing an immutable SHA-256 deletion certificate.

#### Request Payload
```json
{
  "candidate_id": "CAND-43-ADITI",
  "statutory_authority": "GDPR Article 17 Right to be Forgotten",
  "requestor_token": "bearer_auth_dpo_token_99128"
}
```

#### Response Payload (`200 OK`)
```json
{
  "candidate_id": "CAND-43-ADITI",
  "purged_assets_count": 3,
  "deletion_certificate_id": "DEL-CERT-C81DFAFB2149",
  "sha256_verification_hash": "c81dfafb2149553035c73061575fefda982f59eca93c2125ba02e8513aed3d51",
  "timestamp_utc": "2026-10-05T12:00:00Z",
  "status": "PERMANENTLY_ERASED"
}
```

---

### 3.5 `GET /health` — Subsystem Health & Latency Telemetry
Returns operational readiness, subsystem latencies, and statutory compliance modes.

#### Response Payload (`200 OK`)
```json
{
  "status": "HEALTHY",
  "version": "v1.4.4",
  "subsystems": {
    "transcript_cleaner": "PASS (0.15ms latency verified)",
    "demographic_bias_scrubber": "PASS (Zero entity leakage)",
    "stable_flow_engine": "PASS (State machine operational)",
    "refined_scoring_engine": "PASS (Bounded deduction math verified)",
    "compliance_retention_policy": "PASS (GDPR Art. 17 compliant)"
  },
  "avg_latency_ms": 0.29,
  "statutory_mode": "NYC_LL144_AND_EU_AI_ACT"
}
```
