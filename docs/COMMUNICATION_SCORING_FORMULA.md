# Day 35: Communication Skill Evaluation Scoring Formula & Bias Reduction Specification

**Author:** Nandith Gireesh  
**Organization:** Zecser Business LLP  
**System:** Zecpath-AI Enterprise Automated HR Screening & Interview Platform  
**Target Module:** `interview_ai/communication_evaluator.py`  
**Specification Version:** 1.0.0 (Production Standard)  
**Date:** September 2026  

---

## 1. Executive Summary & Objective

In human and automated interviews alike, assessing candidate communication is often the most subjective, biased, and inconsistent dimension. Interviewers frequently confuse rhetorical verbosity with genuine clarity, penalize candidates with non-native accents, or overlook heavy verbal disfluencies in favor of pleasant demeanor.

The **Day 35 Communication Skill Evaluation Engine** establishes an objective, deterministic, and bias-reduced evaluation framework. It measures candidate communication across six orthogonal linguistic dimensions, combines them using role-tailored weighting matrices, and applies mathematical normalization to ensure fairness across native and non-native English speakers.

### Core Objectives:
1. **Multi-Dimensional Objective Measurement:**
   - **Fluency (sentence continuity):** Measures clause flow, average sentence length, and transition connectors.
   - **Grammar Quality:** Evaluates structural agreements, tense consistency, and punctuation health.
   - **Vocabulary Range:** Implements length-damped Root Type-Token Ratio (RTTR) to assess lexical diversity without penalizing answer length.
   - **Clarity of Explanation:** Quantifies idea density and penalizes ambiguous, hand-waving expressions.
   - **Filler Word Detection:** Categorizes pure fillers (*"um"*, *"uh"*) and discourse crutches (*"like"*, *"you know"*, *"basically"*) with density decay scoring.
   - **Answer Structure:** Evaluates STAR framework alignment (Situation, Task, Action, Result) for behavioral questions and PREP framework (Point, Reason, Example, Point) for technical claims.
2. **Assign Composite Communication Score (0–100):** Provides a transparent, explainable 0–100 score.
3. **Bias-Reduction Normalization:** Normalizes for ESL non-native speakers, scales for length invariance (preventing verbosity bias), and tunes weights for technical vs non-technical roles.

---

## 2. Subsystem Architecture

```
+---------------------------------------------------------------------------------------+
|                                HRInterviewFlowEngine                                  |
|                                                                                       |
|  1. Candidate Spoken Utterance Transcript Ingested                                    |
|  2. Turn Telemetry Captured (Word Count, Response Latency, Question Context)          |
|  3. Dispatched to CommunicationEvaluator                                              |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                     interview_ai/communication_evaluator.py                           |
|                                                                                       |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 1: FluencyAnalyzer                                                 |  |
|  | - Clause flow, avg sentence length (ideal: 10-28 words), transition connectives |  |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 2: GrammarQualityAnalyzer                                          |  |
|  | - Subject-verb agreement, auxiliary usage, terminal punctuation, capitalization |  |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 3: VocabularyAnalyzer                                              |  |
|  | - Root Type-Token Ratio (RTTR = Unique / sqrt(Total)), domain sophistication     |  |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 4: ClarityAnalyzer                                                 |  |
|  | - Idea density (content words / total words), vagueness deduction               |  |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 5: FillerWordDetector                                              |  |
|  | - Pure disfluencies (um, uh) & discourse crutches (like, you know, basically)   |  |
|  +---------------------------------------------------------------------------------+  |
|  | Sub-Analyzer 6: AnswerStructureAnalyzer                                         |  |
|  | - STAR framework (Situation, Task, Action, Result)                             |  |
|  | - PREP framework (Point, Reason, Example, Point)                                |  |
|  +---------------------------------------------------------------------------------+  |
|                                           |                                           |
|                                           v                                           |
|  +---------------------------------------------------------------------------------+  |
|  | Master Evaluator & Bias-Reduction Normalization Layer                           |  |
|  | 1. Compute Raw Composite: S_raw = Sum(w_i * S_i)                                |  |
|  | 2. Apply ESL / Non-Native Fairness Boost (Logic > Idiom flair)                  |  |
|  | 3. Apply Length-Invariance Scaling (Crisp concise parity with long answers)     |  |
|  | 4. Categorize Proficiency Tier & Generate Actionable Recruiter Feedback         |  |
|  +---------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------+
```

---

## 3. Detailed Mathematical Formulations per Dimension

Let a candidate response $T$ consist of tokens $W = (w_1, w_2, \dots, w_N)$ and sentences $S = (s_1, s_2, \dots, s_M)$.

### 3.1 Dimension 1: Fluency & Sentence Continuity ($S_{\text{fluency}}$)

Fluency measures the candidate's ability to maintain coherent discourse flow across sentence boundaries without jarring fragmentation or unpunctuated run-on sentences.

#### 1. Average Sentence Length ($\mu_{\text{len}}$):
$$\mu_{\text{len}} = \frac{N}{M}$$
- Ideal professional conversational range: $10 \le \mu_{\text{len}} \le 28$.
- Fragmentation penalty: If $\mu_{\text{len}} < 6$, deduct $15.0$ points.
- Run-on penalty: If $\mu_{\text{len}} > 45$, deduct $15.0$ points.

#### 2. Discourse Transition Density ($\rho_{\text{trans}}$):
Discourse transitions connect clauses logically across four categories:
- **Causation/Result:** *therefore*, *consequently*, *as a result*, *because*, *thus*, *hence*.
- **Contrast/Nuance:** *however*, *on the other hand*, *nevertheless*, *although*, *yet*, *despite*.
- **Addition/Elaboration:** *furthermore*, *in addition*, *moreover*, *specifically*, *for instance*, *subsequently*.

$$\rho_{\text{trans}} = \frac{|\text{Matched Connectors}|}{\max(1, M)}$$
- If $\rho_{\text{trans}} \ge 0.50$: add $+15.0$ bonus.
- If $0.25 \le \rho_{\text{trans}} < 0.50$: add $+8.0$ bonus.

#### 3. Fragmentation Penalty:
$$P_{\text{frag}} = \min(15.0, |\text{Ellipses / Broken Starts}| \times 5.0)$$

$$S_{\text{fluency}} = \text{clip}\left(75.0 + \Delta_{\text{len}} + \text{Bonus}_{\text{trans}} - P_{\text{frag}} - P_{\text{terse}}, 10.0, 100.0\right)$$

---

### 3.2 Dimension 2: Grammar Quality ($S_{\text{grammar}}$)

Grammar quality measures structural correctness, subject-verb agreement, auxiliary verb usage, and punctuation integrity.

#### 1. Grammatical Anti-Pattern Detection ($E_{\text{grammar}}$):
Regex heuristics scan for common structural errors:
- Subject-verb mismatches: `\b(we|they|you)\s+was\b`, `\b(he|she|it)\s+(were|don't)\b`, `\b(i)\s+(is|are)\b`
- Double past-tense corruptions: `\b(did not|didn't)\s+(went|had|saw|built|wrote)\b`
- Modal corruptions: `\b(could|should|would)\s+of\b`
- Double negatives: `\b(haven't|hasn't)\s+no\b`

#### 2. Punctuation Health:
- Terminal sentence punctuation check: deduct $6.0$ points if unpunctuated.
- Capitalization integrity: deduct $4.0$ points for lowercase initial letter.
- Lowercase *"i"* penalty: deduct $\min(10.0, |\text{lowercase i}| \times 3.0)$.

$$S_{\text{grammar}} = \text{clip}\left(95.0 - (|E_{\text{grammar}}| \times 12.0) - P_{\text{punct}} - P_{\text{cap}}, 15.0, 100.0\right)$$

---

### 3.3 Dimension 3: Vocabulary Range & Lexical Sophistication ($S_{\text{vocab}}$)

Standard Type-Token Ratio ($\text{TTR} = \frac{V}{N}$) degrades mathematically as response length increases because speakers inevitably reuse common grammatical words. To eliminate this length bias, Zecpath-AI implements **Root Type-Token Ratio (RTTR)**:

#### 1. Length-Damped Root Type-Token Ratio:
$$\text{RTTR} = \frac{V}{\sqrt{N}}$$
Where $V$ is the number of distinct unique word stems and $N$ is total tokens.
$$\text{Baseline}_{\text{vocab}} = \min\left(88.0, \text{RTTR} \times 16.5\right)$$

#### 2. Domain Lexical Sophistication:
Target domain vocabularies reward candidates who use precise professional terminology:
- **Technical Lexicon:** *concurrency*, *distributed*, *throughput*, *latency*, *idempotent*, *sharding*, *refactored*, *asynchronous*, *benchmarked*, *regression*.
- **Business Lexicon:** *stakeholder*, *governance*, *turnaround*, *strategic*, *cross-functional*, *alignment*, *procurement*, *retrospective*, *consensus*.

$$\text{Bonus}_{\text{domain}} = \min(15.0, |\text{Domain Matches}| \times 4.0)$$

#### 3. Monotony / Word Repetition Penalty:
Excluding stopwords, non-grammatical words repeated $\ge 4$ times in short answers incur:
$$P_{\text{repeat}} = \min\left(15.0, \sum_{w \in W_{\text{content}}} \max(0, \text{count}(w) - 3) \times 3.0\right)$$

$$S_{\text{vocab}} = \text{clip}\left(\text{Baseline}_{\text{vocab}} + \text{Bonus}_{\text{domain}} - P_{\text{repeat}}, 20.0, 100.0\right)$$

---

### 3.4 Dimension 4: Clarity of Explanation ($S_{\text{clarity}}$)

Clarity evaluates information density, readability, and freedom from hand-waving colloquialisms.

#### 1. Content Word (Idea) Density ($\rho_{\text{idea}}$):
$$\rho_{\text{idea}} = \frac{|\text{Content Words}|}{N}$$
Where content words exclude function stopwords (nouns, lexical verbs, descriptive adjectives).
- $\rho_{\text{idea}} \ge 0.55$: $+14.0$ points (Dense, substantive explanation)
- $0.42 \le \rho_{\text{idea}} < 0.55$: $+8.0$ points
- $\rho_{\text{idea}} < 0.30$: $-15.0$ points (Rambling, low information density)

#### 2. Hand-Waving Vagueness Deduction:
Penalizes expressions indicating incomplete knowledge (*"and all"*, *"and stuff"*, *"things like that"*, *"basically just"*):
$$P_{\text{vague}} = |\text{Vague Hits}| \times 12.0$$

$$S_{\text{clarity}} = \text{clip}\left(80.0 + \Delta_{\text{idea}} - P_{\text{vague}} - P_{\text{terse}}, 10.0, 100.0\right)$$

---

### 3.5 Dimension 5: Filler Word Detection ($S_{\text{filler}}$)

Verbal disfluencies distract interviewers and signal nervousness or lack of structured thought. The engine tracks two tiers of filler words:
1. **Pure Fillers:** *um*, *uh*, *er*, *ah*, *erm*, *umm*, *uhh*.
2. **Discourse Fillers & Crutches:** *like*, *you know*, *i mean*, *basically*, *literally*, *actually*, *sort of*, *kind of*, *at the end of the day*, *to be honest*.

#### 1. Filler Rate Percentage:
$$\text{FillerRate} = \left(\frac{|\text{Total Fillers}|}{\max(1, N)}\right) \times 100\%$$

#### 2. Density Decay Scoring Curve:
$$S_{\text{filler}} = \begin{cases}
100.0 - (\text{FillerRate} \times 3.0), & \text{if } \text{FillerRate} \le 1.5\% \\
95.0 - ((\text{FillerRate} - 1.5) \times 8.0), & \text{if } 1.5\% < \text{FillerRate} \le 4.0\% \\
75.0 - ((\text{FillerRate} - 4.0) \times 6.5), & \text{if } 4.0\% < \text{FillerRate} \le 8.0\% \\
\max(20.0, 50.0 - ((\text{FillerRate} - 8.0) \times 4.0)), & \text{if } \text{FillerRate} > 8.0\%
\end{cases}$$

---

### 3.6 Dimension 6: Answer Structure ($S_{\text{structure}}$)

Answers must demonstrate logical progression rather than stream-of-consciousness rambling.

#### A. STAR Framework (Behavioral Questions)
Assesses four narrative components:
1. **Situation (S):** Context markers (*"when I was at"*, *"in my previous role"*, *"during my project"*).
2. **Task (T):** Objective (*"my objective was"*, *"the challenge was"*, *"we needed to"*).
3. **Action (A):** Personal ownership (*"I architected"*, *"I resolved"*, *"my approach was"*).
4. **Result (R):** Quantified outcome (*"which reduced"*, *"resulting in"*, *metrics, %, p99, latency*).

$$\text{Score}_{\text{STAR}} = \begin{cases}
98.0, & \text{if 4/4 elements matched} \\
85.0, & \text{if 3/4 elements matched} \\
70.0, & \text{if 2/4 elements matched} \\
50.0, & \text{if 1/4 elements matched} \\
30.0, & \text{if 0/4 elements matched}
\end{cases}$$

#### B. PREP Framework (Technical / General Assertions)
Assesses argument structure:
1. **Point (P):** Core thesis (*"in my view"*, *"my core philosophy"*, *"the primary reason"*).
2. **Reason (R):** Technical rationale (*"because"*, *"due to the fact that"*, *"this allows"*).
3. **Example (E):** Concrete application (*"for instance"*, *"for example"*, *"using Redis"*).
4. **Point Summary (P):** Takeaway (*"ultimately"*, *"in conclusion"*, *"therefore"*).

$$\text{Score}_{\text{PREP}} = \begin{cases}
92.0, & \text{if } \ge 3 \text{ elements matched} \\
75.0, & \text{if 2 elements matched} \\
55.0, & \text{if 1 element matched} \\
35.0, & \text{if 0 elements matched}
\end{cases}$$

---

## 4. Composite Communication Scoring & Weighting Matrices

The raw composite communication score is computed as a weighted linear combination tailored to the role track:

$$S_{\text{raw}} = \sum_{i \in \text{Dimensions}} w_i \cdot S_i$$

### Role-Track Weighting Matrix

| Dimension | Technical Track Weight ($w_{\text{tech}}$) | Non-Technical Track Weight ($w_{\text{non\_tech}}$) | Rationale |
| :--- | :---: | :---: | :--- |
| **Fluency** | 20% | 20% | Ensures consistent conversational flow |
| **Grammar** | 15% | 15% | Professional grammatical hygiene |
| **Vocabulary** | 15% | 20% | Non-technical roles demand higher rhetorical range |
| **Clarity** | 20% | 15% | Technical roles prioritize precise, unambiguous explanations |
| **Filler Discipline** | 15% | 15% | Eliminates verbal crutch distractions |
| **Answer Structure** | 15% | 15% | Enforces structured problem-solving (STAR/PREP) |
| **Total** | **100%** | **100%** | Standardized 0–100 scale |

---

## 5. Bias-Reduction Normalization Framework

To prevent unfair discrimination against non-native speakers, introverted candidates, or concise communicators, the raw score undergoes two normalization stages:

### 5.1 ESL / Non-Native English Speaker Fairness Adjustment
Non-native English speakers often express highly logical, technically rigorous ideas using simpler vocabulary. Penalizing them for vocabulary range introduces cultural/linguistic bias.

$$\Delta_{\text{ESL}} = \begin{cases}
\min\left(7.0, (72.0 - S_{\text{vocab}}) \times 0.45\right), & \text{if } S_{\text{structure}} \ge 75.0 \land S_{\text{clarity}} \ge 75.0 \land S_{\text{vocab}} < 72.0 \\
0.0, & \text{otherwise}
\end{cases}$$

*Principle:* If a candidate demonstrates excellent answer structure ($\ge 75$) and crystal-clear clarity ($\ge 75$), they receive up to $+7$ points to compensate for simpler vocabulary.

### 5.2 Length-Invariance Scaling (Anti-Verbosity Bias)
Many scoring models artificially reward candidates who ramble for 200 words simply because they output more tokens. Conversely, concise candidates ($20-45$ words) who answer directly without fluff often get penalized.

$$\Delta_{\text{concise}} = \begin{cases}
+5.0, & \text{if } 20 \le N \le 45 \land |\text{Structure Elements}| \ge 3 \land S_{\text{filler}} \ge 85.0 \\
0.0, & \text{otherwise}
\end{cases}$$

### Final Normalized Score:
$$S_{\text{normalized}} = \text{clip}\left(S_{\text{raw}} + \Delta_{\text{ESL}} + \Delta_{\text{concise}}, 0.0, 100.0\right)$$

---

## 6. Communication Proficiency Tiers & Rubrics

| Score Range | Proficiency Tier | Behavioral Characteristics | Recruiter Recommendation |
| :---: | :--- | :--- | :--- |
| **88 – 100** | **Exceptional** | Flawless structure, articulate phrasing, zero fillers, natural transitions, high idea density. | Strong hire on communication; suitable for executive/client-facing interactions. |
| **75 – 87** | **Proficient** | Clear, professional articulation; minor informalities; structured logic; minimal fillers. | Fully meets enterprise hiring standards. |
| **60 – 74** | **Developing** | Understandable but shows noticeable fillers (*like*, *you know*), sentence fragmentation, or missing STAR results. | Acceptable for internal engineering roles; coaching recommended. |
| **< 60** | **Needs Coaching** | Heavy disfluency, hand-waving vagueness (*stuff and all*), broken grammar, unstructured rambling. | Significant communication bottleneck. |

---

## 7. ATS Telemetry Integration & Recruiter Feedback

Each turn exports structured communication telemetry into the ATS candidate evaluation dossier:

```json
{
  "communication_summary": {
    "average_score": 89.2,
    "proficiency_tier": "Exceptional",
    "overall_fluency": 92.5,
    "overall_grammar": 95.0,
    "overall_vocabulary": 84.0,
    "overall_clarity": 90.0,
    "overall_structure": 91.5,
    "total_fillers_detected": 2,
    "strengths": [
      "Exceptional sentence continuity with natural discourse transitions.",
      "High structural grammatical precision.",
      "Strong structural narrative organization (STAR framework)."
    ],
    "areas_for_improvement": [
      "Continue maintaining high-clarity professional articulation."
    ]
  }
}
```
