"""
Zecpath-AI: Technical Interview Question Hierarchy Model & Progression Engine
=============================================================================
Defines the hierarchical question taxonomy, role-to-domain skill mappings,
experience-based tier logic, dynamic difficulty adaptation (DDA), and
Bloom's cognitive taxonomy progression.

Curriculum Reference: Day 46 - Technical Interview System Design
Deliverable 2: Question Hierarchy Model
"""

from typing import List, Dict, Optional, Any, Tuple, Set
from pydantic import BaseModel, Field
import math

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    TechnicalEvaluationRubric,
)


# ==============================================================================
# 1. QUESTION TAXONOMY DATA STRUCTURES
# ==============================================================================

class QuestionNode(BaseModel):
    """Atomic unit in the technical question hierarchy tree."""
    question_id: str
    target_role: JobRole
    skill_domain: str
    sub_skill: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    experience_tier: ExperienceTier
    blooms_level: BloomsTaxonomyLevel
    prompt_text: str
    key_evaluation_points: List[str]
    scaffolding_hints: List[str] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
    sample_ideal_answer_outline: str = ""


class SkillDomainDefinition(BaseModel):
    """Specification of a core competency domain within a job role."""
    domain_id: str
    domain_name: str
    description: str
    sub_skills: List[str]
    weight: float = Field(default=1.0, ge=0.1, le=5.0)


# ==============================================================================
# 2. ROLE-TO-SKILL DOMAIN MATRIX
# ==============================================================================

ROLE_SKILL_DOMAINS: Dict[JobRole, List[SkillDomainDefinition]] = {
    JobRole.MERN_STACK: [
        SkillDomainDefinition(
            domain_id="MERN_FE",
            domain_name="React Frontend Architecture",
            description="Component lifecycles, hooks, reconciliation (Fiber), state management, performance optimization",
            sub_skills=["React Hooks & State", "Virtual DOM & Reconciliation", "Context / Redux / Zustand", "SSR & Next.js", "Frontend Performance Tuning"],
            weight=1.2,
        ),
        SkillDomainDefinition(
            domain_id="MERN_BE",
            domain_name="Node.js & Express Runtime",
            description="Event loop phases, libuv, asynchronous non-blocking I/O, middleware pipelines, streams, clustering",
            sub_skills=["Event Loop & Asynchronous I/O", "Express Middleware & Architecture", "Node.js Streams & Buffers", "Error Handling & Logging", "Worker Threads & Clustering"],
            weight=1.2,
        ),
        SkillDomainDefinition(
            domain_id="MERN_DB",
            domain_name="MongoDB & Document Storage",
            description="Document modeling, indexing strategies, aggregation framework, transaction semantics, replica sets",
            sub_skills=["Schema Design & Normalization Trade-offs", "Aggregation Pipelines", "Indexing & Query Explain Plans", "Transactions & Concurrency", "Sharding & High Availability"],
            weight=1.0,
        ),
        SkillDomainDefinition(
            domain_id="MERN_API",
            domain_name="Fullstack Integration & Security",
            description="RESTful API contracts, WebSocket communication, JWT/OAuth authentication, CORS, CSRF, XSS defense",
            sub_skills=["RESTful API Design", "WebSocket & Real-time Feeds", "Authentication & JWT Security", "CORS & Browser Security", "End-to-End Testing"],
            weight=1.0,
        ),
    ],
    JobRole.JAVA_BACKEND: [
        SkillDomainDefinition(
            domain_id="JAVA_CORE",
            domain_name="Core Java & JVM Internals",
            description="Java Memory Model (JMM), Garbage Collection algorithms (G1, ZGC), class loading, multithreading, concurrency locks",
            sub_skills=["JVM Memory Model & Heap Layout", "Garbage Collection Strategies", "Concurrency & java.util.concurrent", "Generics & Reflection", "Bytecode & JIT Compilation"],
            weight=1.3,
        ),
        SkillDomainDefinition(
            domain_id="JAVA_SPRING",
            domain_name="Spring Framework & Ecosystem",
            description="Inversion of Control (IoC), Dependency Injection, Spring Boot auto-configuration, AOP, Spring Security, WebFlux",
            sub_skills=["Spring IoC & Bean Lifecycle", "Spring Boot Internals", "Aspect-Oriented Programming (AOP)", "Spring Data JPA & Hibernate Caching", "Reactive Programming with WebFlux"],
            weight=1.2,
        ),
        SkillDomainDefinition(
            domain_id="JAVA_DATA",
            domain_name="Relational DB & Transaction Management",
            description="SQL indexing, query execution plans, ACID properties, isolation levels, N+1 problem, optimistic vs pessimistic locking",
            sub_skills=["Transaction Isolation Levels", "Hibernate N+1 Query Optimization", "Connection Pooling (HikariCP)", "Database Sharding & Read Replicas", "Flyway / Liquibase Migrations"],
            weight=1.1,
        ),
        SkillDomainDefinition(
            domain_id="JAVA_DIST",
            domain_name="Microservices, Messaging & Distributed Systems",
            description="Apache Kafka event streaming, consumer groups, message delivery guarantees, Resilience4j circuit breakers, gRPC",
            sub_skills=["Kafka Architecture & Partitions", "Consumer Groups & Offsets", "Circuit Breakers & Resilience4j", "Distributed Tracing (OpenTelemetry)", "REST vs gRPC Microservices"],
            weight=1.2,
        ),
    ],
    JobRole.DEVOPS_CLOUD: [
        SkillDomainDefinition(
            domain_id="DEVOPS_CONTAINERS",
            domain_name="Containerization & Orchestration",
            description="Docker image layering, multi-stage builds, Linux namespaces/cgroups, Kubernetes architecture, Pod lifecycle, CNI",
            sub_skills=["Docker Multi-stage Builds", "Kubernetes Pod Lifecycle & Scheduling", "Kubernetes Services & Ingress Controllers", "ConfigMaps, Secrets & RBAC", "Helm Charts & Package Management"],
            weight=1.3,
        ),
        SkillDomainDefinition(
            domain_id="DEVOPS_IAC",
            domain_name="Infrastructure as Code & Cloud",
            description="Terraform state management, module design, drift detection, AWS/GCP VPC topology, IAM policies, security groups",
            sub_skills=["Terraform State & Locking", "Terraform Module Architecture", "Cloud VPC & Subnet Networking", "IAM Least Privilege Governance", "Disaster Recovery & Multi-region Failover"],
            weight=1.2,
        ),
        SkillDomainDefinition(
            domain_id="DEVOPS_CICD",
            domain_name="CI/CD Pipelines & Deployment Strategies",
            description="Automated build pipelines, blue-green deployments, canary rollouts, GitOps with ArgoCD, security scanning (SAST/DAST)",
            sub_skills=["GitLab CI / GitHub Actions Pipelines", "Blue-Green & Canary Deployments", "GitOps & ArgoCD", "Container Image Scanning (Trivy)", "Artifact Repositories & Semantic Versioning"],
            weight=1.1,
        ),
        SkillDomainDefinition(
            domain_id="DEVOPS_OBS",
            domain_name="Observability, Reliability & Monitoring",
            description="Prometheus time-series metrics, PromQL, Grafana alerting, ELK/Loki log aggregation, SLO/SLA tracking, incident triage",
            sub_skills=["Prometheus Metrics & Exporters", "PromQL & Alert Rules", "Grafana Dashboards", "Distributed Log Aggregation", "Site Reliability Engineering (SLO/SLI)"],
            weight=1.1,
        ),
    ],
    JobRole.PYTHON_DATA_ENG: [
        SkillDomainDefinition(
            domain_id="PY_CORE",
            domain_name="Python Runtime & Architecture",
            description="GIL mechanics, memory management, garbage collection, generators, decorators, async/await with asyncio, typing",
            sub_skills=["Global Interpreter Lock (GIL)", "Generators & Memory Efficiency", "Decorators & Metaclasses", "Asyncio & Event Loops", "Type Hints & Pydantic Validation"],
            weight=1.2,
        ),
        SkillDomainDefinition(
            domain_id="PY_FRAMEWORKS",
            domain_name="Backend APIs & Services",
            description="FastAPI ASGI architecture, Pydantic serialization, Django ORM, background tasks, Celery / Redis integration",
            sub_skills=["FastAPI & ASGI Event Handling", "Dependency Injection in FastAPI", "Celery Distributed Task Queues", "REST & OpenAPI Specs", "API Authentication & Rate Limiting"],
            weight=1.1,
        ),
        SkillDomainDefinition(
            domain_id="PY_DISTRIBUTED",
            domain_name="Distributed Data Processing & Spark",
            description="Apache Spark architecture, RDD vs DataFrame, Catalyst optimizer, Tungsten execution engine, partitioning, skew handling",
            sub_skills=["PySpark DataFrame Operations", "Spark Catalyst Optimizer & Physical Plans", "Partitioning & Data Skew Remediation", "Shuffle Mechanics & Memory Spill", "PySpark Streaming"],
            weight=1.3,
        ),
        SkillDomainDefinition(
            domain_id="PY_PIPELINES",
            domain_name="Data Pipelines, Storage & Lakehouses",
            description="Apache Airflow DAG design, backfilling, idempotent pipelines, Parquet/Delta Lake columnar storage, lakehouse architecture",
            sub_skills=["Airflow DAG Architecture & Sensors", "Idempotent Data Pipelines", "Parquet & Delta Lake Storage", "Data Quality & Great Expectations", "Schema Evolution & Governance"],
            weight=1.2,
        ),
    ],
}


# ==============================================================================
# 3. COMPREHENSIVE CURATED QUESTION BANK
# ==============================================================================

CURATED_QUESTION_BANK: List[QuestionNode] = [
    # --------------------------------------------------------------------------
    # MERN STACK QUESTIONS
    # --------------------------------------------------------------------------
    QuestionNode(
        question_id="Q-MERN-INT-01",
        target_role=JobRole.MERN_STACK,
        skill_domain="Introduction & Project Context",
        sub_skill="Technical Self-Introduction",
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.L1_BASIC,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Welcome to the technical evaluation. Could you walk me through your technical background in the MERN stack, highlighting the fullstack project you are most proud of building and the core architectural choices you made?",
        key_evaluation_points=["Clarity of tech stack description", "Identification of React frontend and Node backend role", "Awareness of data flow"],
        scaffolding_hints=["Focus on how data flowed between your React components, Node.js API, and MongoDB database."],
        suggested_followups=["What was the hardest bug you encountered in that project and how did you diagnose it?"],
    ),
    QuestionNode(
        question_id="Q-MERN-EXP-01",
        target_role=JobRole.MERN_STACK,
        skill_domain="React Frontend Architecture",
        sub_skill="React Hooks & State",
        category=QuestionCategory.EXPERIENCE_BASED,
        difficulty=DifficultyLevel.L2_FOUNDATIONAL,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.APPLY,
        prompt_text="In your past projects, how did you manage state in React? Specifically, describe a scenario where you chose between using standard useState/useReducer versus an external state manager like Redux or Zustand.",
        key_evaluation_points=["Understanding of component re-renders", "Prop drilling considerations", "State locality vs global state"],
        scaffolding_hints=["Think about how many components needed access to that piece of state and how frequently it changed."],
        suggested_followups=["How did you prevent unnecessary re-renders when passing callbacks down deep component trees?"],
    ),
    QuestionNode(
        question_id="Q-MERN-CONC-01",
        target_role=JobRole.MERN_STACK,
        skill_domain="Node.js & Express Runtime",
        sub_skill="Event Loop & Asynchronous I/O",
        category=QuestionCategory.CONCEPTUAL,
        difficulty=DifficultyLevel.L2_FOUNDATIONAL,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Explain the Node.js event loop. What happens behind the scenes when a network request arrives while Node.js is executing a synchronous CPU-bound task?",
        key_evaluation_points=["Single-threaded JavaScript execution context", "Event loop phases (timers, poll, check)", "libuv thread pool offloading", "Non-blocking I/O vs CPU blocking"],
        scaffolding_hints=["Recall that Node has a call stack and uses libuv for asynchronous event notifications."],
        suggested_followups=["How does process.nextTick differ from setImmediate in the event loop execution order?"],
    ),
    QuestionNode(
        question_id="Q-MERN-SCEN-01",
        target_role=JobRole.MERN_STACK,
        skill_domain="MongoDB & Document Storage",
        sub_skill="Indexing & Query Explain Plans",
        category=QuestionCategory.SCENARIO_BASED,
        difficulty=DifficultyLevel.L3_INTERMEDIATE,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.ANALYZE,
        prompt_text="Production scenario: An endpoint executing a MongoDB query against an orders collection with 10 million documents is spiking API response times to 4.5 seconds under peak load. How would you analyze the query performance, inspect the explain plan, and design the optimal indexing strategy?",
        key_evaluation_points=["Use of explain('executionStats')", "Inspection of totalDocsExamined vs nReturned", "COLLSCAN vs IXSCAN", "Compound index ESR (Equality, Sort, Range) rule", "Memory constraints and index sizing in RAM"],
        scaffolding_hints=["Check whether MongoDB is doing a full collection scan (COLLSCAN) and verify your compound index field ordering."],
        suggested_followups=["What are the write latency trade-offs of adding multiple compound indexes to a high-throughput write collection?"],
    ),
    QuestionNode(
        question_id="Q-MERN-SD-01",
        target_role=JobRole.MERN_STACK,
        skill_domain="Fullstack Integration & Security",
        sub_skill="WebSocket & Real-time Feeds",
        category=QuestionCategory.SYSTEM_DESIGN,
        difficulty=DifficultyLevel.L5_SYSTEM_DESIGN,
        experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
        blooms_level=BloomsTaxonomyLevel.CREATE,
        prompt_text="System Design: Design a real-time collaborative document editing platform (similar to Google Docs or Figma) using the MERN stack for 100,000 concurrent active users. How do you handle conflict resolution (Operational Transformation or CRDTs), WebSocket horizontal scaling across a cluster of Node.js instances, and persistent delta storage in MongoDB?",
        key_evaluation_points=["Conflict-free Replicated Data Types (CRDTs) vs Operational Transformation (OT)", "WebSocket sticky sessions or Redis Pub/Sub adapter", "Node.js cluster / Kubernetes ingress horizontal scale", "MongoDB write batching and document versioning", "Client-side optimistic rendering and delta compression"],
        scaffolding_hints=["Consider using a Redis Pub/Sub message broker to sync WebSocket messages between stateless Node.js server pods."],
        suggested_followups=["How do you guarantee message ordering and handle client network reconnects without losing in-flight character deltas?"],
    ),

    # --------------------------------------------------------------------------
    # JAVA BACKEND QUESTIONS
    # --------------------------------------------------------------------------
    QuestionNode(
        question_id="Q-JAVA-INT-01",
        target_role=JobRole.JAVA_BACKEND,
        skill_domain="Introduction & Project Context",
        sub_skill="Technical Overview",
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.L1_BASIC,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Welcome. Please introduce your backend engineering journey with Java and the Spring ecosystem. What is the most complex microservice or distributed feature you have engineered to date?",
        key_evaluation_points=["Articulation of Java & Spring tech stack", "Understanding of enterprise backend architecture", "Context of past responsibilities"],
        scaffolding_hints=["Highlight the architectural layers: controller, service, repository, and any message brokers used."],
        suggested_followups=["Why did your team select Spring Boot over alternative frameworks like Quarkus or Micronaut?"],
    ),
    QuestionNode(
        question_id="Q-JAVA-CONC-01",
        target_role=JobRole.JAVA_BACKEND,
        skill_domain="Core Java & JVM Internals",
        sub_skill="JVM Memory Model & Heap Layout",
        category=QuestionCategory.CONCEPTUAL,
        difficulty=DifficultyLevel.L2_FOUNDATIONAL,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Explain the internal layout of JVM memory (Heap, Metaspace, Thread Stacks, PC Registers). How do objects migrate between Young Generation (Eden, Survivor spaces) and Old Generation during garbage collection?",
        key_evaluation_points=["Distinction between Heap and Stack allocations", "Young Gen vs Old Gen structure", "Minor GC vs Major/Full GC", "Object tenure threshold and age promotion"],
        scaffolding_hints=["Think about where local method primitives are stored versus instantiated objects, and how Eden space handles allocation."],
        suggested_followups=["What causes a java.lang.OutOfMemoryError: Metaspace versus an OutOfMemoryError: Java heap space?"],
    ),
    QuestionNode(
        question_id="Q-JAVA-EXP-01",
        target_role=JobRole.JAVA_BACKEND,
        skill_domain="Spring Framework & Ecosystem",
        sub_skill="Spring Data JPA & Hibernate Caching",
        category=QuestionCategory.EXPERIENCE_BASED,
        difficulty=DifficultyLevel.L3_INTERMEDIATE,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.APPLY,
        prompt_text="In your past experience with Spring Data JPA and Hibernate, have you encountered the N+1 select problem? Walk me through how you diagnosed it and the specific mechanisms (JOIN FETCH, EntityGraphs, or BatchSize) you applied to eliminate it.",
        key_evaluation_points=["Diagnosis through SQL log profiling or Hibernate statistics", "Difference between Lazy and Eager fetching", "Use of JPQL 'JOIN FETCH' and '@EntityGraph'", "Subselect and batch fetching strategies"],
        scaffolding_hints=["Recall that Lazy fetching an association in a loop causes 1 query for the parent plus N individual queries for each child."],
        suggested_followups=["Why can blindly converting relationships to FetchType.EAGER create even worse performance anti-patterns?"],
    ),
    QuestionNode(
        question_id="Q-JAVA-SCEN-01",
        target_role=JobRole.JAVA_BACKEND,
        skill_domain="Microservices, Messaging & Distributed Systems",
        sub_skill="Kafka Architecture & Partitions",
        category=QuestionCategory.SCENARIO_BASED,
        difficulty=DifficultyLevel.L4_ADVANCED,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.ANALYZE,
        prompt_text="Production scenario: In a high-volume financial payments service consuming from an Apache Kafka topic, consumer group rebalances are frequently triggering consumer lag spikes and message processing timeouts. How do you analyze consumer group heartbeats, max.poll.interval.ms, partition distribution, and ensure idempotent message processing?",
        key_evaluation_points=["Understanding of max.poll.interval.ms vs session.timeout.ms", "Thread starvation in long-running consumers", "Cooperative Sticky Assignor vs Eager rebalancing", "Idempotent consumer pattern (deduplication key / transactional outbox)", "Dead Letter Queues (DLQ) for poisoned messages"],
        scaffolding_hints=["Consider whether individual message processing is blocking the consumer polling thread past the max.poll.interval threshold."],
        suggested_followups=["How does an idempotent producer setting (enable.idempotence=true) protect against duplicates on network retries?"],
    ),
    QuestionNode(
        question_id="Q-JAVA-SD-01",
        target_role=JobRole.JAVA_BACKEND,
        skill_domain="Microservices, Messaging & Distributed Systems",
        sub_skill="Circuit Breakers & Resilience4j",
        category=QuestionCategory.SYSTEM_DESIGN,
        difficulty=DifficultyLevel.L5_SYSTEM_DESIGN,
        experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
        blooms_level=BloomsTaxonomyLevel.EVALUATE,
        prompt_text="System Design: Design an ultra-reliable, globally distributed banking transaction authorization engine processing 50,000 TPS with sub-25ms P99 latency. How do you architect database partitioning, distributed saga patterns across microservices, two-phase commits vs eventual consistency, and fault tolerance against multi-data-center network partitions?",
        key_evaluation_points=["Distributed Saga Pattern (Orchestration vs Choreography)", "CAP theorem trade-offs in financial ledgers", "Multi-datacenter replication & active-active conflict resolution", "Pessimistic concurrency vs distributed locks with Redis/Zookeeper", "Circuit breaking, bulkhead patterns, and graceful degradation"],
        scaffolding_hints=["In banking, strong consistency on ledger accounts is non-negotiable. Explore how sharded primary databases with read replicas manage high write TPS."],
        suggested_followups=["How would you handle a transient network split between data centers without producing double-spend anomalies?"],
    ),

    # --------------------------------------------------------------------------
    # DEVOPS / CLOUD QUESTIONS
    # --------------------------------------------------------------------------
    QuestionNode(
        question_id="Q-DEVOPS-INT-01",
        target_role=JobRole.DEVOPS_CLOUD,
        skill_domain="Introduction & Project Context",
        sub_skill="Cloud Infrastructure Overview",
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.L1_BASIC,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Welcome. Could you walk me through your cloud and DevOps experience, outlining the containerization, orchestration, and CI/CD tools you have deployed to production?",
        key_evaluation_points=["Breadth of infrastructure tooling", "Familiarity with cloud providers (AWS, GCP, Azure)", "CI/CD automation concepts"],
        scaffolding_hints=["Outline how code commits progress from git repositories through Docker images to Kubernetes clusters."],
        suggested_followups=["What infrastructure-as-code tools have you used to manage cloud environments?"],
    ),
    QuestionNode(
        question_id="Q-DEVOPS-CONC-01",
        target_role=JobRole.DEVOPS_CLOUD,
        skill_domain="Containerization & Orchestration",
        sub_skill="Docker Multi-stage Builds",
        category=QuestionCategory.CONCEPTUAL,
        difficulty=DifficultyLevel.L2_FOUNDATIONAL,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.APPLY,
        prompt_text="Explain the concept of Docker multi-stage builds. Why are they critical in production container environments, and how do they reduce attack surface and container image size compared to single-stage builds?",
        key_evaluation_points=["Separation of build-time dependencies from runtime artifacts", "Drastic reduction in final image MB/GB size", "Elimination of compilers, package managers, and secrets from production images", "Layer caching efficiency"],
        scaffolding_hints=["Think about how SDKs and build tools are needed to compile an artifact, but only the compiled binary is needed to run."],
        suggested_followups=["How do Docker layer caching rules dictate the ordering of COPY and RUN instructions in a Dockerfile?"],
    ),
    QuestionNode(
        question_id="Q-DEVOPS-EXP-01",
        target_role=JobRole.DEVOPS_CLOUD,
        skill_domain="Infrastructure as Code & Cloud",
        sub_skill="Terraform State & Locking",
        category=QuestionCategory.EXPERIENCE_BASED,
        difficulty=DifficultyLevel.L3_INTERMEDIATE,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.ANALYZE,
        prompt_text="In your production experience with Terraform, how have you structured remote state management, team concurrency locking, and prevented state drift when manual cloud console interventions occurred?",
        key_evaluation_points=["Remote backend configuration (AWS S3 + DynamoDB locking)", "Handling terraform.tfstate corruption and recovery", "Drift detection via 'terraform plan -refresh-only'", "Terraform import workflow for out-of-band changes", "Module decomposition to prevent monolithic state files"],
        scaffolding_hints=["Discuss how DynamoDB provides distributed locking while S3 provides encrypted versioned state storage."],
        suggested_followups=["What are the risks of using sensitive variables in Terraform state and how do you protect them?"],
    ),
    QuestionNode(
        question_id="Q-DEVOPS-SCEN-01",
        target_role=JobRole.DEVOPS_CLOUD,
        skill_domain="Containerization & Orchestration",
        sub_skill="Kubernetes Pod Lifecycle & Scheduling",
        category=QuestionCategory.SCENARIO_BASED,
        difficulty=DifficultyLevel.L4_ADVANCED,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.ANALYZE,
        prompt_text="Production incident: A critical microservice deployment in Kubernetes is entering a CrashLoopBackOff state following an automated canary rollout. Concurrently, node memory pressure is triggering OOMKills across existing pods. Walk me step-by-step through how you triage, isolate, and remediate this incident in real-time.",
        key_evaluation_points=["kubectl describe pod inspection (Exit code 137 vs 1)", "Reviewing previous container logs with kubectl logs --previous", "Resource requests vs limits analysis in pod spec", "Kubelet eviction threshold analysis and cgroups memory pressure", "Immediate rollback via kubectl rollout undo or ArgoCD sync", "Node drainage and cluster autoscaler verification"],
        scaffolding_hints=["Look at the pod exit code: Exit code 137 specifically indicates an OS SIGKILL sent by the kernel OOM-killer."],
        suggested_followups=["How do Kubernetes Quality of Service (QoS) classes (Guaranteed, Burstable, BestEffort) affect pod eviction priority during node memory exhaustion?"],
    ),
    QuestionNode(
        question_id="Q-DEVOPS-SD-01",
        target_role=JobRole.DEVOPS_CLOUD,
        skill_domain="Observability, Reliability & Monitoring",
        sub_skill="Site Reliability Engineering (SLO/SLI)",
        category=QuestionCategory.SYSTEM_DESIGN,
        difficulty=DifficultyLevel.L5_SYSTEM_DESIGN,
        experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
        blooms_level=BloomsTaxonomyLevel.CREATE,
        prompt_text="System Design: Design an enterprise-grade, multi-region Kubernetes platform supporting zero-downtime automated deployments across 500+ microservices. Your architecture must incorporate GitOps, service mesh (Istio/Linkerd), global traffic management, comprehensive observability (Prometheus/Thanos/OpenTelemetry), and an automated disaster recovery failover achieving RPO < 1 min and RTO < 5 min.",
        key_evaluation_points=["Global Server Load Balancing (Route53 / Cloudflare) with health checks", "Service mesh traffic shifting (canary, mTLS, circuit breaking)", "GitOps with ArgoCD ApplicationSets across multi-cluster", "Thanos / Cortex for multi-cluster long-term metric aggregation", "Cross-region database replication and state synchronization", "Chaos engineering and automated DR failover playbooks"],
        scaffolding_hints=["Consider using Thanos to federate Prometheus instances across different geographical regions into a unified query engine."],
        suggested_followups=["How do you prevent a cascading split-brain disaster if the primary interconnect between the two cloud regions is severed?"],
    ),

    # --------------------------------------------------------------------------
    # PYTHON / DATA ENGINEERING QUESTIONS
    # --------------------------------------------------------------------------
    QuestionNode(
        question_id="Q-PY-INT-01",
        target_role=JobRole.PYTHON_DATA_ENG,
        skill_domain="Introduction & Project Context",
        sub_skill="Python & Data Stack Overview",
        category=QuestionCategory.INTRODUCTION,
        difficulty=DifficultyLevel.L1_BASIC,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Welcome to the technical interview. Walk me through your Python backend and data engineering experience. What data pipelines or backend services have you built, and what data volumes were you processing?",
        key_evaluation_points=["Clarity of Python and data tooling background", "Identification of data volumes (MBs, GBs, TBs)", "Familiarity with processing architectures"],
        scaffolding_hints=["Mention the frameworks you used (e.g. FastAPI, Spark, Pandas) and where the data originated."],
        suggested_followups=["What challenges did you face when scaling Python beyond single-node memory limits?"],
    ),
    QuestionNode(
        question_id="Q-PY-CONC-01",
        target_role=JobRole.PYTHON_DATA_ENG,
        skill_domain="Python Runtime & Architecture",
        sub_skill="Global Interpreter Lock (GIL)",
        category=QuestionCategory.CONCEPTUAL,
        difficulty=DifficultyLevel.L2_FOUNDATIONAL,
        experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
        blooms_level=BloomsTaxonomyLevel.UNDERSTAND,
        prompt_text="Explain Python's Global Interpreter Lock (GIL). How does it affect multithreaded CPU-bound tasks versus I/O-bound tasks, and how do multiprocessing or async/await provide workarounds?",
        key_evaluation_points=["Definition of GIL as a mutex protecting CPython memory management", "CPU-bound tasks bottlenecking on a single core in threading", "I/O-bound tasks releasing the GIL during network/disk wait", "multiprocessing module creating independent memory spaces/processes", "asyncio providing single-threaded cooperative multitasking"],
        scaffolding_hints=["CPython reference counting requires thread-safe access to avoid race conditions on object refcounts."],
        suggested_followups=["How does Python 3.12+ sub-interpreters or free-threaded Python change the future of the GIL?"],
    ),
    QuestionNode(
        question_id="Q-PY-EXP-01",
        target_role=JobRole.PYTHON_DATA_ENG,
        skill_domain="Distributed Data Processing & Spark",
        sub_skill="Partitioning & Data Skew Remediation",
        category=QuestionCategory.EXPERIENCE_BASED,
        difficulty=DifficultyLevel.L3_INTERMEDIATE,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.APPLY,
        prompt_text="In your production data engineering experience with PySpark, have you diagnosed and resolved data skew where one or two tasks in a stage took 10x longer than the rest? Walk me through how you identified the skew key and the mitigation strategies (e.g., salting, broadcast joins, Adaptive Query Execution) you implemented.",
        key_evaluation_points=["Diagnosis via Spark Web UI task execution timeline", "Identification of uneven partition records / shuffle spill to disk", "Salting skew keys with random prefixes", "Broadcast Hash Joins for large-small table joins", "Spark 3.x Adaptive Query Execution (AQE) skew join optimization"],
        scaffolding_hints=["Look at the Spark UI: if 199 tasks finish in 5 seconds and 1 task runs for 15 minutes, you have a data skew bottleneck on the join key."],
        suggested_followups=["What are the memory threshold limits for broadcast joins before driver OutOfMemory errors occur?"],
    ),
    QuestionNode(
        question_id="Q-PY-SCEN-01",
        target_role=JobRole.PYTHON_DATA_ENG,
        skill_domain="Data Pipelines, Storage & Lakehouses",
        sub_skill="Idempotent Data Pipelines",
        category=QuestionCategory.SCENARIO_BASED,
        difficulty=DifficultyLevel.L4_ADVANCED,
        experience_tier=ExperienceTier.MID_3_5_YRS,
        blooms_level=BloomsTaxonomyLevel.ANALYZE,
        prompt_text="Production scenario: An Apache Airflow ETL pipeline running hourly batch jobs fails midway during an incremental backfill, leaving partially written files in Amazon S3 and duplicated records in your data warehouse tables. How do you design idempotent pipeline DAGs with atomic commits, write-audit-publish patterns, and Delta Lake ACID transactions?",
        key_evaluation_points=["Definition of pipeline idempotency (f(f(x)) = f(x))", "Avoidance of simple append operations without staging", "Write-Audit-Publish (WAP) pattern", "Delta Lake ACID transactions & MERGE INTO operations", "Airflow execution_date deterministic partition parameterization"],
        scaffolding_hints=["Use Delta Lake's transaction log (_delta_log) to ensure atomic directory replacement so partial writes never get exposed."],
        suggested_followups=["How do you handle schema drift (e.g., upstream team adds or changes a column type) without crashing downstream pipeline consumers?"],
    ),
    QuestionNode(
        question_id="Q-PY-SD-01",
        target_role=JobRole.PYTHON_DATA_ENG,
        skill_domain="Data Pipelines, Storage & Lakehouses",
        sub_skill="Parquet & Delta Lake Storage",
        category=QuestionCategory.SYSTEM_DESIGN,
        difficulty=DifficultyLevel.L5_SYSTEM_DESIGN,
        experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
        blooms_level=BloomsTaxonomyLevel.CREATE,
        prompt_text="System Design: Design an enterprise streaming and batch lakehouse platform processing 5 TB of incoming IoT telematics data per day. The system must support real-time fraud anomaly alerting with sub-second latency while simultaneously serving ad-hoc SQL analytical queries with sub-5-second query performance over 3 years of historical parquet data.",
        key_evaluation_points=["Lambda vs Kappa architecture selection", "Kafka ingestion tier with schema registry (Avro/Protobuf)", "Spark Structured Streaming or Flink for real-time anomaly detection", "Delta Lake / Iceberg storage tier with Z-Ordering and compaction", "Query federation engine (Trino / Presto) over partitioned lakehouse", "Data governance, compaction jobs, and cold storage tiering"],
        scaffolding_hints=["Consider a Kappa architecture using Kafka into Spark Structured Streaming writing directly to a Delta Lake with Change Data Feed."],
        suggested_followups=["How do you solve the small-file problem when streaming writes continuously flush 1MB micro-batches to cloud object storage?"],
    ),
]


# ==============================================================================
# 4. QUESTION PROGRESSION & SELECTION ENGINE
# ==============================================================================

class DynamicDifficultyProgressionEngine:
    """
    Mathematical engine implementing Dynamic Difficulty Adaptation (DDA)
    and Bloom's Cognitive Progression across interview turns.
    """

    EQUILIBRIUM_SCORE = 0.60
    STEP_SIZE = 0.50
    MIN_DIFFICULTY = 1.0
    MAX_DIFFICULTY = 5.0

    @classmethod
    def get_initial_difficulty(cls, tier: ExperienceTier) -> float:
        """
        Maps experience tier to starting baseline difficulty.
        0-2 yrs -> 1.0 (Level 1-2 basics)
        3-5 yrs -> 3.0 (Level 2-4 intermediate)
        5+ yrs  -> 4.0 (Level 3-5 advanced/system design)
        """
        if tier == ExperienceTier.JUNIOR_0_2_YRS:
            return 1.0
        elif tier == ExperienceTier.MID_3_5_YRS:
            return 3.0
        else:
            return 4.0

    @classmethod
    def calculate_next_difficulty(
        cls,
        current_difficulty: float,
        last_score: float,
        tier: ExperienceTier,
        depth_modifier: float = 0.0,
    ) -> Tuple[float, str]:
        """
        Calculates adjusted difficulty following an evaluated answer.

        Formula:
        delta = current + sensitivity * (score - equilibrium) + depth_modifier
        Clamped within tier-aware bounds:
          Junior: [1.0, 3.0]
          Mid:    [2.0, 4.5]
          Senior: [3.0, 5.0]
        """
        diff_change = (last_score - cls.EQUILIBRIUM_SCORE) * 1.0 + depth_modifier

        # Determine step direction
        if last_score >= 0.75:
            action = "STEP_UP"
            delta = cls.STEP_SIZE
        elif last_score >= 0.45:
            action = "MAINTAIN"
            delta = 0.0
        else:
            action = "STEP_DOWN"
            delta = -cls.STEP_SIZE

        new_difficulty = current_difficulty + delta

        # Tier-aware clamping bounds
        if tier == ExperienceTier.JUNIOR_0_2_YRS:
            floor, ceiling = 1.0, 3.0
        elif tier == ExperienceTier.MID_3_5_YRS:
            floor, ceiling = 2.0, 4.5
        else:
            floor, ceiling = 3.0, 5.0

        clamped = max(floor, min(ceiling, new_difficulty))
        # Round to 1 decimal place
        clamped = round(clamped, 1)

        rationale = f"{action} (Score: {last_score:.2f} vs Eq: {cls.EQUILIBRIUM_SCORE:.2f} -> Diff: {current_difficulty:.1f} to {clamped:.1f})"
        return clamped, rationale

    @classmethod
    def map_score_to_blooms(cls, aggregate_score: float, target_difficulty: float) -> BloomsTaxonomyLevel:
        """Determines demonstrated Bloom's cognitive depth from score and difficulty."""
        combined = (aggregate_score * 0.6) + ((target_difficulty / 5.0) * 0.4)
        if combined >= 0.85:
            return BloomsTaxonomyLevel.CREATE
        elif combined >= 0.72:
            return BloomsTaxonomyLevel.EVALUATE
        elif combined >= 0.58:
            return BloomsTaxonomyLevel.ANALYZE
        elif combined >= 0.42:
            return BloomsTaxonomyLevel.APPLY
        elif combined >= 0.25:
            return BloomsTaxonomyLevel.UNDERSTAND
        else:
            return BloomsTaxonomyLevel.REMEMBER


# ==============================================================================
# 5. QUESTION HIERARCHY REPOSITORY & QUERY INTERFACE
# ==============================================================================

class QuestionHierarchyRepository:
    """Provides querying, filtering, and hierarchical navigation of technical questions."""

    def __init__(self, question_bank: Optional[List[QuestionNode]] = None):
        self._bank = question_bank or CURATED_QUESTION_BANK

    def get_questions_for_role(self, role: JobRole) -> List[QuestionNode]:
        """Returns all questions configured for a specific technical role."""
        return [q for q in self._bank if q.target_role == role]

    def get_skill_domains_for_role(self, role: JobRole) -> List[SkillDomainDefinition]:
        """Returns standard skill domain definitions mapped to the role."""
        return ROLE_SKILL_DOMAINS.get(role, [])

    def select_best_question(
        self,
        role: JobRole,
        category: QuestionCategory,
        target_difficulty: float,
        experience_tier: ExperienceTier,
        used_question_ids: Set[str],
    ) -> Optional[QuestionNode]:
        """
        Hierarchical matching algorithm selecting the optimal question node:
        1. Exact role match
        2. Exact category match
        3. Excludes previously asked questions
        4. Minimizes |difficulty - target_difficulty|
        5. Prefers candidate's experience tier or adjacent tier
        """
        candidates = [
            q for q in self._bank
            if q.target_role == role
            and q.category == category
            and q.question_id not in used_question_ids
        ]

        if not candidates:
            # Fallback: Relax category if introduction or wrap-up
            candidates = [
                q for q in self._bank
                if q.target_role == role and q.question_id not in used_question_ids
            ]

        if not candidates:
            return None

        # Sort by distance to target difficulty, then tier match
        def rank_key(q: QuestionNode) -> float:
            diff_dist = abs(float(q.difficulty.value) - target_difficulty)
            tier_penalty = 0.0 if q.experience_tier == experience_tier else 0.5
            return diff_dist + tier_penalty

        candidates.sort(key=rank_key)
        return candidates[0]

    def total_questions_count(self) -> int:
        return len(self._bank)
