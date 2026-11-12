# Zecpath-AI: Demo Dataset Specification
**Deliverable 2 — Comprehensive Multi-Cohort Benchmark Evaluation Dataset**
*Candidate: Nandith Gireesh | Organization: Zecser Business LLP | Curriculum: Day 45 of 100 (Capstone)*

---

## 1. Overview & Dataset Philosophy
The **Day 45 Demo Dataset** (`data/day45_demo_interview_dataset.json`) provides a calibrated benchmark suite designed to evaluate conversational intelligence, bias neutralization, deliberation credits, and anti-double-dipping bounded scoring across realistic recruitment cohorts.

---

## 2. Cohort Persona Matrix

| Candidate ID | Name & Seniority | Target Role | Key Evaluation Test Case | Expected Outcome |
| :--- | :--- | :--- | :--- | :---: |
| **`CAND-45-01`** | Aditi Rao (Senior) | Lead Cloud Infrastructure Architect | High technical depth, 3.2s analytical pause, CDR deliberation credit (+4.2 pts) | **`STRONG_HIRE`** (88.9 pts) |
| **`CAND-45-02`** | Marcus Chen (Senior) | Senior Full-Stack Engineer | Casual speech, demographic leakage attempt (age, Stanford, gender), nervousness | **`HIRE`** (75.3 pts) |
| **`CAND-45-03`** | Priya Patel (Senior) | Data Platform Specialist | Non-standard ESL regional idioms ('prepone', 'did the needful'), zero penalty | **`STRONG_HIRE`** (84.9 pts) |
| **`CAND-45-04`** | Kevin Miller (Junior) | Junior Backend Developer | Shallow initial response, dynamic follow-up triggered, recursion capped at depth 2 | **`LEAN_HIRE`** (65.2 pts) |
| **`CAND-45-05`** | Dr. Elena Rostova (Principal)| Senior Cloud Architect | 16 yrs experience, Overqualification Leveling Index (OLI = 0.88), role upgrade | **`OVERQUALIFIED_UPGRADE`** (98.9 pts) |

---

## 3. Data Schema & Field Definitions
Each candidate record in `data/day45_demo_interview_dataset.json` adheres to strict typing:
- `candidate_id` / `pseudonym`: Statutory identifier pair enforcing unlinkable pseudonymization.
- `statutory_consent`: Cryptographic SHA-256 receipt proving pre-flight transparency notice.
- `turns`: Array of conversational turns containing raw transcript, speech latency, duration, and target competency.
- `scoring_profile`: 4-factor scores, deliberation credit restoration flags, bounded deductions, and hiring decision.
