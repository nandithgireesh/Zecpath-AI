# Deliverable 2: Hiring Fit Calculator & Decision Synthesis
**System:** Zecpath-AI Multi-Modal Enterprise Interview Pipeline  
**Module:** `unified_scoring/hiring_fit_calculator.py`  
**Scope:** Multi-Dimensional Fit Index, Risk Discounting, Percentile Calibration & Gated Decision Synthesis  
**Evaluation Standard:** Calibrated Enterprise Bar Raiser Methodology  

---

## 1. Executive Summary & Purpose

A single linear composite score is insufficient for executive hiring decisions because it fails to capture dimensional balance, cognitive risk factors, and organizational role readiness. A candidate with a high technical score who exhibits toxic blame deflection or severe cross-turn contradictions represents an operational risk that a naive average would obscure.

**Deliverable 2: The Hiring Fit Calculator** (`HiringFitCalculator`) transforms raw multi-round telemetry into a comprehensive **Hiring Fit Percentage (0–100%)**, computes empirical cohort percentile rankings, applies non-linear risk discounts, and synthesizes gated hiring decisions and role-leveling classifications.

---

## 2. Multi-Dimensional Fit Architecture

The calculator evaluates four orthogonal competency pillars by synthesizing cross-round telemetry:

```
[ATS Skill & Exp] + [HR Situational Aptitude]  ──► 1. Technical Competence Fit (0-100)
[Screening Clarity] + [HR Communication Hygiene] ──► 2. Communication Clarity Fit (0-100)
[Screening Sentiment] + [HR STAR Ownership]     ──► 3. Behavioral & Culture Fit (0-100)
[Screening Consistency] + [HR Stress Composure] ──► 4. Adaptability & Trajectory Fit (0-100)
                                                                 │
                                                                 ▼
[Integrity Flags & Contradictions]               ──► 5. Risk & Integrity Discount (-pts)
                                                                 │
                                                                 ▼
                                                  [Net Hiring Fit Percentage (0-100%)]
                                                                 │
                                                                 ▼
                                                  [Cohort Percentile Rank (0.1 - 99.9th)]
```

### 1. Technical Competence Fit ($T_{\text{fit}}$)
Blends verified resume capabilities with live conversational aptitude and architecture triage:
$$T_{\text{fit}} = 0.40 \cdot \text{ATS}_{\text{skill}} + 0.20 \cdot \text{ATS}_{\text{experience}} + 0.40 \cdot \text{HR}_{\text{aptitude}}$$

### 2. Communication Clarity Fit ($C_{\text{fit}}$)
Synthesizes speech-to-text acoustic transcription clarity with interview vocabulary, syntax hygiene, and filler word control:
$$C_{\text{fit}} = 0.45 \cdot \text{Screening}_{\text{clarity}} + 0.55 \cdot \text{HR}_{\text{communication}}$$

### 3. Behavioral & Culture Fit ($B_{\text{fit}}$)
Measures alignment against five enterprise cultural pillars (Ownership, Teamwork, Customer Trust, Adaptability, Ethics):
$$B_{\text{fit}} = 0.40 \cdot \text{Screening}_{\text{behavioral}} + 0.60 \cdot \text{HR}_{\text{cultural\_fit}}$$

### 4. Adaptability & Trajectory Fit ($A_{\text{fit}}$)
Evaluates cognitive agility, responsiveness to dynamic follow-up probes, and composure under situational stress:
$$A_{\text{fit}} = 0.50 \cdot \text{Screening}_{\text{consistency}} + 0.50 \cdot \text{HR}_{\text{confidence\_composure}}$$

---

## 3. Risk & Integrity Discounting Engine

When candidates exhibit operational fallacies, contradictory claims, or eligibility misrepresentations, the calculator applies targeted risk discounts:

| Risk / Fallacy Flag | Severity Tier | Algorithmic Penalty | Operational Rationale |
|---|:---:|:---:|---|
| `CRITICAL_CONTRADICTION` | **CRITICAL** | **-6.0 pts** | Direct factual contradiction between conversational turns (e.g. solo authorship vs subordinate execution). |
| `BLAME_DEFLECTION` | **CRITICAL** | **-5.0 pts** | Externalizing responsibility for production outages onto management or QA teams. |
| `FALSE_DILEMMA` / `FALLACY` | **HIGH** | **-4.0 pts** | Framing complex architectural trade-offs as extreme binaries (e.g. "rewrite or go bankrupt"). |
| `VAGUENESS_DETECTED` | **MODERATE** | **-2.5 pts** | Superficial trade-offs triggering dynamic follow-up probes. |
| Minor Fluency / Hedging | **LOW** | **-2.0 pts** | Excessive hedging or ungrounded conversational claims. |

### Non-Linear Bounding:
To prevent mathematical collapse below zero on multi-fallacy transcripts, total risk penalties are bounded:
$$\text{RiskDiscount} = \min\left(20.0, \, \sum_{j} \text{Penalty}_j\right)$$

---

## 4. Net Hiring Fit Percentage & Percentile Calibration

The **Net Hiring Fit Percentage** ($HFP$) balances multi-round composite points with sub-dimensional harmony and risk discounts:
$$HFP = \max\left(0.0, \, \min\left(100.0, \, 0.50 \cdot C + 0.50 \cdot \left(\frac{T_{\text{fit}} + C_{\text{fit}} + B_{\text{fit}} + A_{\text{fit}}}{4}\right) - 0.50 \cdot \text{RiskDiscount}\right)\right)$$

### Percentile Calibration:
Using an empirical enterprise hiring cohort distribution ($\mu = 68.0, \sigma = 14.5$), the calculator computes the candidate's exact percentile rank:
$$z = \frac{HFP - \mu}{\sigma} = \frac{HFP - 68.0}{14.5}$$
$$\text{Percentile} = \Phi(z) \times 100 = \frac{1}{2} \left[1 + \text{erf}\left(\frac{z}{\sqrt{2}}\right)\right] \times 100$$

---

## 5. Decision Synthesis & Role-Leveling Thresholds

The synthesized decision tier and readiness classification are determined through calibrated thresholds and hard gating:

```
Net Hiring Fit (%)     Gating Status     Recommendation Tier       Readiness Classification
─────────────────────────────────────────────────────────────────────────────────────────────
85.0 - 100.0%          All Gates Passed  STRONG_HIRE               IMMEDIATE_FAST_TRACK
72.0 - 84.9%           All Gates Passed  HIRE                      PRODUCTION_READY
60.0 - 71.9%           All Gates Passed  LEAN_HIRE                 DEVELOPING_WITH_MENTORSHIP
45.0 - 59.9%           Any Gate Status   LEAN_NO_HIRE              SUB_THRESHOLD_UPSKILL
< 45.0% OR             Failed Hard Gate  NO_HIRE                   OPERATIONAL_RISK_REJECT
RiskDiscount >= 12.0
```

### Calibrated Role-Leveling Logic:
1. **Overqualification Escalation:** If Candidate Experience $\ge 12.0$ years, $T_{\text{fit}} \ge 90.0$, and Decision is `STRONG_HIRE` for a standard role, the calculator automatically generates a **Leveling Upgrade Advisory** (e.g. recommending placement into a *Principal Infrastructure Architect* or *Staff Systems Lead* role).
2. **Developing Associate Placement:** If Candidate Experience $< 3.0$ years and Decision is `LEAN_HIRE`, the calculator designates the candidate as a *Developing Associate with Structured Onboarding Mentorship*.

---

## 6. Cohort Calculation Results

| Candidate ID | Name | Net Hiring Fit | Percentile | Risk Discount | Decision Tier | Readiness Level | Calibrated Leveling Tier |
|---|---|:---:|:---:|:---:|---|---|---|
| `SIM-CONF-01` | Aditi Rao | **87.7%** | **91.3th** | 0.0 pts | `STRONG_HIRE` | `IMMEDIATE_FAST_TRACK` | Senior / Lead Architect |
| `SIM-HES-02` | Siddharth Verma | **67.6%** | **48.9th** | 0.0 pts | `LEAN_HIRE` | `DEVELOPING_WITH_MENTORSHIP` | Associate / Developing Engineer |
| `SIM-INEXP-03` | Kavita Patel | **56.6%** | **21.6th** | -1.3 pts | `LEAN_NO_HIRE` | `SUB_THRESHOLD_UPSKILL` | Sub-Threshold for Senior Systems Eng |
| `SIM-OVER-04` | Dr. Rajesh Sundaram | **91.9%** | **95.1th** | 0.0 pts | `STRONG_HIRE` | `IMMEDIATE_FAST_TRACK` | **Principal / Staff Leveling Upgrade** |
| `SIM-INCON-05` | Tarun Khanna | **44.0%** | **4.9th** | -11.0 pts | `NO_HIRE` | `OPERATIONAL_RISK_REJECT` | Disqualified / Operational Risk |

---

## 7. Summary

The Hiring Fit Calculator provides fair, explainable, and multi-dimensional intelligence that eliminates blind spots, protects organizations from toxic or fraudulent hires, and recognizes exceptional senior talent with appropriate leveling recommendations.
