# Zecpath-AI: Question Hierarchy Model & Progression Engine
**Curriculum Milestone:** Day 46 – Technical Interview System Design  
**Deliverable 2:** Question Hierarchy Model  
**Specification Version:** 1.0.0-PROD-HIERARCHY  
**Document Classification:** Technical Algorithms & Taxonomy Specification  

---

## 1. Question Taxonomy Structure

The question taxonomy organizes technical evaluation items into a 6-level hierarchical tree:

```
Root: Job Role (e.g., DEVOPS_CLOUD)
  └── Skill Domain (e.g., Containerization & Orchestration)
        └── Sub-Skill / Core Competency (e.g., Kubernetes Pod Lifecycle & Scheduling)
              └── Experience Tier (e.g., Senior 5+ Years)
                    └── Question Category (e.g., SCENARIO_BASED)
                          └── Difficulty Level (e.g., L4_ADVANCED)
                                └── Question Node (Prompt, Rubric, Hints, Follow-ups)
```

Each atomic `QuestionNode` specifies:
- `question_id`: Globally unique identifier (e.g., `Q-DEVOPS-SCEN-01`).
- `prompt_text`: Role-calibrated technical question prompt.
- `key_evaluation_points`: Core theoretical concepts and mechanics expected in candidate responses.
- `scaffolding_hints`: Progressive algorithmic clues provided if the candidate experiences severe struggle.
- `suggested_followups`: Sub-turn probes targeting omitted trade-offs, scalability boundaries, or edge cases.
- `blooms_level`: Target Bloom's revised cognitive taxonomy level.

---

## 2. Experience-Based Tier Logic & Technical Scope

Candidates are automatically assigned to one of three discrete experience tiers based on verified professional experience:

### 2.1 Junior Tier (0–2 Years) -> Foundational Basics
- **Target Difficulty:** Level 1 – Level 2 ($\delta \in [1.0, 3.0]$).
- **Core Focus:** Syntax precision, standard data structures (arrays, hash maps, queues, trees), core OOP/FP principles, fundamental APIs, error handling, basic database queries.
- **Cognitive Depth:** Bloom's Taxonomy Levels 1–2 (Remember & Understand).
- **Scaffolding:** High hint allowance upon algorithmic syntax deadlocks.

### 2.2 Mid-Level Tier (3–5 Years) -> Intermediate Architecture
- **Target Difficulty:** Level 2 – Level 4 ($\delta \in [2.0, 4.5]$).
- **Core Focus:** Design patterns, database query optimization (indexing, query execution plans, N+1 query elimination), asynchronous concurrency, caching patterns, RESTful/GraphQL contract design, code modularity.
- **Cognitive Depth:** Bloom's Taxonomy Levels 3–4 (Apply & Analyze).
- **Scaffolding:** Moderate hint allowance; primary evaluation centers on architectural trade-off reasoning.

### 2.3 Senior / Architect Tier (5+ Years) -> Distributed System Design
- **Target Difficulty:** Level 3 – Level 5 ($\delta \in [3.0, 5.0]$).
- **Core Focus:** High-scale distributed systems, sharding, consensus protocols (Raft, Paxos), event-driven microservices (Kafka, Sagas), CAP theorem trade-offs, multi-region disaster recovery, SLA/SLO engineering.
- **Cognitive Depth:** Bloom's Taxonomy Levels 5–6 (Evaluate & Create).
- **Scaffolding:** Minimal hints; candidate must independently navigate ambiguous, production-scale failure scenarios.

---

## 3. Dynamic Difficulty Adaptation (DDA) Formulation

The system adjusts technical question difficulty after each turn using a deterministic adaptation formula:

$$\delta_{t+1} = \text{clamp}\left(\delta_t + \alpha \cdot (s_t - \tau) + \text{DepthModifier}, \delta_{\min}, \delta_{\max}\right)$$

Where:
- $\delta_t \in [1.0, 5.0]$ is the current question difficulty.
- $s_t \in [0.0, 1.0]$ is the candidate's evaluated turn score.
- $\tau = 0.60$ is the equilibrium threshold score.
- $\alpha = 1.0$ is the adaptation sensitivity multiplier.
- $\text{DepthModifier} \in [-0.1, 0.1]$ is a modifier reflecting technical granularity and trade-off depth.

### 3.1 Discrete Progression Rules

1. **Step-Up (Strong Answer, $s_t \ge 0.75$):**
   $$\delta_{t+1} = \min(\delta_t + 0.50, \delta_{\max})$$
   Advances to more rigorous concepts or higher-scale architecture problems.

2. **Maintain (Neutral / Satisfactory, $0.45 \le s_t < 0.75$):**
   $$\delta_{t+1} = \delta_t$$
   Maintains current difficulty level, selecting a lateral concept or orthogonal competency.

3. **Step-Down (Incomplete / Struggling, $s_t < 0.45$):**
   $$\delta_{t+1} = \max(\delta_t - 0.50, \delta_{\min})$$
   Provides scaffolding hints and stabilizes difficulty at the tier floor.

### 3.2 Tier Clamping Bounds Table

| Experience Tier | Baseline $\delta_0$ | Minimum Difficulty $\delta_{\min}$ | Maximum Difficulty $\delta_{\max}$ |
| :--- | :--- | :--- | :--- |
| **Junior (0–2 yrs)** | 1.0 | 1.0 | 3.0 |
| **Mid-Level (3–5 yrs)** | 3.0 | 2.0 | 4.5 |
| **Senior (5+ yrs)** | 4.0 | 3.0 | 5.0 |

---

## 4. Bloom's Cognitive Taxonomy Mapping

| Level | Cognitive Domain | Action Verbs | Evaluation Focus |
| :--- | :--- | :--- | :--- |
| **L1** | **Remember** | Recall, list, define, state | Core language syntax, standard library functions. |
| **L2** | **Understand** | Explain, describe, summarize | Event loop mechanics, JVM heap layout, multi-stage build benefits. |
| **L3** | **Apply** | Execute, solve, query, implement | Writing indexing plans, resolving Hibernate N+1 with EntityGraphs. |
| **L4** | **Analyze** | Triage, diagnose, deconstruct | Isolating K8s CrashLoopBackOff, thread starvation, OOMKill root cause. |
| **L5** | **Evaluate** | Defend, weigh, critique, compare | Defending active-active multi-region replication against CAP theorem. |
| **L6** | **Create** | Architect, synthesize, engineer | Designing 100k concurrent WebSocket platform or 5TB daily lakehouse. |
