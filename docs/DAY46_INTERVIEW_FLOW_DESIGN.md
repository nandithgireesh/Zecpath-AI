# Zecpath-AI: Interview Flow Design & Finite State Machine Specification
**Curriculum Milestone:** Day 46 – Technical Interview System Design  
**Deliverable 3:** Interview Flow Design Diagram & State Engine  
**Specification Version:** 1.0.0-PROD-FLOW  
**Document Classification:** Conversational State Machine Specification  

---

## 1. Finite State Machine (FSM) Overview

The technical interview execution is governed by a deterministic, audit-logged Finite State Machine (FSM) implemented in `tech_interview/flow_engine.py`. The state machine guarantees that no candidate skips required phases, prevents premature completion, enforces minimum turns per stage, and provides structured sub-turn dynamic adaptation.

### 1.1 FSM State Lifecycle

```
[INITIALIZED]
     |
     v
[INTRODUCTION] -------- (min 1 turn completed)
     |
     v
[EXPERIENCE_PROBING] -- (min 1-2 questions answered)
     |
     v
[CONCEPTUAL_EVAL] ----- (min 1-2 questions answered)
     |
     v
[SCENARIO_ANALYSIS] --- (min 1-2 scenarios solved)
     |
     +--------------> [SYSTEM_DESIGN] (Mandatory for Senior 5+y; Conditional for Mid)
     |                      |
     v                      v
[WRAP_UP] <-----------------+
     |
     v
[COMPLETED] (Terminal State: Generates Final Scoring Radar & Dossier)
```

### 1.2 State Transition Matrix & Transition Guards

| From State | Allowed Target States | Guard / Exit Criteria |
| :--- | :--- | :--- |
| `INITIALIZED` | `INTRODUCTION`, `ABORTED` | Candidate profile validated and baseline tier established. |
| `INTRODUCTION` | `EXPERIENCE_PROBING`, `PAUSED`, `ABORTED` | $\ge 1$ question answered; technical background grounded. |
| `EXPERIENCE_PROBING` | `CONCEPTUAL_EVALUATION`, `PAUSED`, `ABORTED` | $\ge 2$ questions answered (1 in fast-track); past engineering decisions verified. |
| `CONCEPTUAL_EVALUATION` | `SCENARIO_ANALYSIS`, `PAUSED`, `ABORTED` | $\ge 2$ questions answered; runtime internals and fundamentals assessed. |
| `SCENARIO_ANALYSIS` | `SYSTEM_DESIGN_DEEPDIVE`, `WRAP_UP`, `PAUSED` | $\ge 2$ scenarios triaged; moves to System Design if Senior (5+y) or Mid score $\ge 0.70$. |
| `SYSTEM_DESIGN` | `WRAP_UP`, `PAUSED`, `ABORTED` | $\ge 1$ large-scale architecture problem synthesized. |
| `WRAP_UP` | `COMPLETED`, `ABORTED` | Candidate debrief questions addressed; session sealed. |
| `PAUSED` | Any non-terminal state, `ABORTED` | Resumes directly to previous active state without loss of context. |
| `COMPLETED` | None | Terminal state. Outbound transitions strictly forbidden. |

---

## 2. Sub-Turn Dynamic Conversational Adaptation

While primary states represent macroscopic interview phases, each turn executes fine-grained sub-turn adaptation via three distinct paths:

### 2.1 Branch A: Dynamic Follow-up Probing (`PROBE_DEEPER`)
- **Condition:** Candidate response is partially correct or shows omissions, with score $s_t \in [0.35, 0.70)$, and current probing depth $< 2$.
- **Action:** Retains active question context and issues a targeted follow-up probe exploring missing edge cases, latency constraints, or parameter trade-offs.
- **Safety Bound:** Maximum recursion depth capped at $\le 2$ sub-turns per question to prevent conversational deadlock.

### 2.2 Branch B: Scaffolding Hints (`PROVIDE_SCAFFOLDING_HINT`)
- **Condition:** Candidate experiences severe struggle ($s_t < 0.35$) or indicates uncertainty.
- **Action:** Issues a directional algorithmic hint (e.g. highlighting a relevant design pattern or memory space) without disclosing the direct answer.
- **Outcome:** Tests candidate receptivity to guidance and coaching.

### 2.3 Branch C: Phase & Question Advancement (`ADVANCE_QUESTION`)
- **Condition:** Candidate provides a complete answer ($s_t \ge 0.70$) OR maximum probing depth is reached.
- **Action:** Finalizes turn grade, increments stage completion count, calculates next difficulty $\delta_{t+1}$, and evaluates phase exit guards.

---

## 3. Evaluation Scoring Rubric & Decision Verdicts

Every answer is graded across four orthogonal dimensions:
- **Conceptual Correctness (35%):** Factual accuracy of algorithms and runtime internals.
- **Implementation Depth (30%):** Knowledge of execution mechanics, concurrency, and edge conditions.
- **Architectural Trade-offs (20%):** Awareness of latency vs throughput, memory vs compute, consistency vs availability.
- **Communication Clarity (15%):** Conciseness, structure, and professional technical articulation.

$$\text{Score} = (0.35 \times C_{\text{corr}}) + (0.30 \times D_{\text{depth}}) + (0.20 \times T_{\text{trade}}) + (0.15 \times K_{\text{clar}})$$

### 3.1 Final Hiring Recommendation Thresholds

| Composite Technical Score | Recommendation Verdict | Action Outcome |
| :--- | :--- | :--- |
| **80.0 – 100.0%** | `STRONG_HIRE` | Exceptional competency across all tested domains. Direct offer recommendation. |
| **65.0 – 79.9%** | `LEAN_HIRE` | Solid technical foundation with minor coaching required in advanced edge cases. |
| **50.0 – 64.9%** | `BORDERLINE` | Satisfactory on foundational concepts but exhibits gaps in architecture or optimization. |
| **< 50.0%** | `NO_HIRE` | Fails to meet minimum technical bar for the target job role. |
