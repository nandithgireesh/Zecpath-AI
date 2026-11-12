# Day 34: Dynamic Follow-Up Logic & Adaptive Questioning Engine
## Architecture, Decision Tree Specification & Conversational State Tracking

**Author:** Nandith Gireesh  
**Organization:** Zecser Business LLP  
**System:** Zecpath-AI Enterprise Automated HR Screening & Interview Platform  
**Target Module:** `interview_ai/dynamic_followup_engine.py`  
**Specification Version:** 1.0.0 (Production Candidate)  
**Date:** September 2026  

---

## 1. Executive Summary & Objective

In modern talent acquisition, static question scripts fail to reliably uncover a candidate's true technical depth, behavioral ownership, or operational competence. Superficial candidates can recite memorized definitions, while seasoned engineers with massive impact may deliver humble summaries that require deliberate technical elevation.

The **Dynamic Follow-Up Logic & Adaptive Questioning Engine** (Day 34) provides the conversational intelligence layer for Zecpath-AI's HR Interview System. The engine evaluates candidate utterances in real time, computes linguistic heuristics (ambiguity, agency, confidence, brevity), dynamically adapts questioning difficulty, and synthesizes targeted follow-up probes.

### Core Objectives:
1. **Detect Incomplete or Vague Answers**: Identify hand-waving filler phrases, ultra-terse responses, passive-collective dodging, and purely theoretical recitations lacking real-world grounding.
2. **Follow-Up Trigger Taxonomy**: Dispatch one of three standardized trigger categories:
   - **Clarification**: Resolves ambiguous terminology, terse descriptions, or obscured ownership.
   - **Deepening Questions**: Probes underlying engineering mechanics, trade-offs, bottleneck thresholds, and interpersonal friction.
   - **Example-Based Prompts**: Demands concrete STAR situations, production incidents, and quantifiable metrics from candidates relying on textbook theory.
3. **Difficulty Adaptation**:
   - **Simple / Surface-Level Responses** $\rightarrow$ Deeper Probe (`AdaptationTier.DEEP_PROBE`).
   - **Confident / High-Scale Assertions** $\rightarrow$ Scenario-Based Challenge (`AdaptationTier.SCENARIO_CHALLENGE`).
4. **Anti-Repetition & Interrogation Prevention**: Enforce a strict follow-up depth limit ($K=1$) per parent question and track prompt dispatch history to guarantee candidates never face identical probes.
5. **Conversational State Tracking**: Capture real-time turn diagnostics (`ambiguity_score`, `confidence_score`, `adaptation_tier`, `probe_category`) and aggregate session telemetry for the ATS dossier.

---

## 2. Subsystem Architecture

The adaptive questioning system is decomposed into three decoupled, high-cohesion components:

```
+-----------------------------------------------------------------------------------+
|                            HRInterviewFlowEngine                                  |
|                                                                                   |
|  1. Ingest Candidate Utterance                                                    |
|  2. Query DynamicFollowUpEngine for Evaluation                                     |
|  3. Dispatch Follow-Up Probe OR Advance Phase/Turn                                |
|  4. Update Turn State & Session Telemetry                                         |
+--------------------------+--------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------------------------------+
|                           DynamicFollowUpEngine                                   |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | VaguenessAmbiguityAnalyzer                                                  |  |
|  | - Brevity & Word Count Metrics                                              |  |
|  | - Hand-Waving & Filler Phrase Scanning                                       |  |
|  | - Conflict Avoidance Detection                                              |  |
|  | - Personal Agency vs Passive-Collective Heuristic                            |  |
|  | - Metric / STAR Incident Quantifier Verification                            |  |
|  | - Multi-Factor Confidence Scoring                                           |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Master Decision Tree Evaluator                                              |  |
|  | - Guard 1: Anti-Repetition Depth Cap (current_depth >= MAX_DEPTH)           |  |
|  | - Guard 2: Conversational Phase Context (Intro / Closing Protections)        |  |
|  | - Branch 1: Ambiguity & Terse -> CLARIFICATION                              |  |
|  | - Branch 2: Conflict Avoidance -> DEEPENING                                 |  |
|  | - Branch 3: Lack of Agency -> EXAMPLE_BASED                                 |  |
|  | - Branch 4: High Confidence -> SCENARIO_CHALLENGE (Difficulty Adaptation)   |  |
|  | - Branch 5: Pure Theory -> EXAMPLE_BASED                                    |  |
|  | - Branch 6: Simple / Surface-Level -> DEEPENING (Difficulty Adaptation)     |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Contextual Probe Banks & Anti-Repetition Selector                           |  |
|  | - Clarification Bank (RoleTrack x ExperienceTier)                           |  |
|  | - Deepening Bank (RoleTrack x ExperienceTier)                               |  |
|  | - Example Bank (RoleTrack x ExperienceTier)                                 |  |
|  | - Scenario Challenge Bank (RoleTrack x ExperienceTier)                      |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Quantitative Vagueness & Ambiguity Scoring Engine

The `VaguenessAmbiguityAnalyzer` extracts lexical, syntactic, and structural signals from candidate responses.

### 3.1 Mathematical Heuristic Formulations

#### 1. Vagueness Score $V(T)$
Given a candidate utterance $T$ consisting of words $W = \{w_1, w_2, \dots, w_n\}$, let $H_{\text{vague}}$ be the set of matched hand-waving filler phrases (e.g., *"and all"*, *"stuff"*, *"things like that"*, *"basically"*, *"more or less"*):

$$V(T) = \min\left(1.0, (|H_{\text{vague}}| \times 0.25) + 0.4 \cdot \mathbb{I}[|W| < 15]\right)$$

Where $\mathbb{I}[\cdot]$ is the indicator function. A response with two filler phrases or an ultra-terse length automatically triggers $V(T) \ge 0.50$, indicating excessive ambiguity.

#### 2. Personal Agency & Ownership Heuristic
Candidates frequently mask lack of direct contribution by using the passive-collective voice (*"we did"*, *"the team built"*, *"management implemented"*). The engine computes:

$$\text{Agency}(T) = \begin{cases} 
\text{FALSE}, & \text{if } \exists p \in P_{\text{collective}} \lor (|W| > 15 \land \text{"we"} \in T \land \neg \exists f \in F_{\text{first\_person}}) \\
\text{TRUE}, & \text{otherwise}
\end{cases}$$

Where $F_{\text{first\_person}} = \{\text{"i"}, \text{"my"}, \text{"personally"}, \text{"built"}, \text{"led"}, \text{"designed"}, \text{"resolved"}\}$.

#### 3. Pure Theory vs Empirical Grounding
To identify textbook recitations lacking concrete STAR experience, the engine tests for the presence of quantitative metrics ($M$) and personal incident markers ($S$):
- $M$: Numerical counts, latency measures, throughput indicators, percentages ($\ge 1$ match of `\b\d+[kmb%]?\b`, `\bp\d+\b`, `ms`, `qps`, `percent`, `three years`).
- $S$: Incident markers (`"when i"`, `"in my project"`, `"outage"`, `"memory leak"`, `"client"`, `"capstone"`).

$$\text{PureTheory}(T) = (|W| \ge 18) \land (M = \emptyset) \land (S = \emptyset)$$

#### 4. Multi-Factor Confidence Scoring $C(T)$
Confidence is evaluated across word count, assertive technical verbs ($C_{\text{hits}}$), hesitation markers ($H_{\text{hits}}$), and vagueness:

$$C(T) = \text{clip}\left(0.50 + \Delta_{|W|} + \min(0.35, |C_{\text{hits}}| \times 0.12) - (|H_{\text{hits}}| \times 0.25) - (V(T) \times 0.20), 0.0, 1.0\right)$$

Where:
$$\Delta_{|W|} = \begin{cases} 
+0.20, & |W| \ge 25 \\
-0.25, & |W| < 15 \\
0.0, & \text{otherwise}
\end{cases}$$

A candidate qualifies for **High Confidence** if:
$$C(T) \ge 0.70 \land |W| \ge 16 \land V(T) \le 0.25 \land \text{AdvancedClaims}(T)$$

---

## 4. Adaptive Questioning Framework: Difficulty Adaptation Mechanics

The engine implements two-way difficulty adaptation based on candidate response quality:

```
                           Candidate Response
                                   |
                  +----------------+----------------+
                  |                                 |
           Simple / Shallow                 Confident / High-Scale
          Surface Explanation                  Architectural Claims
                  |                                 |
                  v                                 v
        [ Adapt: Deeper Probe ]           [ Adapt: Scenario Challenge ]
          AdaptationTier:                   AdaptationTier:
            DEEP_PROBE                        SCENARIO_CHALLENGE
          Category:                         Category:
            DEEPENING                         SCENARIO_CHALLENGE
                  |                                 |
                  +----------------+----------------+
                                   |
                                   v
                      Dynamic Contextual Probing
```

### 4.1 Adaptation Matrix

| Candidate State | Diagnostic Criteria | Adaptation Tier | Probe Category | Engine Action |
| :--- | :--- | :--- | :--- | :--- |
| **Terse / Ambiguous** | Word count $<15$ OR $V(T) \ge 0.50$ | `DEEP_PROBE` | `CLARIFICATION` | Request step-by-step breakdown or tool specification |
| **Passive / Evasive** | Passive collective voice without personal agency | `DEEP_PROBE` | `EXAMPLE_BASED` | Demand specific individual deliverable and ownership |
| **Conflict Avoidance** | "Never had conflict", "always agreed" | `DEEP_PROBE` | `DEEPENING` | Present constructive conflict resolution probe |
| **Pure Theory** | Word count $\ge 18$, 0 metrics, 0 incident anchors | `STANDARD` | `EXAMPLE_BASED` | Demand real-world project incident or production outage |
| **Simple / Surface** | Word count $15-26$, basic assertion, 0 technical specifics | `DEEP_PROBE` | `DEEPENING` | Probe failure modes, trade-offs, and verification logic |
| **High Confidence** | $C(T) \ge 0.70$, high scale claims, 0 vagueness | `SCENARIO_CHALLENGE` | `SCENARIO_CHALLENGE` | Inject high-stakes production failure / deadlock scenario |

---

## 5. Complete Decision Tree Specification

### 5.1 Decision Tree Flowchart

```
                          Candidate Turn Received
                                     |
                                     v
                  +-------------------------------------+
                  |   current_depth >= MAX_DEPTH (1)?   |
                  +-------------------------------------+
                               /             \
                        YES   /               \   NO
                             v                 v
                   [ Bypass Follow-Up ]  +-------------------------------------+
                   [ Advance Question ]  | Phase Guard: Intro / Closing &      |
                                         | Response Satisfactory (V < 0.50)?   |
                                         +-------------------------------------+
                                                       /             \
                                                YES   /               \   NO
                                                     v                 v
                                           [ Bypass Follow-Up ]  +-------------------------------------+
                                           [ Advance Question ]  | Branch 1: Terse (|W| < 15) OR       |
                                                                 |           Vagueness Score >= 0.50?  |
                                                                 +-------------------------------------+
                                                                               /             \
                                                                        YES   /               \   NO
                                                                             v                 v
                                                                   [ CLARIFICATION ]     +-------------------------------------+
                                                                   [ Tier: DEEP_PROBE ]  | Branch 2: Conflict Avoidance        |
                                                                                         |           Pattern Detected?         |
                                                                                         +-------------------------------------+
                                                                                                       /             \
                                                                                                YES   /               \   NO
                                                                                                     v                 v
                                                                                           [ DEEPENING ]         +-------------------------------------+
                                                                                           [ Conflict Probe ]    | Branch 3: Lacks Personal Agency /   |
                                                                                                                 |           Passive-Collective Voice? |
                                                                                                                 +-------------------------------------+
                                                                                                                               /             \
                                                                                                                        YES   /               \   NO
                                                                                                                             v                 v
                                                                                                                   [ EXAMPLE_BASED ]     +-------------------------------------+
                                                                                                                   [ Ownership Probe ]   | Branch 4: High Confidence           |
                                                                                                                                         |           (C >= 0.70 & Adv Claims)? |
                                                                                                                                         +-------------------------------------+
                                                                                                                                                       /             \
                                                                                                                                                YES   /               \   NO
                                                                                                                                                     v                 v
                                                                                                                                           [ SCENARIO_CHALLENGE ] +-------------------------------------+
                                                                                                                                           [ Difficulty Adapt ]   | Branch 5: Pure Theory               |
                                                                                                                                                                  |           (|W| >= 18 & 0 Metrics)?  |
                                                                                                                                                                  +-------------------------------------+
                                                                                                                                                                                /             \
                                                                                                                                                                         YES   /               \   NO
                                                                                                                                                                              v                 v
                                                                                                                                                                    [ EXAMPLE_BASED ]     +-------------------------------------+
                                                                                                                                                                    [ Incident Probe ]    | Branch 6: Simple / Surface-Level?   |
                                                                                                                                                                                          +-------------------------------------+
                                                                                                                                                                                                        /             \
                                                                                                                                                                                                 YES   /               \   NO
                                                                                                                                                                                                      v                 v
                                                                                                                                                                                            [ DEEPENING ]         [ Quality Met ]
                                                                                                                                                                                            [ Deeper Probe ]      [ Advance Turn ]
```

---

## 6. Anti-Repetition Guard & Conversational State Tracking

### 6.1 Follow-Up Depth Invariant ($K=1$)
A critical design requirement in AI interview systems is preventing "interrogation loops" where an AI relentlessly pesters a candidate on a single topic. The engine enforces:
$$\text{FollowUpDepth}(q) \le 1, \quad \forall q \in Q$$
If a candidate remains terse or vague after receiving one follow-up probe, the engine acknowledges the input, logs the low score in turn telemetry, and automatically transitions to the next competency question.

### 6.2 Prompt Variant Selector with Memory
The engine maintains four distinct probe banks indexed by `(RoleTrack, ExperienceTier)`. When a trigger fires, `_select_variant()` checks the session history:
$$\text{Prompt} = \min_{p \in \text{Bank}[track, tier]} \left\{ p \mid p \notin \text{History}(S) \right\}$$
This guarantees that candidates never hear duplicate prompts during the interview.

### 6.3 State Tracking Data Structures

Every interview turn updates the `InterviewTurnState`:
```python
@dataclass
class InterviewTurnState:
    turn_index: int
    phase: InterviewPhase
    category: HRCategory
    question_id: str
    ai_prompt: str
    candidate_response: str = ""
    is_follow_up: bool = False
    follow_up_depth: int = 0
    follow_up_triggered: bool = False
    follow_up_reason: FollowUpTriggerReason = FollowUpTriggerReason.NONE
    probe_category: FollowUpProbeCategory = FollowUpProbeCategory.NONE
    adaptation_tier: AdaptationTier = AdaptationTier.STANDARD
    ambiguity_score: float = 0.0
    confidence_score: float = 0.5
    rubric_scores: Dict[str, float] = field(default_factory=dict)
```

Session-level tracking aggregates metrics in `HRInterviewSession`:
- `total_clarifications: int`
- `total_deepenings: int`
- `total_examples_requested: int`
- `total_scenarios_triggered: int`
- `probes_dispatched_history: List[str]`

---

## 7. ATS Dossier Telemetry Integration

At the completion of an interview session, `export_session_dossier()` generates an enterprise ATS payload incorporating all follow-up intelligence:

```json
{
  "session_id": "hr-sess-82a17df3",
  "candidate_name": "Vikram Mehta",
  "job_role": "Senior Distributed Systems Architect",
  "experience_tier": "experienced",
  "role_track": "technical",
  "follow_ups_triggered": 2,
  "total_clarifications": 0,
  "total_deepenings": 1,
  "total_examples_requested": 0,
  "total_scenarios_triggered": 1,
  "probes_dispatched_history": [
    "Scenario challenge: your core microservice experiences a 5x traffic surge...",
    "In engineering, disagreements on architecture or code review priorities are natural..."
  ],
  "turns": [
    {
      "turn_index": 2,
      "category": "core_competencies_and_strengths",
      "adaptation_tier": "scenario_challenge",
      "probe_category": "scenario_challenge",
      "ambiguity_score": 0.0,
      "confidence_score": 0.88
    }
  ]
}
```

---

## 8. Verification & Test Suite Summary

The engine is validated by a dedicated test suite (`tests/test_dynamic_followup_engine.py`) with 100% pass rate:
- `test_01_ambiguity_and_vagueness_detection`: Verifies filler phrase extraction, ultra-terse detection, and confidence scoring.
- `test_02_clarification_trigger_terse_and_ambiguous`: Confirms `CLARIFICATION` trigger for hand-waving or terse responses.
- `test_03_deepening_trigger_simple_responses`: Validates difficulty adaptation: simple/surface response $\rightarrow$ `DEEPENING` probe.
- `test_04_scenario_based_followup_confident_responses`: Validates difficulty adaptation: confident/high-scale response $\rightarrow$ `SCENARIO_CHALLENGE`.
- `test_05_example_based_trigger_pure_theory`: Confirms `EXAMPLE_BASED` prompt for theoretical answers lacking empirical grounding.
- `test_06_repetition_prevention_and_max_depth`: Confirms follow-up depth cap ($K=1$) stops interrogation loops.
- `test_07_full_adaptive_session_and_ats_telemetry`: End-to-end integration test validating turn flow, session counters, and dossier export.
