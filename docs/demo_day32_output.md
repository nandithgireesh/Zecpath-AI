# Day 32 Live Demo Output: Turnkey Production Screening Telephony Session

**Session ID**: `sess_prod_aa339ce30b4b`  
**Candidate ID**: `cand_rahul_sharma_981`  
**Candidate Name**: Rahul Sharma  
**Role**: Senior Python Engineer  
**Completed Timestamp**: 2026-09-24T04:43:37.084324+00:00  
**Final Decision**: **STRONG_HIRE** (Score: 91.1/100.0)  

---

## 1. Executive Screening Evaluation Summary

| Assessment Dimension | Result | Benchmark Target | Verdict |
| :--- | :--- | :--- | :--- |
| **Eligibility Gate** | PASSED | Mandatory 100% | PASS |
| **Overall Score** | 91.1/100 | >= 65.0 | STRONG_HIRE |
| **Technical Competence** | 95.0/100 | >= 60.0 | PASS |
| **Communication Clarity** | 92.0/100 | >= 60.0 | PASS |
| **Confidence & Sentiment** | 85.0/100 | >= 60.0 | PASS |
| **False Rejection Risk** | 0.0% | < 2.0% | SAFE (Protected) |
| **Brevity Protection** | Active | ROC/AUC Calibrated | PASS |

## 2. Multi-Turn Conversational Transcript & Telemetry

### Initial Greeting (Turn 0)
- **AI Speaker**: "Hello Rahul Sharma, this is Zecpath AI calling regarding your application for the Senior Python Engineer position. Are you ready for a brief technical discussion?"

### Turn 1: Readiness & Eligibility Response
- **Candidate Audio Input**: *"Yes, I am ready for the interview. I have 5 years of experience building Python and FastAPI microservices."*
- **Normalized English Utterance**: *"Yes, I am ready for were interview. I have 5 years of experience building Python and FastAPI microservices."*
- **Acoustic Telemetry**: SNR=24.5dB | Loss=0.2% | Clips=0
- **Acoustic Fairness Discount**: 0.0%
- **Detected Intent**: `CONFIRMING_SKILL`
- **Safety Degradation Tier**: `NORMAL_FLOW`
- **FSM Transition State**: `ELIGIBILITY_CHECK`
- **Next AI Spoken Prompt**: "Great! To start, could you confirm how many years of experience you have with Python and backend microservices?"

### Turn 2: Technical Architecture & Task Queues (Hinglish Code-Switching)
- **Candidate Audio Input**: *"Humne Celery aur Redis use kiya tha asynchronous background processing ke liye kyunki high scale pe database pe direct load nahi daal sakte the. PgBouncer bhi use kiya connection pooling ke liye."*
- **Normalized English Utterance**: *"we Celery and Redis use kiya was asynchronous background processing of for because high scale pe database pe direct load not daal sakte were. PgBouncer bhi use kiya connection pooling of for."*
- **Acoustic Telemetry**: SNR=22.0dB | Loss=0.8% | Clips=0
- **Acoustic Fairness Discount**: 0.0%
- **Detected Intent**: `CONFIRMING_SKILL`
- **Safety Degradation Tier**: `NORMAL_FLOW`
- **FSM Transition State**: `TECHNICAL_QUESTIONING`
- **Next AI Spoken Prompt**: "Excellent. In your recent projects, how did you design your asynchronous background processing pipeline?"

### Turn 3: Technical Concurrency & Caching (With Mild Ambient Noise)
- **Candidate Audio Input**: *"Under high concurrency, we implement Redis distributed locks using Redlock algorithm, combined with PostgreSQL transaction isolation level repeatable read and optimistic locking with version columns."*
- **Normalized English Utterance**: *"Under high concurrency, we implement Redis distributed locks using Redlock algorithm, combined with PostgreSQL transaction isolation level repeatable read and optimistic locking with version columns."*
- **Acoustic Telemetry**: SNR=15.5dB | Loss=2.0% | Clips=1
- **Acoustic Fairness Discount**: 10.0%
- **Detected Intent**: `CONFIRMING_SKILL`
- **Safety Degradation Tier**: `NORMAL_FLOW`
- **FSM Transition State**: `TECHNICAL_QUESTIONING`
- **Next AI Spoken Prompt**: "That's very clear. How did you handle database transaction isolation and caching under high concurrent read traffic?"

### Turn 4: Salary & Notice Period Verification
- **Candidate Audio Input**: *"My current CTC is 20 LPA, expected is 26 LPA, and my notice period is 30 days which can be negotiated to 15 days."*
- **Normalized English Utterance**: *"My current CTC is 20 LPA, expected is 26 LPA, and my notice period is 30 days which can be negotiated to 15 days."*
- **Acoustic Telemetry**: SNR=23.0dB | Loss=0.0% | Clips=0
- **Acoustic Fairness Discount**: 0.0%
- **Detected Intent**: `STATING_SALARY`
- **Safety Degradation Tier**: `NORMAL_FLOW`
- **FSM Transition State**: `SALARY_NOTICE_VERIFICATION`
- **Next AI Spoken Prompt**: "Understood. Could you share your current and expected CTC, as well as your standard notice period?"

## 3. Subsystem Health & Readiness Diagnostic

```json
{
  "status": "HEALTHY",
  "timestamp": "2026-09-24T04:43:37.066778+00:00",
  "version": "1.0.0-prod",
  "uptime_status": "OPERATIONAL",
  "subsystems": [
    {
      "subsystem_name": "EligibilityDecisionEngine",
      "status": "HEALTHY",
      "latency_ms": 1.2,
      "details": null
    },
    {
      "subsystem_name": "ScreeningQuestionBank",
      "status": "HEALTHY",
      "latency_ms": 0.8,
      "details": null
    },
    {
      "subsystem_name": "AudioConditionHandler",
      "status": "HEALTHY",
      "latency_ms": 2.1,
      "details": null
    },
    {
      "subsystem_name": "LanguageMixingNormalizer",
      "status": "HEALTHY",
      "latency_ms": 3.4,
      "details": null
    },
    {
      "subsystem_name": "MissingAnswerHandler",
      "status": "HEALTHY",
      "latency_ms": 1.5,
      "details": null
    },
    {
      "subsystem_name": "OptimizedIntentClassifier",
      "status": "HEALTHY",
      "latency_ms": 4.8,
      "details": null
    },
    {
      "subsystem_name": "ScreeningScoringEngine",
      "status": "HEALTHY",
      "latency_ms": 2.0,
      "details": null
    },
    {
      "subsystem_name": "ScreeningThresholdOptimizer",
      "status": "HEALTHY",
      "latency_ms": 1.0,
      "details": null
    },
    {
      "subsystem_name": "ConversationStateMachine",
      "status": "HEALTHY",
      "latency_ms": 0.5,
      "details": null
    },
    {
      "subsystem_name": "SafetyFallbackEngine",
      "status": "HEALTHY",
      "latency_ms": 0.9,
      "details": null
    },
    {
      "subsystem_name": "ScreeningReportBuilder",
      "status": "HEALTHY",
      "latency_ms": 3.2,
      "details": null
    }
  ],
  "active_sessions_count": 0
}
```

## 4. ATS Callback JSON Payload

```json
{
  "session_id": "sess_prod_aa339ce30b4b",
  "candidate_id": "cand_rahul_sharma_981",
  "candidate_name": "Rahul Sharma",
  "job_role": "Senior Python Engineer",
  "completed_at": "2026-09-24T04:43:37.084324+00:00",
  "eligibility_verified": true,
  "final_score": 91.1,
  "decision": "STRONG_HIRE",
  "score_breakdown": {
    "technical_competence": 95.0,
    "communication_clarity": 92.0,
    "confidence_sentiment": 85.0
  },
  "technologies_verified": [
    "microservices",
    "postgres",
    "async",
    "redis",
    "celery",
    "python"
  ],
  "turns_completed": 4,
  "brevity_protection_applied": true,
  "false_rejection_risk": "0.0%"
}
```
