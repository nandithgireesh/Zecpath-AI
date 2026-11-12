# Deliverable 1: Cross-Round Unified Scoring System
**System:** Zecpath-AI Multi-Modal Enterprise Interview Pipeline  
**Module:** `unified_scoring/cross_round_engine.py` & `unified_scoring/weight_system.py`  
**Scope:** Integration of ATS Resume (Round 1), Pre-Screening (Round 2), and HR Interview (Round 3)  
**Evaluation Standard:** Enterprise Calibrated Hiring Intelligence v2.0  

---

## 1. Executive Summary & Purpose

Modern hiring funnels suffer from fragmented signal isolation: ATS resume parsers screen candidates based on keyword density, pre-screening calls assess basic eligibility and communication, and technical/HR interviews evaluate behavioral competency and problem-solving depth. However, recruiting panels typically lack an automated, mathematically rigorous mechanism to synthesize these disjointed evaluation rounds into a unified hiring intelligence score.

**Deliverable 1: The Cross-Round Unified Scoring System** solves this challenge by providing a centralized orchestration engine (`UnifiedScoringEngine`) that ingests, validates, normalizes, and dynamically weights candidate scores across all three stages of the Zecpath-AI evaluation pipeline:
1. **Round 1: ATS Resume & Skill Matching** (Days 1–20)
2. **Round 2: Conversational Pre-Screening Call** (Days 21–32)
3. **Round 3: In-Depth HR Interview & Situational Aptitude** (Days 33–40)

---

## 2. Multi-Round Pipeline Architecture

```
[Round 1: ATS Resume Parsing] ──► (Skill Match, Exp Relevance, Credentials)
               │                                      │
               ▼                                      ▼
[Round 2: Conversational Screening] ──► (STT Clarity, Sentiment, Eligibility)
               │                                      │
               ▼                                      ▼
[Round 3: In-Depth HR Interview]  ──► (STAR Behavioral, Aptitude, Composure)
               │                                      │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
                [Cross-Round Weight System & Gating]
                                  │
                                  ▼
                    [Hiring Fit Calculator (0-100%)]
                                  │
                                  ▼
              [Unified Candidate Score Object (ATS JSON & MD)]
```

### Ingestion Flow:
1. **Input Normalization:** Round scores from disparate sources (resume parsers, call transcripts, behavioral rubrics) are validated and mapped onto a standardized `[0.0, 100.0]` continuous scale.
2. **Confidence Weighting:** Signal completeness factors are evaluated. Incomplete or skipped rounds trigger safety gate alerts rather than silent default passes.
3. **Role-Track Resolution:** The engine analyzes the target job role title against enterprise taxonomy rules to assign the optimal `RoleFamily` weight profile.
4. **Safety Gating:** Hard minimum thresholds are verified independently for each round. A candidate who fails a mandatory safety gate cannot receive an unqualified hire recommendation.

---

## 3. Role-Based Cross-Round Weight Profiles

The `CrossRoundWeightSystem` manages five canonical role family presets, plus support for custom enterprise configurations:

| Role Family | Display Name | ATS (R1) | Screening (R2) | HR Interview (R3) | Mandatory Safety Gates | Architectural Justification |
|---|---|:---:|:---:|:---:|---|---|
| `TECHNICAL_ENGINEERING` | Technical & Engineering Track | **25%** | **30%** | **45%** | R1 $\ge 50$, R2 $\ge 50$, R3 $\ge 55$ | Emphasizes deep architectural reasoning, CAP trade-offs, and STAR execution in Round 3. |
| `LEADERSHIP_MANAGEMENT` | Leadership & Executive Track | **20%** | **25%** | **55%** | R1 $\ge 55$, R2 $\ge 60$, R3 $\ge 65$ | Heavily weights stakeholder consensus, blameless post-mortem ownership, and crisis composure. |
| `SALES_CUSTOMER_FACING` | Sales & Customer Success Track | **15%** | **40%** | **45%** | R2 $\ge 65$, R3 $\ge 60$ | Prioritizes conversational articulation and persuasion in screening, with customer empathy in HR. |
| `EARLY_CAREER_FRESHER` | Early Career & Graduate Track | **15%** | **40%** | **45%** | R2 $\ge 45$, R3 $\ge 45$ | Reduces tenure penalty on resume ATS, focusing on learning agility and foundational aptitude. |
| `OPERATIONS_SUPPORT` | Operations & Mission-Critical Support | **25%** | **40%** | **35%** | R2 $\ge 55$, R3 $\ge 50$ | Balances procedural rigor and SLA incident triage with operational composure under stress. |
| `CUSTOM_ENTERPRISE` | Enterprise Custom Configuration | User Defined | User Defined | User Defined | Configurable | Strict validation enforces that weights sum to exactly $1.0 \pm 10^{-4}$. |

---

## 4. Mathematical Weight Normalization & Invariants

Let $S_1, S_2, S_3 \in [0, 100]$ represent normalized scores from ATS, Screening, and HR Interview rounds respectively. Let $w_1, w_2, w_3 \in [0, 1]$ represent their assigned cross-round weights.

The multi-round composite score $C$ is computed as:
$$C = \sum_{i=1}^{3} w_i \cdot S_i \quad \text{subject to} \quad \sum_{i=1}^{3} w_i = 1.0, \quad w_i \ge 0$$

### Safety Gating Invariant:
For each round $i$ with minimum threshold $\theta_i$:
$$\text{PassedGate}_i = \begin{cases} \text{True} & \text{if } S_i \ge \theta_i \\ \text{False} & \text{otherwise} \end{cases}$$
$$\text{AllGatesPassed} = \bigwedge_{i=1}^{3} \text{PassedGate}_i$$

If $\text{AllGatesPassed} = \text{False}$, the unified decision is restricted:
- If $C < 60.0 \implies \text{Decision} = \texttt{NO\_HIRE}$
- If $C \ge 60.0 \implies \text{Decision} = \texttt{LEAN\_NO\_HIRE}$ (Preventing false-positive hiring of candidates who failed foundational compliance or eligibility gates).

---

## 5. Candidate Evaluation Cohort Benchmark

The cross-round scoring engine was benchmarked across five standard candidates representing distinct performance profiles:

| Candidate ID | Name | Role & Family | R1: ATS | R2: Screening | R3: HR | Weighted Composite | Gates | Final Decision |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `SIM-CONF-01` | Aditi Rao | Sr Cloud Architect (Technical) | 88.0 | 85.0 | 90.3 | **88.1 pts** | **PASS** | `STRONG_HIRE` |
| `SIM-HES-02` | Siddharth Verma | Data Infra Eng (Technical) | 72.0 | 70.0 | 65.0 | **68.3 pts** | **PASS** | `LEAN_HIRE` |
| `SIM-INEXP-03` | Kavita Patel | Sr Systems Eng (Technical) | 58.0 | 60.0 | 55.8 | **57.6 pts** | **PASS** | `LEAN_NO_HIRE` |
| `SIM-OVER-04` | Dr. Rajesh Sundaram | DevOps Engineer (Technical) | 94.0 | 90.0 | 92.2 | **92.0 pts** | **PASS** | `STRONG_HIRE (LEVEL UP)` |
| `SIM-INCON-05` | Tarun Khanna | Sr Backend Lead (Leadership) | 65.0 | 55.0 | 40.1 | **48.8 pts** | **FAIL** | `NO_HIRE` |

---

## 6. Implementation & Verification Summary

The cross-round scoring engine is fully implemented in:
- `unified_scoring/cross_round_engine.py`: Master evaluation pipeline and input builders.
- `unified_scoring/weight_system.py`: Preset profiles, role-title resolution, and validation.
- `unified_scoring/models.py`: Pydantic telemetry models and enumerations.

Unit test verification in `tests/test_unified_scoring_engine.py` confirms 100% test passing rate across weight validation, profile resolution, gate enforcement, and multi-round composite calculations.
