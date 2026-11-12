# Zecpath-AI: Developer Handbook & Troubleshooting Guide
**Deliverable 3 — Integration Runbooks & Enterprise Incident Playbooks**
*Candidate: Nandith Gireesh | Organization: Zecser Business LLP | Curriculum: Day 44 of 100*

---

## 1. Developer Integration Quickstart
Integrating Zecpath-AI into your Applicant Tracking System (ATS) requires 4 core interaction steps:

### Step 1: Authentication & Session Initialization
Initialize the session and verify that the candidate has acknowledged statutory disclosures:

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_SERVICE_TOKEN",
    "Content-Type": "application/json",
    "X-Correlation-ID": "550e8400-e29b-41d4-a716-446655440000"
}

init_payload = {
    "candidate_id": "CAND-43-ADITI",
    "role_id": "DATA_INFRA_ENG",
    "target_seniority": "SENIOR",
    "explicit_opt_in": True,
    "locale": "en-US"
}

resp = requests.post("https://api.zecpath.ai/api/v1/interview/sessions", json=init_payload, headers=headers)
session_data = resp.json()
session_id = session_data["session_id"]
print(f"Session initialized: {session_id} | Initial Question: {session_data['initial_question']}")
```

### Step 2: Ingest Conversational Turns
Stream candidate speech or send transcribed text turns:

```python
turn_payload = {
    "session_id": session_id,
    "turn_index": 1,
    "raw_transcript": "I deployed Apache Kafka and partitioned consumer groups for fault-tolerance.",
    "speech_latency_seconds": 2.4,
    "audio_duration_seconds": 15.0
}

turn_resp = requests.post("https://api.zecpath.ai/api/v1/interview/turns", json=turn_payload, headers=headers)
turn_result = turn_resp.json()

if not turn_result["is_concluded"]:
    next_question = turn_result["followup_question"]
    print(f"AI Follow-Up: {next_question}")
```

### Step 3: Compute Calibrated Score & Explainability
When the interview concludes, request the multi-factor score and EU AI Act explainability dossier:

```python
score_payload = {
    "session_id": session_id,
    "include_explainability": True,
    "apply_deliberation_discount": True
}

score_resp = requests.post("https://api.zecpath.ai/api/v1/interview/score", json=score_payload, headers=headers)
score_data = score_resp.json()
print(f"Hiring Decision: {score_data['decision']} ({score_data['composite_score']} pts)")
```

---

## 2. Standardized Error Catalog & Diagnostics

| Error Code | Title / Failure Condition | Severity | Statutory Impact | Remediation Runbook |
| :--- | :--- | :---: | :--- | :--- |
| **`ERR_ZEC_4001`** | Candidate Consent Opt-Out / Revocation | HIGH | NYC LL144 / BIPA / EU AI Act Art. 14 | **`RB-ZEC-CONSENT-01`** |
| **`ERR_ZEC_4002`** | Demographic Token Leakage in Text | CRITICAL | EEOC Title VII / ADEA 29 U.S.C. § 621 | **`RB-ZEC-SCRUB-02`** |
| **`ERR_ZEC_4003`** | Follow-Up Recursion Cap Exceeded | MEDIUM | Candidate Experience / 30m Time SLA | **`RB-ZEC-FLOW-03`** |
| **`ERR_ZEC_4004`** | ASR Disfluency Saturation (>40%) | LOW | Audio Quality & SNR Assurance | **`RB-ZEC-ASR-04`** |
| **`ERR_ZEC_4005`** | Double-Dipping Penalty Violation | HIGH | EEOC Uniform Guidelines (29 CFR § 1607) | **`RB-ZEC-SCORE-05`** |
| **`ERR_ZEC_4006`** | Retention TTL Expiry Violation | CRITICAL | Illinois BIPA / GDPR Art. 5(1)(e) | **`RB-ZEC-PURGE-06`** |
| **`ERR_ZEC_5001`** | Turn Latency SLA Breach (>350ms) | HIGH | Real-Time Voice Responsiveness | **`RB-ZEC-PERF-07`** |

---

## 3. Incident Triage Runbooks

### Runbook `RB-ZEC-CONSENT-01`: Candidate Opt-Out or Human Review Request
1. **Trigger:** Candidate unchecks statutory consent or requests human reassignment during interview.
2. **Immediate Action:** Terminate automated recording. Return HTTP `403 Forbidden` with status `OPTED_OUT`.
3. **Webhook Dispatch:** Trigger `POST /webhooks/recruiter/human-handoff` to alert talent acquisition.
4. **Candidate Protection:** Guarantee in writing that the candidate's hiring candidacy remains completely unprejudiced.

### Runbook `RB-ZEC-SCRUB-02`: Demographic Token Leakage Intercept
1. **Trigger:** Pre-scoring validator detects an unmasked entity (`[A-Z][a-z]+ [A-Z][a-z]+` or `19[0-9]{2}`).
2. **Immediate Action:** Quarantine the utterance payload. Block submission to LLM / Scoring Engine.
3. **Remediation:** Invoke secondary heuristic named-entity scrubbers:
   ```python
   from interview_ai.demographic_bias_scrubber import DemographicBiasScrubber
   scrubber = DemographicBiasScrubber()
   clean_text, meta = scrubber.scrub_text(leaked_text)
   ```
4. **Log Event:** Record the signature pattern to `var/log/scrubber_fallbacks.log` for rulebase retraining.

### Runbook `RB-ZEC-SCORE-05`: Double-Dipping Deduction Capping
1. **Trigger:** Composite deduction sum exceeds `-12.0` points.
2. **Immediate Action:** Enforce partition ceilings:
   - Linguistic deductions clamped to $\le -6.0$ pts.
   - Behavioral deductions clamped to $\le -8.0$ pts.
   - Fallacy deductions clamped to $\le -4.0$ pts.
   - Net deductions clamped to $\le -12.0$ pts.
3. **Verification:** Verify that the candidate profile does not collapse into false rejection on borderline scores.
