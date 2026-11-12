# Candidate HR Score Report Format & Scoring Engine Specification

**Document Version:** 1.0  
**Curriculum Track:** Day 37 – HR Interview Scoring Engine  
**Platform:** Zecpath-AI Talent Platform  
**Target Modules:** `interview_ai/hr_scoring_engine.py`, `interview_ai/weight_config.py`, `interview_ai/hr_score_report.py`  
**Candidate / Author:** Nandith Gireesh  
**Organization:** Zecser Business LLP  

---

## 1. Architectural Overview & Purpose

The **HR Interview Scoring Engine** synthesizes candidate multi-turn responses, speech/text communication signals, behavioral confidence indicators, and narrative consistency into a single calibrated composite score ($S_{\text{composite}} \in [0, 100]$).

Traditional hiring processes suffer from high variability across human interviewers, who assign subjective scores based on recency bias, halo effects, or unstandardized expectations. The Day 37 engine solves this through:
1. **Four Orthogonal Scoring Parameters:** Answer Relevance, Communication Score, Confidence Score, and Factual Consistency.
2. **Configurable Role-Track Weighting:** Dynamic weight profiles tailored to technical engineering, leadership, client-facing, and campus fresher tracks.
3. **Length Normalization:** Mathematical smoothing that ensures fair, equitable evaluation regardless of whether an interview had 3, 5, or 8+ turns.
4. **Explainable Scoring Breakdowns:** Transparent factor point contributions, strengths, risk flags, and calibrated hiring recommendation tiers.

---

## 2. Four Core Scoring Parameters & Mathematical Formulations

### Parameter 1: Answer Relevance ($S_{\text{relevance}} \in [0, 100]$)
Evaluates how directly, thoroughly, and substantively the candidate's answer addresses the specific prompt and category intent:
$$S_{\text{relevance}} = \text{clip}\left(0.40 \cdot S_{\text{intent}} + 0.35 \cdot S_{\text{keywords}} + 0.25 \cdot S_{\text{depth}} - P_{\text{evasion}}, 10.0, 100.0\right)$$
- **$S_{\text{intent}}$:** Semantic alignment between prompt question keywords and candidate answer core premise.
- **$S_{\text{keywords}}$:** Coverage of category-specific domain concepts (e.g. distributed systems, database scaling, conflict resolution, metrics).
- **$S_{\text{depth}}$:** Substantive depth curve (sweet spot: 45–220 words) with $+15$ bonus for concrete quantifiable metrics (e.g. QPS, ms, %, team size).
- **$P_{\text{evasion}}$:** Penalty ($40$ pts) if conversational evasion or non-committal markers are detected (*"I don't know"*, *"skip this"*, *"none of your business"*).

### Parameter 2: Communication Score ($S_{\text{communication}} \in [0, 100]$)
Ingests the 6-dimension linguistic pipeline from Day 35:
$$S_{\text{communication}} = \sum_{d=1}^{6} w_d \cdot S_d$$
- **Fluency ($S_{\text{fluency}}$):** Sentence length variance ($\bar{L} \in [10, 28]$ words) and transition connectives (*therefore*, *furthermore*).
- **Grammar Quality ($S_{\text{grammar}}$):** Subject-verb agreement, tense consistency, and anti-pattern deductions.
- **Vocabulary Range ($S_{\text{vocab}}$):** Length-damped Root Type-Token Ratio ($RTTR = V / \sqrt{N}$) and domain terminology.
- **Clarity of Explanation ($S_{\text{clarity}}$):** Content-word idea density and hand-waving vagueness deductions.
- **Filler Word Control ($S_{\text{filler}}$):** Pure disfluencies (*um*, *uh*) and discourse crutches (*like*, *you know*) on exponential decay curve.
- **Answer Structure ($S_{\text{structure}}$):** Automated extraction of STAR (Situation, Task, Action, Result) or PREP (Point, Reason, Example, Point).

### Parameter 3: Behavioral Confidence Score ($S_{\text{confidence}} \in [0, 100]$)
Ingests the 4-engine behavioral analysis pipeline from Day 36:
$$S_{\text{confidence}} = \text{clip}\left(0.35 \cdot S_{\text{hesitation}} + 0.25 \cdot S_{\text{consistency\_sub}} + 0.25 \cdot S_{\text{sentiment}} + 0.15 \cdot (100 - S_{\text{stress}}), 0.0, 100.0\right)$$
- **Hesitation ($S_{\text{hesitation}}$):** Response latency delay ($>2.8$s delay: 5 pts/s), pause tokens, and repeated word stutters (*"I I"*).
- **Sentiment & Composure ($S_{\text{sentiment}}$):** Professional composure ($0$--$100$) reflecting constructive technical ownership vs defensiveness.
- **Quantitative Stress Index ($S_{\text{stress}}$):** Disfluency frequency per 100 words, stutter clusters, latency freeze, and panic cues mapped to `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.

### Parameter 4: Factual & Narrative Consistency ($S_{\text{consistency}} \in [0, 100]$)
Evaluates truthfulness, absence of contradictions, and narrative coherence across the entire conversation:
$$S_{\text{consistency}} = \text{clip}\left(100.0 - \sum_{i=1}^{k} D_i, 10.0, 100.0\right)$$
- **Within-Turn Retractions:** Deducts $12$ pts (*"actually no wait"*).
- **Semantic Opposition Pairs:** Deducts $25$ pts (*"built alone"* vs *"team built"*).
- **Cross-Turn Timeline Clashes:** Deducts $35$ pts (*"6 years experience"* in Turn 1 vs *"1 year experience"* in Turn 3).

---

## 3. Weight Configuration System

Weights reflect the operational competencies prioritized by different hiring tracks:

$$S_{\text{composite}} = w_{\text{rel}} \cdot S_{\text{rel}}^{\text{norm}} + w_{\text{comm}} \cdot S_{\text{comm}}^{\text{norm}} + w_{\text{conf}} \cdot S_{\text{conf}}^{\text{norm}} + w_{\text{cons}} \cdot S_{\text{cons}}^{\text{norm}}$$

Subject to constraint:
$$\sum_{p \in \mathcal{P}} w_p = 1.0, \qquad \forall p: w_p \in [0.05, 0.60]$$

### Enterprise Role Presets

| Role Track Preset | Answer Relevance ($w_{\text{rel}}$) | Communication ($w_{\text{comm}}$) | Confidence ($w_{\text{conf}}$) | Consistency ($w_{\text{cons}}$) | Target Hiring Focus |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Technical Engineering** | **35%** | 25% | 20% | 20% | Prioritizes deep architectural depth and factual integrity. |
| **Engineering Leadership** | 30% | **30%** | **25%** | 15% | Emphasizes strategic communication, composure, and clarity. |
| **Client-Facing & Solutions** | 25% | **35%** | **25%** | 15% | Prioritizes consultative fluency, persuasion, and presence. |
| **Campus Graduate / Fresher** | **30%** | **30%** | 20% | 20% | Forgiving of initial nervousness; values clarity and honesty. |
| **Standard Balanced** | **30%** | 25% | 25% | 20% | General corporate benchmark for mid-level hiring. |

---

## 4. Length Normalization Mechanics

In live interview workflows, interview length varies ($N \in [2, 10]$ turns). A naive arithmetic average creates severe distortion: a candidate answering 2 easy questions might appear artificially superior to a candidate enduring 8 deep technical probes.

The Length Normalization Engine applies a **three-stage calibration**:

### Stage 1: Bayesian Prior Smoothing
To dampen small-sample volatility, scores are smoothed against a conservative empirical prior ($\mu_0 = 70.0$, effective prior weight $m = 2.0$):
$$\bar{S}_{\text{bayes}} = \frac{m \cdot \mu_0 + \sum_{i=1}^{N} S_i}{m + N}$$

### Stage 2: Turn Progression / Warm-up Weighting
Candidates typically demonstrate increased confidence and depth after initial rapport is established. Later deep-dive turns receive progressive weight:
$$w_i = 0.85 + 0.30 \cdot \frac{i - 1}{\max(1, N - 1)}, \qquad \bar{S}_{\text{recency}} = \frac{\sum_{i=1}^{N} w_i \cdot S_i}{\sum_{i=1}^{N} w_i}$$

Blended parameter score:
$$S_{\text{blended}} = 0.60 \cdot \bar{S}_{\text{recency}} + 0.40 \cdot \bar{S}_{\text{bayes}}$$

### Stage 3: Session Completeness Scaling
If an interview is abandoned early ($N < 3$ turns), a completeness penalty factor $C(N)$ is applied:
$$C(N) = \begin{cases} 1.0 & \text{if completed and } N \ge 3 \\ \max(0.65, 0.65 + 0.10 \cdot N) & \text{if prematurely terminated} \end{cases}$$
$$S^{\text{norm}} = \text{clip}\left(S_{\text{blended}} \cdot C(N), 10.0, 100.0\right)$$

---

## 5. Candidate HR Score Report Schema (ATS JSON Standard)

```json
{
  "candidate_id": "cand_9482b1a",
  "candidate_name": "Arjun Varma",
  "job_role": "Senior Distributed Systems Engineer",
  "experience_years": 7.0,
  "session_id": "sess_hr_3b2f299c79af",
  "evaluation_date": "2026-09-26T10:00:00Z",
  "weight_profile_used": "Technical Engineering Track",
  "composite_score": 93.4,
  "recommendation": "STRONG_HIRE",
  "executive_summary": "Candidate Arjun Varma achieved a length-normalized composite score of 93.4/100 (STRONG HIRE), evaluated across 3 turns under the Technical Engineering Track matrix.",
  "parameter_breakdown": {
    "answer_relevance": {
      "parameter": "answer_relevance",
      "display_name": "Answer Relevance & Depth",
      "raw_score": 95.0,
      "normalized_score": 93.6,
      "weight": 0.35,
      "weighted_contribution": 32.76,
      "percentage_of_total": 35.1,
      "diagnostic_summary": "Candidate addressed prompt intent with 93.6/100 normalized depth."
    },
    "communication_score": {
      "parameter": "communication_score",
      "display_name": "Communication & Structure",
      "raw_score": 94.0,
      "normalized_score": 92.8,
      "weight": 0.25,
      "weighted_contribution": 23.20,
      "percentage_of_total": 24.8,
      "diagnostic_summary": "Articulated ideas with 92.8/100 structural fluency and grammar hygiene."
    },
    "confidence_score": {
      "parameter": "confidence_score",
      "display_name": "Behavioral Confidence & Poise",
      "raw_score": 92.2,
      "normalized_score": 91.5,
      "weight": 0.20,
      "weighted_contribution": 18.30,
      "percentage_of_total": 19.6,
      "diagnostic_summary": "Exhibited composure of 91.5/100 with low hesitation latency."
    },
    "consistency": {
      "parameter": "consistency",
      "display_name": "Factual & Narrative Consistency",
      "raw_score": 100.0,
      "normalized_score": 96.0,
      "weight": 0.20,
      "weighted_contribution": 19.20,
      "percentage_of_total": 20.5,
      "diagnostic_summary": "Maintained narrative alignment at 96.0/100 without factual clashes."
    }
  },
  "length_normalization": {
    "total_turns_evaluated": 3,
    "expected_standard_turns": 5,
    "raw_average_score": 95.3,
    "normalized_score": 93.4,
    "prior_mean": 70.0,
    "prior_weight_m": 2.0,
    "recency_weighted_average": 96.1,
    "session_completeness_factor": 1.0,
    "normalization_adjustment": -1.9
  },
  "communication_subdimensions": {
    "fluency": 92.5,
    "grammar": 95.0,
    "vocabulary": 90.0,
    "clarity": 94.0,
    "filler_control": 100.0,
    "structure": 96.0
  },
  "behavioral_subdimensions": {
    "hesitation_control": 95.5,
    "sentiment_composure": 90.5,
    "narrative_consistency": 100.0,
    "stress_resilience": 85.0
  },
  "turn_score_trajectory": [
    {
      "turn_index": 1,
      "phase": "Introduction",
      "category": "Introduction",
      "relevance": 92.0,
      "communication": 93.0,
      "confidence": 93.2,
      "consistency": 100.0,
      "composite_turn": 94.1
    },
    {
      "turn_index": 2,
      "phase": "Behavioral Core",
      "category": "Behavioral_STAR",
      "relevance": 95.0,
      "communication": 94.5,
      "confidence": 87.2,
      "consistency": 100.0,
      "composite_turn": 94.3
    },
    {
      "turn_index": 3,
      "phase": "Technical Deep Dive",
      "category": "Technical_Depth",
      "relevance": 98.0,
      "communication": 95.0,
      "confidence": 96.2,
      "consistency": 100.0,
      "composite_turn": 97.3
    }
  ],
  "key_strengths": [
    "High contextual relevance and concrete problem-solving depth with quantifiable metrics.",
    "Clear executive articulation using structured STAR/PREP delivery with zero filler crutches.",
    "Authoritative technical presence and composed demeanor under challenging scenarios."
  ],
  "risk_flags": [],
  "recommended_next_steps": [
    "Advance candidate to final technical bar-raiser or hiring manager round.",
    "Validate system architecture depth on large-scale distributed consensus."
  ]
}
```

---

## 6. Hiring Recommendation Tiers

| Composite Score ($S_{\text{composite}}$) | Hiring Recommendation Tier | Operational Guidance |
| :---: | :--- | :--- |
| **88.0 – 100.0** | **`STRONG_HIRE`** | Top percentile talent; exceeds technical and behavioral bar; fast-track offer. |
| **76.0 – 87.9** | **`HIRE`** | Meets all role expectations; strong domain knowledge and clear communication. |
| **65.0 – 75.9** | **`LEAN_HIRE`** | Acceptable core competency; targeted follow-up recommended in identified weak areas. |
| **50.0 – 64.9** | **`LEAN_NO_HIRE`** | Below benchmark threshold; significant communication, relevance, or composure gaps. |
| **0.0 – 49.9** | **`NO_HIRE`** | Critical deficiencies, severe evasiveness, or disqualifying factual contradictions. |
