# Day 32 Handover Runbook: Production Screening AI Engine
**Organization**: Zecser Business LLP  
**Candidate**: Nandith Gireesh  
**System Version**: 1.0.0-PROD  
**Target Audience**: DevOps, Telephony Platform Engineers, ML Engineers, Recruiter Operations

---

## 1. Executive System Overview
The **Production Screening System** (`screening_ai/production_screening_system.py`) is the turnkey production orchestrator that coordinates all 12 operational subsystems developed across Days 21 through 31. It provides an automated, voice-telephony-ready screening conversational agent capable of:
1. Real-time eligibility gate validation (Work authorization, notice period, location/shift).
2. Adaptive question delivery across 3 candidate tiers (Junior, Mid-Level, Senior).
3. Whisper STT transcription and multi-engine confidence scoring with telemetry ingestion.
4. Robust acoustics recovery (SNR, clipping, ambient noise handling, silence fallback).
5. Hinglish/code-switching normalization with canonical token mapping.
6. Multi-intent intent classification (Answer, Clarification, Repeat, Counter-question, Silence).
7. Calibrated response scoring (Rubric + Semantic similarity with ROC/AUC threshold optimization).
8. Deterministic state machine execution with circuit-breaker safety fallbacks.
9. Comprehensive ATS compliance audit reports with PII redaction and cryptographic hash seals.

---

## 2. Environment Configuration
Create or configure `.env` in the project root with the following parameters:

```env
# Telephony & Server Settings
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO

# Screening Engine Config
MAX_SILENCE_PROMPTS=3
MAX_REPEAT_REQUESTS=2
CALL_TIMEOUT_SECONDS=900
SNR_WARN_THRESHOLD_DB=12.0
SNR_CRITICAL_THRESHOLD_DB=8.0

# Speech & Model Backends
WHISPER_MODEL_SIZE=base
WHISPER_CONFIDENCE_THRESHOLD=0.65
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ATS Integration
ATS_WEBHOOK_URL=https://api.zecser.com/ats/v1/screening-callback
ATS_WEBHOOK_SECRET=prod_ats_sec_9942a9b3f0c1
PII_REDACTION_ENABLED=true

# Security & Auditing
AUDIT_LOG_DIR=logs/audit_screening
AUDIT_SIGNING_SALT=zecser_prod_salt_2026
```

---

## 3. Deployment & Startup Procedure

### 3.1 Local / Development Server
Activate the Python virtual environment and run Uvicorn:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn api.main_day20:app --host 0.0.0.0 --port 8000 --reload
```

### 3.2 Production Container Deployment (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main_day20:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Run container:
```bash
docker build -t zecpath/screening-engine:v1.0.0 .
docker run -d -p 8000:8000 --env-file .env --name screening-ai-prod zecpath/screening-engine:v1.0.0
```

---

## 4. Operational Health & Verification

### 4.1 Live Health Check
```bash
curl -X GET http://localhost:8000/screening/production/health
```
**Expected Response (200 OK):**
```json
{
  "system_status": "ONLINE",
  "version": "1.0.0-PROD",
  "active_sessions": 0,
  "subsystem_health": {
    "day21_eligibility": "HEALTHY",
    "day22_question_banks": "HEALTHY",
    "day23_stt_transcription": "HEALTHY",
    "day24_telemetry_acoustics": "HEALTHY",
    "day25_language_hinglish": "HEALTHY",
    "day26_intent_flow": "HEALTHY",
    "day27_calibrated_scoring": "HEALTHY",
    "day28_dialogue_state_machine": "HEALTHY",
    "day29_threshold_roc_auc": "HEALTHY",
    "day30_silence_safety_fallback": "HEALTHY",
    "day31_ats_reporting": "HEALTHY",
    "day32_production_orchestration": "HEALTHY"
  },
  "overall_healthy": true
}
```

### 4.2 Production Handover Manifest
Inspect module versions, checksums, and calibrated thresholds:
```bash
curl -X GET http://localhost:8000/screening/production/manifest
```

---

## 5. End-to-End Operational Lifecycle

```
Candidate Connects (Telephony / Twilio SIP)
                │
                ▼
1. POST /screening/production/session/start
   - Initializes state machine to GREETING
   - Returns greeting audio text prompt
                │
                ▼
2. POST /screening/production/session/turn (Turn 1: Eligibility)
   - Evaluates work authorization, notice period, location
   - If Ineligible -> Routes to EARLY_EXIT_INELIGIBLE
                │
                ▼
3. POST /screening/production/session/turn (Turns 2..N: Technical Screening)
   - Dispatches question based on candidate tier
   - Normalizes Hinglish/Code-switching
   - Analyzes audio telemetry (SNR, clipping, ambient noise)
   - Resolves intent (clarification vs answer vs silence)
   - Scores answer against domain rubrics (0.0 - 1.0)
                │
                ▼
4. POST /screening/production/session/finalize
   - Compiles final scoring metrics and recommendation
   - Dispatches signed ATS audit payload (webhook)
   - Destroys ephemeral memory; persists encrypted transcript
```

---

## 6. Resilience & Incident Response Matrix

| Symptom / Event | Root Cause | System Response | Operator Remediation |
| :--- | :--- | :--- | :--- |
| **Degraded SNR (< 10dB)** | Candidate in high ambient noise | Audio condition handler requests acoustic repeat ("We are having trouble hearing you...") | If 3 consecutive acoustic retries fail, escalate to human callback. |
| **Silence / No Audio** | Network jitter, muted mic, hesitation | State machine stays on current question, issues silence nudge (rephrase) | Max 3 silence attempts allowed before soft graceful termination. |
| **Severe Code-Switching** | Candidate mixing Hindi, Tamil, English | Hinglish normalizer maps idioms to canonical technical terms | Engine logs code-switch ratio in audit record. |
| **Candidate Asks Clarification** | Ambiguous question or candidate inquiry | Intent classifier detects `clarification_requested`; engine rephrases without penalizing score | Verify rephrased prompt answered candidate query. |
| **Webhook Delivery Timeout (504)** | ATS endpoint offline or rate-limiting | Engine queues payload to local disk `logs/audit_screening/backlog/` with exponential retry | Check ATS server status; manually trigger batch replay script. |
| **Uncaught Exception in Turn** | Corrupted audio input or memory spike | `SafetyFallbackEngine` catches error, transitions to `ESCALATED_HUMAN`, preserves logs | Check system logs at `logs/screening.log`; initiate human recruiter handover. |

---

## 7. Compliance, Audit & Data Privacy Runbook
1. **PII Masking**: All phone numbers, emails, and candidate names are masked using SHA-256 tokens in long-term logs.
2. **Audio Retention**: Raw audio blobs are discarded within 24 hours of ATS report generation unless explicit talent acquisition consent is granted.
3. **Anti-Bias Verification**: Calibration thresholds utilize calibrated demographic parity tests (evaluated in Day 29). No disparate impact observed across accent clusters.
4. **Audit Hash Integrity**: Every final ATS report contains a SHA-256 `report_hash` computed over `{session_id, candidate_id, final_decision, scores}`. Any tamper in database invalidates signature.

---

## 8. Verification & Test Automation
Run the complete unit and API test suites to verify integrity before any deployment:
```powershell
.\venv\Scripts\python.exe -m unittest tests/test_production_screening_system.py
.\venv\Scripts\python.exe -m unittest tests/test_production_api.py
```
Both suites must report **OK** with 0 failures and 0 errors.
