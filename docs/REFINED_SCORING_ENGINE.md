# Day 42 — Deliverable 3: Refined Scoring Engine & Calibration Architecture
**Zecpath-AI Enterprise Talent Acquisition Platform**  
**Author:** Nandith Gireesh | **Organization:** Zecser Business LLP | **Date:** October 2026  

---

## 1. Executive Summary & Objective

In multi-round AI talent evaluation, boundary anomalies and edge cases can distort scoring accuracy. Empirical evaluations in Day 40 and Day 41 identified four critical scoring vulnerabilities in early prototypes:
1. **Hesitation Penalty Over-Sensitivity:** Deep analytical formulations on complex system architecture questions were penalized as nervous hesitation, creating false negatives for thoughtful candidates.
2. **Penalty Double-Dipping Collapse:** Candidates with multiple behavioral red flags (e.g. contradictions + blame deflection + fallacies) suffered uncapped cumulative deductions, driving scores into artificial collapse.
3. **Overqualification Economic Misalignment:** Senior candidates with 12+ years of experience were granted raw scores exceeding 92 pts, but human panels hesitated to award Strong Hire due to flight risk and role economics without a clear leveling upgrade.
4. **Edge-Case Fragility:** Zero-length transcripts, audio dropouts, or out-of-bounds parameters risked division-by-zero or floating-point instability.

**Deliverable 3** implements the **Refined Scoring Engine** (`interview_ai/refined_scoring_engine.py`), delivering mathematical calibration, bounded penalty guarantees, and an automated Overqualification Leveling Index ($OLI$).

---

## 2. Mathematical Formalisms & Anomaly Resolutions

### 2.1 Anomaly Resolution 1: Cognitive Deliberation Ratio (CDR)
Instead of applying linear acoustic penalties for pauses $> 2.0$s, the engine evaluates the candidate's speech formulation ratio:
$$\text{CDR} = \frac{\text{Word Count}_{\text{answer}}}{\text{Latency (seconds)}}$$
* **Analytical Pause Classification:** If $\text{Latency} \ge 2.0$s, $\text{Word Count} \ge 50$ words, and $\text{CDR} \ge 15.0$ words/sec, the pause is classified as **deliberate cognitive structuring** rather than uncertain hesitation.
* **Composure Restoration:** Up to 75% of the latency penalty is discounted:
  $$\Delta_{\text{composure}} = \min\left(10.0, \; (\text{Latency} - 1.5) \times 4.0 \times 0.75\right)$$
* **Impact:** For hesitant candidate Siddharth Verma (`SIM-HES-02`), whose solid 85-word explanation of dual-write replication followed a 3.8s pause, composure adjusted from 68.0 to 74.9, lifting the refined score from 65.0 to **68.5**, aligning with human ground truth (68.2).

### 2.2 Anomaly Resolution 2: Tiered Anti-Double-Dipping Penalty Bounding
To prevent penalty cascade and score collapse, the engine partitions flags into bounded sub-categories and enforces a global ceiling:
$$\text{Penalty}_{\text{linguistic}} = \min(6.0, \; \text{vagueness} + \text{fillers})$$
$$\text{Penalty}_{\text{behavioral}} = \min(8.0, \; \text{deflection} + \text{contradiction})$$
$$\text{Penalty}_{\text{fallacy}} = \min(4.0, \; \text{fallacies})$$
$$\text{Penalty}_{\text{net}} = \min(12.0, \; \text{Penalty}_{\text{linguistic}} + \text{Penalty}_{\text{behavioral}} + \text{Penalty}_{\text{fallacy}})$$
* **Impact:** For inconsistent candidate Tarun Khanna (`SIM-INCON-05`), uncapped deductions previously reached $-16.5$ pts, destabilizing composite synthesis. The bounded penalty caps deductions at $-12.0$ pts, producing a stable score of **42.5** while strictly preserving the **`NO_HIRE`** verdict.

### 2.3 Anomaly Resolution 3: Overqualification Leveling Index ($OLI$)
Senior talent exceeding target role scope is objectively recognized without distorting base grading:
$$\text{OLI} = \left(\frac{\text{Experience (years)}}{10.0}\right) \times \left(\frac{\text{Composite Score}}{100.0}\right)$$
* If $\text{Experience} \ge 12.0$y and $\text{Score} \ge 88.0 \implies \textbf{STAFF\_PRINCIPAL\_UPGRADE}$
* If $\text{Experience} \ge 8.0$y and $\text{Score} \ge 85.0 \implies \textbf{SENIOR\_LEAD\_UPGRADE}$
* If $\text{Experience} \ge 15.0$y and $\text{Score} \ge 90.0 \implies \textbf{DIRECTOR\_EXECUTIVE\_UPGRADE}$
* **Impact:** For Dr. Rajesh Sundaram (`SIM-OVER-04`), $OLI = 1.291$, formally escalating the placement recommendation from DevOps Engineer to Staff / Principal Architect.

### 2.4 Anomaly Resolution 4: Edge-Case & Null-Input Resiliency
* All input scores are clamped to $[0.0, 100.0]$ via $\max(0.0, \min(100.0, x))$.
* Zero-length answers, audio dropouts, and empty transcripts default cleanly to safe sub-threshold evaluations without triggering `ZeroDivisionError` or unhandled exceptions.

---

## 3. Comparative Cohort Evaluation (Baseline vs. Refined)

| Candidate ID | Candidate Name | Role Track | Baseline Score | Refined Score | Human Truth | Decision Tier | Anomaly Resolution Applied |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **`SIM-CONF-01`** | Aditi Rao | Cloud Architect | 90.3 | **90.3** | 89.7 | `STRONG_HIRE` | Baseline confirmed; zero penalties. |
| **`SIM-HES-02`** | Siddharth Verma | Data Infra Eng | 65.0 | **68.5** | 68.2 | `LEAN_HIRE` | **CDR Hesitation Filter:** Pause discounted, +3.5 pts. |
| **`SIM-INEXP-03`** | Kavita Patel | Systems Eng | 55.8 | **55.8** | 52.8 | `LEAN_NO_HIRE` | Sub-threshold autonomy confirmed. |
| **`SIM-OVER-04`** | Dr. Rajesh Sundaram | DevOps Eng | 92.2 | **92.2** | 89.5 | `STRONG_HIRE` | **Leveling Upgrade:** $OLI = 1.291 \to$ Staff Architect. |
| **`SIM-INCON-05`** | Tarun Khanna | Backend Lead | 40.1 | **42.5** | 43.5 | `NO_HIRE` | **Anti-Double-Dipping:** Penalty capped at $-12.0$ pts. |

---

## 4. Production Code Reference

```python
from interview_ai.refined_scoring_engine import RefinedScoringEngine

engine = RefinedScoringEngine()

summary = engine.evaluate_candidate(
    candidate_id="SIM-HES-02",
    candidate_name="Siddharth Verma",
    target_role="Data Infrastructure Engineer",
    experience_years=4.0,
    semantic_relevance=72.0,
    communication_score=68.0,
    raw_composure=64.0,
    consistency_score=74.0,
    latency_seconds=3.8,
    answer_word_count=85,
    flags_or_penalties=["HESITATION_DETECTED"],
)

print(f"Refined Score: {summary.net_refined_score}")  # 68.5
print(f"Decision: {summary.final_decision.value}")     # LEAN_HIRE
print(f"Fixes Applied: {summary.anomaly_fixes_applied}")
```
