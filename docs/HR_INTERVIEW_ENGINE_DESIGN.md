# AI HR Interview System: Architectural Design & Question Flow Specification
**Zecpath-AI Enterprise Talent Acquisition Platform**  
**Document Version:** 1.0.0 | **Author:** Nandith Gireesh (Zecser Business LLP) | **Date:** September 2026  
**Curriculum Reference:** Day 33 - Designing an AI HR Interview System (Architecture, Flow & State Modeling)

---

## Executive Summary

The **AI HR Interview System** (`interview_ai/`) provides an automated, adaptive conversational evaluation engine designed to assess behavioral competencies, professional maturity, culture fit, and role-specific readiness. Moving beyond rigid, one-size-fits-all scripts, the engine operates on a dynamic **$2 \times 2$ matrix** (Experience Tier $\times$ Role Track) across **6 standardized HR categories**, orchestrating a 4-phase conversational state machine with real-time response telemetry and heuristic follow-up probing.

This document fulfills the three mandated deliverables of Day 33:
1. **Deliverable 1: HR Interview AI Structure Diagram** (High-level system topology, module interactions, and execution pipeline)
2. **Deliverable 2: Question Bank Architecture** (Taxonomy of 6 HR categories, $2 \times 2$ role-based matrix, and metadata indexing)
3. **Deliverable 3: Interview Flow Design Document** (Finite State Machine phase transitions, state capture structures, and follow-up eligibility heuristics)

---

## Deliverable 1: HR Interview AI Structure Diagram

### 1.1 Architectural Topology

The system is decoupled into modular layers: **Configuration & Telemetry**, **Taxonomy & Schema**, **Curated Question Bank**, **Adaptive Question Generator**, and the **Finite State Machine Flow Engine**.

```
+--------------------------------------------------------------------------------------------------+
|                                    CANDIDATE CLIENT INTERFACE                                    |
|                         (Web Portal / Mobile App / WebRTC Audio Streaming)                       |
+-------------------------------------------------+------------------------------------------------+
                                                  |  (Audio / Text Input & Latency Metrics)
                                                  v
+--------------------------------------------------------------------------------------------------+
|                                      HR INTERVIEW FLOW ENGINE                                    |
|                                (interview_ai/hr_flow_engine.py)                                  |
|                                                                                                  |
|  +---------------------------+   +-----------------------------+   +--------------------------+  |
|  |   Session State Store     |   |   Phase Transition FSM      |   |   Response & Telemetry   |  |
|  | - Session UUID            |   | - INTRODUCTION              |   |   Capture Buffer         |  |
|  | - Candidate Metadata      |   | - CORE_HR                   |   | - Raw Speech Text        |  |
|  | - Active Question Pointer |   | - ROLE_BASED_EVALUATION     |   | - Latency & Word Count   |  |
|  | - Turn History            |   | - CLOSING                   |   | - Behavioral Themes      |  |
|  +---------------------------+   +-----------------------------+   +--------------------------+  |
+-------------------------------------------------+------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
+--------------------------------------------------+   +-------------------------------------------+
|            ADAPTIVE QUESTION GENERATOR           |   |         FOLLOW-UP ELIGIBILITY ENGINE      |
|        (interview_ai/hr_question_generator.py)   |   |        (Heuristic Probing Analyzer)       |
|                                                  |   |                                           |
| - Resolves Candidate Matrix Quadrant             |   | - Evaluates Word Count (< 15 words)       |
| - Sequences 4-Phase Question Trajectory          |   | - Detects Conflict Avoidance ("nobody",)  |
| - Balances Universal vs Domain Probes            |   | - Flags Vague Team Contributions          |
| - Injects Dynamic Personalization                |   | - Triggers Targeted In-Depth Probes       |
+------------------------+-------------------------+   +-------------------------------------------+
                         |
                         v
+--------------------------------------------------------------------------------------------------+
|                                    CURATED HR QUESTION BANK                                      |
|                               (24 Standardized Question Vectors)                                 |
|                                                                                                  |
|   Matrix Quadrants:                                                                              |
|   1. FRESHER / TECHNICAL        (Foundations, Academics, Collaboration, Upskilling)              |
|   2. FRESHER / NON-TECHNICAL    (Interpersonal, Problem Solving, Communication, Adaptability)    |
|   3. EXPERIENCED / TECHNICAL    (Architecture, Cross-functional Align, Scalability, Mentorship)  |
|   4. EXPERIENCED / NON-TECHNICAL(Strategic Planning, Stakeholder Negotiation, Conflict Mgmt)   |
|                                                                                                  |
|   Categories Assessed:                                                                           |
|   [1] Self-Introduction  [2] Career Journey  [3] Strengths & Weaknesses                           |
|   [4] Teamwork & Culture [5] Career Goals    [6] Availability & Commitment                       |
+--------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+--------------------------------------------------------------------------------------------------+
|                                    ATS EXPORT & DOSSIER REPORT                                   |
|              (Session Audit Log, Transcript with Timestamps, Competency Summaries)               |
+--------------------------------------------------------------------------------------------------+
```

### 1.2 Component Responsibility Matrix

| Module | Primary Class / Component | Responsibilities & Design Patterns |
| :--- | :--- | :--- |
| `hr_models.py` | `HRCategory`, `ExperienceTier`, `RoleTrack`, `InterviewPhase`, `InterviewTurnState`, `HRInterviewConfig`, `HRInterviewSession` | Defines immutable enums, strict Pydantic schemas, auto-classification factory methods, and full telemetry serialization contracts. |
| `hr_question_generator.py` | `HRQuestionBank`, `HRQuestionGenerator` | Houses the 24-question vector bank indexed by matrix quadrant and category; calculates dynamic interview trajectories; evaluates response depth to trigger adaptive follow-ups. |
| `hr_flow_engine.py` | `HRInterviewFlowEngine` | Implements the conversational state machine; enforces phase sequencing; captures timestamped candidate transcripts; extracts behavioral themes; exports structured ATS session dossiers. |
| `interview.py` | CLI Entrypoint & Factory API | Exposes high-level helper functions (`create_hr_interview_session`) and interactive command-line simulation runners. |

---

## Deliverable 2: Question Bank Architecture

### 2.1 The 6 Standardized HR Categories

The interview framework assesses candidate suitability across 6 core behavioral dimensions derived from modern corporate human resources best practices:

```
+-----------------------------------------------------------------------------------------------+
|                                  THE 6 HR INTERVIEW CATEGORIES                                |
+-----------------------------------+-----------------------------------------------------------+
| 1. Self-Introduction              | Formulate professional elevator pitch, communication tone,|
|                                   | personal brand, and initial articulation confidence.      |
+-----------------------------------+-----------------------------------------------------------+
| 2. Career Journey                 | Retrospective chronology, pivotal decisions, milestones, |
|                                   | career transitions, and continuous learning curve.        |
+-----------------------------------+-----------------------------------------------------------+
| 3. Strengths & Weaknesses         | Self-awareness, real-world application of strengths, and  |
|                                   | concrete remediation strategies for acknowledged flaws.   |
+-----------------------------------+-----------------------------------------------------------+
| 4. Teamwork & Culture Fit         | Collaboration dynamics, interpersonal conflict resolution,|
|                                   | cross-functional alignment, and peer empathy.             |
+-----------------------------------+-----------------------------------------------------------+
| 5. Career Goals                   | Alignment between personal trajectory and company goals,  |
|                                   | long-term vision, ambition, and retention likelihood.     |
+-----------------------------------+-----------------------------------------------------------+
| 6. Availability & Commitment      | Notice periods, onboarding timelines, shift readiness,    |
|                                   | relocation flexibility, and long-term organizational stay.|
+-----------------------------------+-----------------------------------------------------------+
```

### 2.2 The $2 \times 2$ Role-Based Differentiation Matrix

Candidate expectations vary significantly depending on years of experience and functional track. The engine segments candidates into four discrete quadrants:

```
                             ROLE TRACK
                  TECHNICAL                  NON-TECHNICAL
         +--------------------------+--------------------------+
         | Quadrant 1:              | Quadrant 2:              |
         | FRESHER - TECHNICAL      | FRESHER - NON-TECHNICAL  |
         | Focus: Project execution,| Focus: Interpersonal,    |
FRESHER  | coding fundamentals,     | client handling, campus  |
(<2 yrs) | academic teamwork, and   | initiatives, learning    |
         | technical curiosity.     | speed, and adaptability. |
         +--------------------------+--------------------------+
         | Quadrant 3:              | Quadrant 4:              |
         | EXPERIENCED - TECHNICAL  | EXPERIENCED - NON-TECH   |
EXPERI-  | Focus: High-level system | Focus: Cross-functional  |
ENCED    | architecture, mentoring, | negotiation, revenue     |
(>=2 yrs)| trade-offs, and technical| strategy, leadership, and|
         | debt management.         | team conflict dynamics.  |
         +--------------------------+--------------------------+
```

### 2.3 Curated Question Catalog & Metadata Schema

Each question in `HRQuestionBank` is modeled with rich metadata:
- **`question_id`**: Unique alphanumeric vector key (e.g., `HR-INTRO-F-TECH-01`).
- **`category`**: One of the 6 `HRCategory` dimensions.
- **`experience_tier`**: `FRESHER` or `EXPERIENCED`.
- **`role_track`**: `TECHNICAL` or `NON_TECHNICAL`.
- **`phase`**: Associated conversation phase (`INTRODUCTION`, `CORE_HR`, `ROLE_BASED_EVALUATION`, `CLOSING`).
- **`prompt`**: Natural language question delivered by the AI interviewer.
- **`follow_up_prompt`**: Adaptive probe invoked if the candidate's initial answer is brief or ambiguous.
- **`evaluation_criteria`**: Key competencies and indicators scored by the evaluation layer.

#### Catalog Matrix Overview (24 Core Questions)

| Quadrant | Category | Question ID | Target Competency / Prompt Summary |
| :--- | :--- | :--- | :--- |
| **Fresher - Tech** | Self-Introduction | `HR-INTRO-F-TECH-01` | Academic background, core technologies, and engineering passion |
| | Career Journey | `HR-JOURNEY-F-TECH-01` | Milestone university/internship projects and overcoming technical roadblocks |
| | Strengths & Weaknesses | `HR-STRENGTH-F-TECH-01` | Core algorithmic strength vs. debugging/time estimation growth area |
| | Teamwork & Culture | `HR-TEAM-F-TECH-01` | Hackathon/capstone collaboration, code reviews, and Git conflicts |
| | Career Goals | `HR-GOALS-F-TECH-01` | 3-year technical trajectory (e.g., Senior Engineer / Full-Stack specialist) |
| | Availability & Commitment| `HR-AVAIL-F-TECH-01` | Graduation status, immediate joining timeline, and relocation willingness |
| **Fresher - NonTech**| Self-Introduction | `HR-INTRO-F-NONTECH-01` | Professional presentation, domain interests, and business communication |
| | Career Journey | `HR-JOURNEY-F-NONTECH-01` | Extracurricular leadership, internships, and dynamic problem solving |
| | Strengths & Weaknesses | `HR-STRENGTH-F-NONTECH-01` | Communication/empathy strength vs. public speaking/delegation growth |
| | Teamwork & Culture | `HR-TEAM-F-NONTECH-01` | Diverse team project, mediating peer disagreements, and active listening |
| | Career Goals | `HR-GOALS-F-NONTECH-01` | 3-year career milestone in marketing/operations/sales excellence |
| | Availability & Commitment| `HR-AVAIL-F-NONTECH-01` | Notice/joining availability, training program commitment, and flexibility |
| **Experienced - Tech**| Self-Introduction | `HR-INTRO-E-TECH-01` | Career journey overview, architectural stack, and systems scaled |
| | Career Journey | `HR-JOURNEY-E-TECH-01` | Evolution from junior coder to senior engineer/architect, key migrations |
| | Strengths & Weaknesses | `HR-STRENGTH-E-TECH-01` | System design mastery vs. perfectionism/over-engineering mitigation |
| | Teamwork & Culture | `HR-TEAM-E-TECH-01` | Cross-functional alignment (Product vs Eng), mentoring junior developers |
| | Career Goals | `HR-GOALS-E-TECH-01` | 3-to-5 year technical roadmap (Staff/Principal Engineer or Tech Lead) |
| | Availability & Commitment| `HR-AVAIL-E-TECH-01` | Current notice period (e.g., 30/60/90 days), buyout option, stability |
| **Experienced - NonTech**| Self-Introduction | `HR-INTRO-E-NONTECH-01`| Executive summary, commercial impact delivered, and leadership philosophy |
| | Career Journey | `HR-JOURNEY-E-NONTECH-01`| Major organizational transformations, turnaround initiatives, and revenue KPIs |
| | Strengths & Weaknesses | `HR-STRENGTH-E-NONTECH-01`| Stakeholder diplomacy vs. over-commitment/delegation control |
| | Teamwork & Culture | `HR-TEAM-E-NONTECH-01` | Managing toxic team dynamics, cross-departmental friction, and culture building |
| | Career Goals | `HR-GOALS-E-NONTECH-01` | Strategic leadership aspirations (Director / VP / Business Unit Head) |
| | Availability & Commitment| `HR-AVAIL-E-NONTECH-01` | Notice period, handover commitments, client non-compete clauses |

---

## Deliverable 3: Interview Flow Design Document

### 3.1 Finite State Machine (FSM) Phase Transitions

The interview progresses through 4 distinct conversational phases:

```
  [START SESSION]
         |
         v
+------------------------------------------------------------------------------------+
| PHASE 1: INTRODUCTION                                                              |
| Purpose: Build rapport, establish communication baseline, verify identity & tone.  |
| Trigger: Session initialization -> Dispatches Category 1 (Self-Introduction)      |
+-----------------------------------------+------------------------------------------+
                                          |
                        Candidate response logged & validated
                                          |
                                          v
+------------------------------------------------------------------------------------+
| PHASE 2: CORE HR QUESTIONS                                                         |
| Purpose: Evaluate behavioral honesty, self-awareness, teamwork, and resilience.   |
| Sequence: Category 3 (Strengths & Weaknesses) -> Category 4 (Teamwork & Culture)   |
+-----------------------------------------+------------------------------------------+
                                          |
                        Behavioral themes analyzed & logged
                                          |
                                          v
+------------------------------------------------------------------------------------+
| PHASE 3: ROLE-BASED EVALUATION                                                     |
| Purpose: Assess domain maturity, career trajectory, and practical availability.   |
| Sequence: Category 2 (Career Journey) -> Category 5 (Goals) -> Category 6 (Avail)  |
+-----------------------------------------+------------------------------------------+
                                          |
                        Commitment & timelines recorded
                                          |
                                          v
+------------------------------------------------------------------------------------+
| PHASE 4: CLOSING                                                                   |
| Purpose: Professional wrap-up, candidate Q&A window, next steps notice, audit.     |
| Output: Session finalized -> Generates structured ATS Dossier Report               |
+-----------------------------------------+------------------------------------------+
                                          |
                                          v
                                   [END OF SESSION]
```

### 3.2 State Structure & Telemetry Contract

Every candidate utterance and AI interaction is encapsulated inside an `InterviewTurnState` model:

```python
class InterviewTurnState(BaseModel):
    turn_index: int                       # 1-indexed conversational turn counter
    phase: InterviewPhase                 # Current FSM phase (INTRO, CORE_HR, ROLE_EVAL, CLOSING)
    category: HRCategory                  # Active HR competency being assessed
    question_id: str                      # Alphanumeric template vector identifier
    ai_prompt: str                        # Natural language utterance generated by AI
    candidate_response: Optional[str]     # Cleaned speech-to-text transcript
    prompt_timestamp: str                 # UTC ISO8601 timestamp of prompt delivery
    response_timestamp: Optional[str]     # UTC ISO8601 timestamp of response ingestion
    response_time_seconds: float          # Latency / thinking time before speech
    word_count: int                       # Total spoken word count
    follow_up_eligible: bool              # Decision flag computed by eligibility engine
    follow_up_triggered: bool             # Whether an adaptive probe was dispatched
    follow_up_reason: FollowUpTriggerReason # Reason (TERSE, CONFLICT_AVOIDANCE, VAGUE, etc.)
    extracted_themes: List[str]           # Extracted behavioral tags (e.g., "Ownership", "Leadership")
    phase_completed: bool                 # True when turn satisfies requirements to advance
```

### 3.3 Follow-up Eligibility Decision Tree (Adaptive Probing)

Rather than asking static follow-ups, the AI assesses candidate responses in real-time to determine if an exploratory probe is warranted:

```
[Candidate Response Ingested]
             |
             v
   Is Word Count < 15 Words?
             |
             +----[YES]----> Flag: TERSE_RESPONSE
             |               Action: Dispatch targeted elaboration probe
             |
             +----[NO]-----> Contains Conflict Avoidance Patterns?
                             ("never had conflict", "always agreed", "nobody disagreed")
                                     |
                                     +----[YES]----> Flag: CONFLICT_AVOIDANCE
                                     |               Action: Probe for constructive disagreement
                                     |
                                     +----[NO]-----> In Category 4 (Teamwork) and lacks "I" / role specifics?
                                                     ("we just finished it", "team did everything")
                                                             |
                                                             +----[YES]----> Flag: VAGUE_CONTRIBUTION
                                                             |               Action: Probe for personal accountability
                                                             |
                                                             +----[NO]-----> Cliché / Platitude Detected?
                                                                             ("i am a perfectionist", "work too hard")
                                                                                     |
                                                                                     +----[YES]----> Flag: CLICHE_PLATITUDE
                                                                                     |               Action: Probe for authentic weakness
                                                                                     |
                                                                                     +----[NO]-----> Flag: NONE
                                                                                                     Action: Advance to next question
```

### 3.4 ATS Session Dossier & Telemetry Export

Upon reaching the `CLOSING` phase, the engine exports a standardized audit dossier:
- **`session_id`**: Universally unique session identifier.
- **`candidate_id` / `candidate_name` / `job_role`**: Metadata identifying candidate.
- **`experience_tier` / `role_track`**: Evaluated matrix quadrant.
- **`current_phase`**: `CLOSING` (or `COMPLETED`).
- **`total_turns_conducted`**: Count of all questions and follow-ups.
- **`follow_ups_triggered`**: Count of adaptive probing interruptions.
- **`average_response_words`**: Metric of candidate articulation depth.
- **`categories_assessed`**: Verification that all 6 categories were evaluated.
- **`identified_themes`**: Aggregate behavioral competency tags (`Leadership`, `Ownership`, `Collaboration`, etc.).
- **`turn_details`**: Full chronological audit trail with prompts, answers, latencies, and triggers.

---

## Deliverable Verification & Test Coverage

The engine is validated against a 7-point comprehensive automated test suite (`tests/test_hr_interview_engine.py`):

1. **`test_01_hr_categories_enum`**: Confirms that all 6 HR categories mandated by the curriculum are defined without regression.
2. **`test_02_question_bank_matrix_coverage`**: Asserts 100% matrix completeness (24 curated questions across 4 quadrants).
3. **`test_03_role_based_question_generator_quadrants`**: Verifies that Fresher-Tech, Fresher-NonTech, Experienced-Tech, and Experienced-NonTech generate properly customized question plans.
4. **`test_04_interview_state_and_response_capture`**: Confirms real-time state capture (Question ID, response text, word count, timestamps, response latency, and theme tagging).
5. **`test_05_follow_up_eligibility_triggers`**: Validates the adaptive probing heuristics for terse answers ($<15$ words), conflict avoidance, and rich answers.
6. **`test_06_conflict_avoidance_follow_up`**: Specifically tests candidates who claim "never had any conflict" and verifies that a constructive conflict resolution probe is immediately injected.
7. **`test_07_full_interview_phase_progression_and_dossier`**: Simulates an end-to-end interview running through all 4 phases (`INTRODUCTION` $\rightarrow$ `CORE_HR` $\rightarrow$ `ROLE_BASED_EVALUATION` $\rightarrow$ `CLOSING`), verifying that an ATS session dossier is exported with 100% category coverage.

**Automated Test Execution Result:**
```
Ran 7 tests in 0.003s
OK (100% Pass)
```

---

## Conclusion

The Zecpath-AI HR Interview Engine (`interview_ai/`) provides a robust, scalable, and adaptable conversational framework. By combining structured taxonomy, role-based matrix differentiation, and heuristic follow-up probing, it transforms static behavioral interviews into dynamic, data-driven assessments ready for real-time ATS integration and voice AI pipelines.
