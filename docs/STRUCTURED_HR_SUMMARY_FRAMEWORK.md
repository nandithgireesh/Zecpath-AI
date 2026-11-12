# Zecpath-AI Technical Specification: Structured HR Summary Framework

**Module:** `interview_ai` (Day 39)  
**System Component:** Interview Summary Generator & Inconsistency Detection Engine  
**Target Roles:** Technical Engineering, Leadership, Client-Facing, Campus Freshers  
**Status:** Production Grade (Integrated with Days 33–38 Telemetry)

---

## 1. Executive Overview & System Objectives

Traditional automated interview systems output raw scalar ratings or disconnected metric tables that force recruiters and hiring managers to manually cross-reference turn-by-turn answers. 

The **Zecpath-AI Day 39 Interview Summary Generator** solves this challenge by converting high-dimensional multi-modal telemetry (behavioral STAR execution, 6-axis communication hygiene, acoustic/linguistic stress signals, and IDEA situational judgment logic) into **recruiter-ready insights**.

### Core Technical Objectives
1. **Multi-Dimensional Synthesis**: Holistically balances $S_{\text{behavioral}}$ (30%), $S_{\text{communication}}$ (25%), $S_{\text{composure}}$ (20%), and $S_{\text{aptitude}}$ (25%) into a calibrated composite hiring index.
2. **Cross-Turn & Cross-Modal Inconsistency Detection**: Identifies factual divergences between candidate resume credentials and verbal disclosures, cross-turn narrative contradictions, and verbal-affect discordances.
3. **5-Pillar Cultural Fit Profiling**: Quantifies candidate alignment against core enterprise values: Ownership & Accountability, Collaboration, Customer Centricity, Adaptability, and Transparency & Ethics.
4. **Natural-Language Executive Briefings**: Programmatically crafts publication-grade narrative dossiers tailored for Hiring Manager and Bar Raiser debriefs.
5. **Dual Enterprise Formats**: Exports strictly compliant JSON (Draft-07 schema) for ATS integration and human-readable Markdown scorecards.

---

## 2. Inconsistency Detection Engine Heuristics

The `InconsistencyDetector` operates four deterministic analytical passes over the session transcript:

### 2.1 Cross-Turn Contradiction (`CROSS_TURN_CONTRADICTION`)
- **Trigger**: Candidate claims solo architecture ("single-handedly", "sole engineer", "built it all alone") in an early turn, but subsequently admits subordinate execution ("my tech lead made all decisions", "I only wrote tests", "followed orders") in a later turn.
- **Severity**: `CRITICAL`
- **Penalty**: Direct $-12.0$ pt deduction from composite hiring score per critical incident.

### 2.2 Verbal-Affect Discordance (`VERBAL_AFFECT_DISCORDANCE`)
- **Trigger**: Candidate asserts extreme verbal certainty (`"100% certainty"`, `"trivially easy"`, `"expert without doubt"`) while multi-modal acoustic telemetry records physiological strain:
  $$\text{Stress Index} \ge 65.0 \quad \lor \quad \text{Hesitation Latency} \ge 3.0\,\text{s} \quad \lor \quad \text{Filler Density} \ge 8.0\%$$
- **Severity**: `MODERATE`
- **Action**: Generates a targeted follow-up probing question for the onsite hiring manager to stress-test technical grounding.

### 2.3 Competency-Performance Gap (`COMPETENCY_PERFORMANCE_GAP`)
- **Trigger**: Senior/Lead role applicant ($\ge 5.0$ yrs exp) exhibits elementary cognitive fallacies (`BLAME_DEFLECTION`, `FALSE_DILEMMA`, `CIRCULAR_REASONING`) during situational judgment tests (Day 38).
- **Severity**: `CRITICAL` or `MODERATE`

### 2.4 Factual Experience Mismatch (`FACTUAL_EXPERIENCE_MISMATCH`)
- **Trigger**: Discrepancy of $\ge 3.0$ years between claimed resume tenure ($Y_{\text{resume}}$) and spoken verbal tenure ($Y_{\text{spoken}}$).
- **Severity**: `CRITICAL`

---

## 3. Cultural Fit Scoring Framework

Candidates are evaluated across five key organizational dimensions on a $0 - 100$ scale:

| Dimension | Evaluated Behaviors | Linguistic / Behavioral Cues | Alignment Tiers |
| :--- | :--- | :--- | :---: |
| **Ownership & Accountability** | Extreme ownership, blameless post-mortems vs blame deflection | `"took ownership"`, `"my responsibility"`, `"root cause analysis"` | $\ge 88$: `EXEMPLARY`<br>$70-87$: `STRONG`<br>$50-69$: `MODERATE`<br>$<50$: `WEAK` |
| **Collaboration & Teamwork** | Cross-functional empathy, mentoring peers, driving consensus | `"pair programming"`, `"cross-functional"`, `"aligned stakeholders"` | Same |
| **Customer Centricity** | Preserving customer SLAs, user impact awareness, blast radius | `"SLA impact"`, `"customer trust"`, `"business continuity"` | Same |
| **Adaptability & Growth** | Navigating technical ambiguity, pivoting architecture gracefully | `"adapted"`, `"refactored incrementally"`, `"continuous learning"` | Same |
| **Transparency & Ethics** | Rigorous compliance, PII masking, data integrity, auditability | `"GDPR"`, `"PII masking"`, `"security audit"`, `"refused shortcuts"` | Same |

---

## 4. Mathematical Synthesis & Role Leveling

### Holistic Composite Score ($S_{\text{holistic}}$):
$$S_{\text{holistic}} = \max\Big(0.0, \; \big(0.30 \cdot S_{\text{behavioral}} + 0.25 \cdot S_{\text{comm}} + 0.20 \cdot S_{\text{composure}} + 0.25 \cdot S_{\text{aptitude}}\big) - 12.0 \cdot N_{\text{crit}}\Big)$$
Where $N_{\text{crit}}$ is the number of identified critical inconsistencies.

### Calibrated Hiring Recommendation Thresholds:
* **Strong Hire (`STRONG_HIRE`)**: $S_{\text{holistic}} \ge 85.0$ and $N_{\text{crit}} = 0$. Fast-track to executive offer.
* **Hire (`HIRE`)**: $72.0 \le S_{\text{holistic}} < 85.0$ and $N_{\text{crit}} = 0$. Standard production-ready onboarding.
* **Lean Hire (`LEAN_HIRE`)**: $60.0 \le S_{\text{holistic}} < 72.0$ or ($N_{\text{crit}} = 1$ with raw score $\ge 65.0$). Targeted onsite probing required.
* **Lean No Hire (`LEAN_NO_HIRE`)**: $45.0 \le S_{\text{holistic}} < 60.0$. Sub-threshold for requested seniority tier.
* **No Hire (`NO_HIRE`)**: $S_{\text{holistic}} < 45.0$ or severe operational risk/fabrication. Rejection.

---

## 5. ATS JSON Schema Compliance

The output conforms to [hr_interview_summary_schema.json](file:///d:/Zecpath-AI%20-%20Copy/templates/hr_interview_summary_schema.json). Key fields include:
- `summary_id`: Globally unique identifier `SUM-<cand_id>-<timestamp>`
- `overall_performance`: Detailed numerical scores, hiring recommendation, and executive verdict
- `candidate_strengths`: Array of evidence-backed strengths
- `candidate_weaknesses`: Array of actionable developmental gaps
- `cultural_fit_indicators`: Array of dimension scores, evidence quotes, and recruiter observations
- `inconsistencies`: Array of typed contradiction objects with recommended probing questions
- `natural_language_report`: Formatted narrative paragraphs ready for hiring manager debriefs
