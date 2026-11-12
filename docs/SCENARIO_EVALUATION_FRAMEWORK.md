# Zecpath-AI Scenario Evaluation Framework & Aptitude AI Logic Specification
**Module:** `interview_ai/scenario_evaluator.py`, `interview_ai/logical_reasoning_scorer.py`, `interview_ai/aptitude_engine.py`  
**Curriculum Track:** Day 38: Aptitude Logic Design  
**Author:** Nandith Gireesh | Zecser Business LLP  
**Date:** September 2026  
**Status:** Production Ready (100% Automated Test Coverage)

---

## 1. Executive Overview & Problem Statement

Conventional HR conversational interviews excel at evaluating past career chronology, self-reported accomplishments, and interpersonal polish. However, empirical recruitment research demonstrates that past historical claims often fail to predict on-the-job analytical performance when candidates encounter novel, high-stakes, ambiguous workplace crises.

Day 38 integrates **Cognitive and Situational Aptitude Evaluation** into the Zecpath-AI interview platform. The subsystem systematically presents:
1. **Reasoning-Based Questions:** Probing diagnostic root-cause deconstruction, counter-factual hypotheses, and constraint estimation.
2. **Situational Judgment Scenarios (SJTs):** Realistic workplace dilemmas requiring trade-off balancing across engineering crises, ethical violations, and stakeholder impasses.
3. **Structured Response Frameworks (IDEA & CARL):** Evaluating adherence to disciplined problem-solving methodologies.
4. **Quantitative Scoring Engines:** Deterministically scoring **Logical Thinking Ability ($S_{\text{logic}}$)**, **Problem-Solving Clarity ($S_{\text{clarity}}$)**, **Situational Effectiveness ($S_{\text{eff}}$)**, and **Risk Mitigation ($S_{\text{risk}}$)** on standardized $[0, 100]$ scales.

---

## 2. Three Mandated Curriculum Deliverables

In strict accordance with the Day 38 curriculum specification, this framework implements exactly three deliverables:

```
+---------------------------------------------------------------------------------------------------+
|                                  DAY 38 CORE DELIVERABLES                                         |
+------------------------------------+----------------------------------+---------------------------+
| 1. Aptitude AI Design              | 2. Logical Reasoning Model       | 3. Scenario Framework     |
| (interview_ai/aptitude_engine.py)  | (interview_ai/logical_scorer.py) | (scenario_evaluator.py)   |
| - 5 Cognitive Dimensions           | - Premise Grounding (30%)        | - Clarity Analyzer (25%)  |
| - Curated SJT Scenario Registry    | - Causal Deductions (40%)        | - Effectiveness (25%)     |
| - IDEA/CARL Framework Mappings     | - Trade-Off Depth (30%)          | - Risk Mitigation (15%)   |
| - Role-Track Preset Routing        | - Fallacy Detection (-50 max)    | - ATS Dossier Integration |
+------------------------------------+----------------------------------+---------------------------+
```

---

## 3. Cognitive Reasoning Dimensions & Question Taxonomy

The system defines 5 core cognitive dimensions within `CognitiveDimension`:

| Cognitive Dimension | Evaluation Focus | Key Linguistic Indicators | Target Behavioral Outcome |
| :--- | :--- | :--- | :--- |
| **Root Cause Analysis** | Diagnostic troubleshooting without jumping to conclusions. | *"Core bottleneck"*, *"underlying symptom"*, *"isolate failure domain"*. | Identifies root failure mechanism before proposing code changes. |
| **Trade-Off Evaluation** | Balancing competing architectural constraints (CAP, speed vs quality). | *"Downside is"*, *"on the other hand"*, *"at the expense of"*, *"compromise"*. | Weighs operational trade-offs and justifies compromises. |
| **Systemic Thinking** | Second-order effects, cascading dependencies, and blast radius. | *"Downstream impact"*, *"blast radius"*, *"cascading retry storm"*. | Mitigates unintended system-wide repercussions. |
| **Resource Estimation** | Quantitative Fermi estimation and capacity scaling. | *"Order of magnitude"*, *"throughput capacity"*, *"egress saturation"*. | Demonstrates sound numerical intuition under scale. |
| **Hypothesis Testing** | Formulating falsifiable test steps and observability. | *"Initial hypothesis"*, *"verify via logs"*, *"test with canary"*. | Follows scientific method rather than guesswork. |

---

## 4. Ideal Answer Structuring Frameworks

To score problem-solving without subjective evaluator bias, candidate answers are mapped against prescribed cognitive milestones:

### 4.1 The IDEA Framework (Primary Technical Standard)
- **I — Identify Core Premise:** Define the real problem, decouple secondary noise, and acknowledge boundary conditions.
- **D — Define Constraints & Assumptions:** Clarify non-negotiable variables (SLA, budget, schema backwards-compatibility, deadlines).
- **E — Evaluate Alternatives:** Compare at least two distinct approaches (e.g. immediate feature-flag bypass vs database rollback) highlighting pros and cons.
- **A — Action Plan & Mitigation:** Present a step-by-step phased execution sequence accompanied by rollbacks, telemetry monitoring, and post-mortem review.

### 4.2 The CARL Framework (Behavioral Situational Standard)
- **C — Context:** Clarify the situational dilemma, constraints, and conflicting priorities.
- **A — Action:** Detail individual technical and interpersonal interventions.
- **R — Reasoning:** Explain *why* specific choices were favored over alternatives.
- **L — Learning:** Reflect on post-mortem insights and long-term architectural prevention.

---

## 5. Mathematical Formulations

### 5.1 Logical Reasoning Scoring Model ($S_{\text{logic}}$)

$$\text{Raw Logic} = 0.30 \cdot S_{\text{premise}} + 0.40 \cdot S_{\text{causal}} + 0.30 \cdot S_{\text{tradeoff}}$$

$$S_{\text{logic}} = \text{clip}\left(\text{Raw Logic} - \sum \text{Fallacy Deductions}, \, 0.0, \, 100.0\right)$$

#### Logical Fallacy Detection Matrix:
- **False Dilemma ($-10.0$ pts):** Articulating problems as artificial black-and-white binaries (*"the only option is"*, *"we have no choice but to"*).
- **Hasty Conclusion ($-12.0$ pts):** Proposing catastrophic overhauls or aggressive actions without diagnostic isolation (*"just rewrite everything"*, *"fire the developer"*).
- **Circular Reasoning ($-8.0$ pts):** Tautological statements lacking explanatory causal backing (*"it broke because it didn't work"*).
- **Blame Deflection ($-10.0$ pts):** Abrogating ownership toward external groups (*"not my job"*, *"management's fault"*).

### 5.2 Problem-Solving Clarity Score ($S_{\text{clarity}}$)

$$S_{\text{clarity}} = \text{clip}\left(\left(0.35 \cdot S_{\text{signpost}} + 0.30 \cdot S_{\text{causal\_density}} + 0.35 \cdot S_{\text{decisiveness}}\right) \cdot \text{Depth Ratio}, \, 10.0, \, 100.0\right)$$

- **Signposting Score ($S_{\text{signpost}}$):** Measures structural clarity via sequential markers (*"First"*, *"Step 1"*, *"Secondly"*, *"Subsequently"*, *"Finally"*).
- **Decisiveness Score ($S_{\text{decisiveness}}$):** Rewards high-conviction action verbs (*"isolate"*, *"deploy"*, *"rollback"*, *"stabilize"*) while penalizing ambiguity paralysis (*"maybe"*, *"I guess"*, *"might work"*).

### 5.3 Composite Cognitive Aptitude Score ($S_{\text{aptitude}}$)

$$S_{\text{aptitude}} = 0.35 \cdot S_{\text{logic}} + 0.25 \cdot S_{\text{clarity}} + 0.25 \cdot S_{\text{effectiveness}} + 0.15 \cdot S_{\text{risk\_mitigation}}$$

---

## 6. Cognitive Maturity Tier Classification

| Maturity Level | Score Band | Recruiter Behavioral Profile | Hiring Recommendation |
| :--- | :---: | :--- | :---: |
| **EXEMPLARY** | $85.0 - 100.0$ | Methodical root-cause isolation, proactive trade-off nuance, explicit risk containment, zero fallacies. | **STRONG HIRE** |
| **PROFICIENT** | $70.0 - 84.9$ | Solid logical deductions, structured sequential execution, minor trade-off omissions. | **HIRE** |
| **COMPETENT** | $55.0 - 69.9$ | Adequate practical resolution, occasional unstated assumptions, basic safeguards. | **LEAN HIRE** |
| **SUPERFICIAL** | $40.0 - 54.9$ | Surface-level fixes, generic buzzwords, lacks depth and contingency planning. | **LEAN NO HIRE** |
| **DEFICIENT** | $< 40.0$ | Chaotic reasoning, severe fallacy deductions, reckless anti-patterns, blame deflection. | **NO HIRE** |

---

## 7. ATS JSON Schema Payload

```json
{
  "scenario_id": "SJT_INCIDENT_01",
  "scenario_title": "Critical Production Outage During Black Friday Flash Sale",
  "category": "system_incident_escalation",
  "composite_aptitude_score": 88.5,
  "cognitive_maturity": "EXEMPLARY",
  "framework_adherence_percent": 100.0,
  "scores": {
    "logical_reasoning": 89.2,
    "problem_solving_clarity": 91.5,
    "situational_effectiveness": 90.0,
    "risk_mitigation": 95.0,
    "stakeholder_awareness": 85.0
  },
  "diagnostics": {
    "observed_strengths": [
      "High cognitive rigor: Structured deductive reasoning and clear cause-and-effect linkages.",
      "Exceptional structural signposting: Clearly demarcated problem-solving sequence.",
      "Proactive risk containment: Integrates telemetry, rollback plans, and safeguards."
    ],
    "cognitive_flags": [],
    "recruiter_coaching_notes": []
  }
}
```
