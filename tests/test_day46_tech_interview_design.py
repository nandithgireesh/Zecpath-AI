"""
Unit Tests for Day 46: Technical Interview System Design
=========================================================
Validates the complete Deliverables for Day 46:
- Deliverable 1: Technical Interview AI Blueprint (specifications, SLA, hashing, schemas)
- Deliverable 2: Question Hierarchy Model (taxonomy, role domains, experience tiers, DDA math)
- Deliverable 3: Interview Flow Design & FSM (states, transitions, dynamic probing, scaffolding, evaluation)
"""

import unittest
import time

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    InterviewFlowState,
    SubTurnAction,
    RecommendationVerdict,
    CandidateProfile,
    TechnicalInterviewConfig,
    TechnicalEvaluationRubric,
    TechnicalInterviewAIBlueprint,
)
from tech_interview.question_hierarchy import (
    QuestionNode,
    SkillDomainDefinition,
    ROLE_SKILL_DOMAINS,
    CURATED_QUESTION_BANK,
    DynamicDifficultyProgressionEngine,
    QuestionHierarchyRepository,
)
from tech_interview.flow_engine import (
    LEGAL_STATE_TRANSITIONS,
    InterviewTurnRecord,
    StateTransitionEvent,
    TechnicalInterviewReport,
    TechnicalInterviewFlowEngine,
)


class TestDay46TechnicalInterviewDesign(unittest.TestCase):
    """Comprehensive test suite for Day 46 technical interview design modules."""

    # ==========================================================================
    # 1. BLUEPRINT & CANDIDATE PROFILE TESTS
    # ==========================================================================

    def test_01_candidate_profile_auto_tiering(self):
        """Verify automatic experience tier classification based on verified years."""
        p_junior = CandidateProfile(candidate_id="CAND-01", target_role=JobRole.MERN_STACK, years_experience=1.5)
        self.assertEqual(p_junior.experience_tier, ExperienceTier.JUNIOR_0_2_YRS)

        p_mid = CandidateProfile(candidate_id="CAND-02", target_role=JobRole.JAVA_BACKEND, years_experience=4.0)
        self.assertEqual(p_mid.experience_tier, ExperienceTier.MID_3_5_YRS)

        p_senior = CandidateProfile(candidate_id="CAND-03", target_role=JobRole.DEVOPS_CLOUD, years_experience=8.5)
        self.assertEqual(p_senior.experience_tier, ExperienceTier.SENIOR_5_PLUS_YRS)

    def test_02_blueprint_manifest_and_sha256(self):
        """Verify blueprint architectural manifest structure and deterministic hash."""
        manifest = TechnicalInterviewAIBlueprint.get_blueprint_manifest()
        self.assertEqual(manifest["version"], "1.0.0-PROD-BLUEPRINT")
        self.assertIn("Subsystem_1_IRPS", manifest["subsystems"])
        self.assertIn("Subsystem_2_AQO", manifest["subsystems"])
        self.assertIn("Subsystem_3_CTEE", manifest["subsystems"])
        self.assertIn("Subsystem_4_SMFC", manifest["subsystems"])
        self.assertIn("Subsystem_5_ISFG", manifest["subsystems"])

        sha_hash = TechnicalInterviewAIBlueprint.generate_blueprint_hash()
        self.assertEqual(len(sha_hash), 64)

    # ==========================================================================
    # 2. ROLE DOMAIN MAPPINGS & QUESTION HIERARCHY
    # ==========================================================================

    def test_03_role_to_skill_domain_mappings(self):
        """Verify all target roles have explicit, rich skill domain mappings."""
        for role in [JobRole.MERN_STACK, JobRole.JAVA_BACKEND, JobRole.DEVOPS_CLOUD, JobRole.PYTHON_DATA_ENG]:
            domains = ROLE_SKILL_DOMAINS.get(role)
            self.assertIsNotNone(domains)
            self.assertGreaterEqual(len(domains), 4)
            for d in domains:
                self.assertTrue(len(d.sub_skills) >= 4)
                self.assertGreater(d.weight, 0.0)

    def test_04_curated_question_bank_coverage(self):
        """Verify question bank covers all roles, categories, and difficulty levels."""
        repo = QuestionHierarchyRepository()
        self.assertGreaterEqual(repo.total_questions_count(), 20)

        for role in [JobRole.MERN_STACK, JobRole.JAVA_BACKEND, JobRole.DEVOPS_CLOUD, JobRole.PYTHON_DATA_ENG]:
            questions = repo.get_questions_for_role(role)
            self.assertGreaterEqual(len(questions), 4)

            # Check presence of key categories
            categories = {q.category for q in questions}
            self.assertIn(QuestionCategory.INTRODUCTION, categories)
            self.assertIn(QuestionCategory.CONCEPTUAL, categories)
            self.assertIn(QuestionCategory.SCENARIO_BASED, categories)

    # ==========================================================================
    # 3. DYNAMIC DIFFICULTY PROGRESSION (DDA) & BLOOM'S TAXONOMY
    # ==========================================================================

    def test_05_initial_difficulty_by_tier(self):
        """Verify starting difficulty baseline corresponds to candidate tier."""
        self.assertEqual(DynamicDifficultyProgressionEngine.get_initial_difficulty(ExperienceTier.JUNIOR_0_2_YRS), 1.0)
        self.assertEqual(DynamicDifficultyProgressionEngine.get_initial_difficulty(ExperienceTier.MID_3_5_YRS), 3.0)
        self.assertEqual(DynamicDifficultyProgressionEngine.get_initial_difficulty(ExperienceTier.SENIOR_5_PLUS_YRS), 4.0)

    def test_06_dda_step_up_maintain_step_down(self):
        """Verify difficulty steps up on high score, maintains on neutral, steps down on low score."""
        # Junior tier: range [1.0, 3.0]
        # Step up on score = 0.85
        next_diff, r_up = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=1.5, last_score=0.85, tier=ExperienceTier.JUNIOR_0_2_YRS
        )
        self.assertEqual(next_diff, 2.0)
        self.assertIn("STEP_UP", r_up)

        # Maintain on score = 0.60
        next_diff, r_hold = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=2.0, last_score=0.60, tier=ExperienceTier.JUNIOR_0_2_YRS
        )
        self.assertEqual(next_diff, 2.0)
        self.assertIn("MAINTAIN", r_hold)

        # Step down on score = 0.30
        next_diff, r_down = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=2.0, last_score=0.30, tier=ExperienceTier.JUNIOR_0_2_YRS
        )
        self.assertEqual(next_diff, 1.5)
        self.assertIn("STEP_DOWN", r_down)

    def test_07_dda_tier_aware_clamping_bounds(self):
        """Verify difficulty never breaches experience tier boundaries."""
        # Junior upper bound is 3.0
        clamped_high, _ = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=3.0, last_score=0.99, tier=ExperienceTier.JUNIOR_0_2_YRS
        )
        self.assertEqual(clamped_high, 3.0)

        # Senior lower bound is 3.0
        clamped_low, _ = DynamicDifficultyProgressionEngine.calculate_next_difficulty(
            current_difficulty=3.0, last_score=0.10, tier=ExperienceTier.SENIOR_5_PLUS_YRS
        )
        self.assertEqual(clamped_low, 3.0)

    def test_08_blooms_taxonomy_mapping(self):
        """Verify cognitive taxonomy classification based on score and difficulty."""
        bloom_high = DynamicDifficultyProgressionEngine.map_score_to_blooms(0.95, 5.0)
        self.assertEqual(bloom_high, BloomsTaxonomyLevel.CREATE)

        bloom_mid = DynamicDifficultyProgressionEngine.map_score_to_blooms(0.65, 3.0)
        self.assertEqual(bloom_mid, BloomsTaxonomyLevel.ANALYZE)

        bloom_low = DynamicDifficultyProgressionEngine.map_score_to_blooms(0.20, 1.0)
        self.assertEqual(bloom_low, BloomsTaxonomyLevel.REMEMBER)

    # ==========================================================================
    # 4. FINITE STATE MACHINE (FSM) & FLOW ENGINE
    # ==========================================================================

    def test_09_fsm_legal_transitions_and_rejections(self):
        """Verify state machine permits valid transitions and rejects invalid jumps."""
        p = CandidateProfile(candidate_id="CAND-TEST", target_role=JobRole.JAVA_BACKEND, years_experience=4.0)
        engine = TechnicalInterviewFlowEngine(p)

        self.assertEqual(engine.current_state, InterviewFlowState.INITIALIZED)

        # Legal: INITIALIZED -> INTRODUCTION
        self.assertTrue(engine.transition_to(InterviewFlowState.INTRODUCTION))
        self.assertEqual(engine.current_state, InterviewFlowState.INTRODUCTION)

        # Illegal: INTRODUCTION -> SYSTEM_DESIGN_DEEPDIVE directly
        self.assertFalse(engine.transition_to(InterviewFlowState.SYSTEM_DESIGN_DEEPDIVE))
        self.assertEqual(engine.current_state, InterviewFlowState.INTRODUCTION)

        # Legal: INTRODUCTION -> EXPERIENCE_PROBING
        self.assertTrue(engine.transition_to(InterviewFlowState.EXPERIENCE_PROBING))
        self.assertEqual(engine.current_state, InterviewFlowState.EXPERIENCE_PROBING)

    def test_10_dynamic_probing_and_scaffolding_hints(self):
        """Verify flow engine triggers scaffolding on low score and probing on partial answer."""
        p = CandidateProfile(candidate_id="CAND-TEST", target_role=JobRole.MERN_STACK, years_experience=2.0)
        engine = TechnicalInterviewFlowEngine(p)
        engine.transition_to(InterviewFlowState.INTRODUCTION)

        q = engine.prepare_next_question()
        self.assertIsNotNone(q)

        # Low answer triggers scaffolding hint
        weak_answer = "I don't know."
        action, reply, eval_res = engine.process_candidate_turn(weak_answer)
        self.assertIn(action, [SubTurnAction.PROVIDE_SCAFFOLDING_HINT, SubTurnAction.PROBE_DEEPER])
        self.assertLess(eval_res.aggregate_score, 0.40)

        # Strong answer advances question
        strong_answer = (
            "In my past MERN project, I engineered fullstack features where React frontend components "
            "communicated through RESTful endpoints and WebSockets with an Express and Node.js backend. "
            "MongoDB was used for flexible JSON document storage, where I designed indexed schemas to minimize "
            "query latency. I carefully evaluated state management trade-offs between useState and Redux, "
            "ensuring clear data flow and modular architecture."
        )
        action_strong, _, eval_strong = engine.process_candidate_turn(strong_answer)
        self.assertIn(action_strong, [SubTurnAction.ADVANCE_QUESTION, SubTurnAction.PROBE_DEEPER])
        self.assertGreaterEqual(eval_strong.aggregate_score, 0.65)

    # ==========================================================================
    # 5. END-TO-END INTERVIEW SIMULATION TESTS
    # ==========================================================================

    def test_11_junior_mern_end_to_end_simulation(self):
        """Simulate complete junior MERN interview from Introduction to Completion."""
        p = CandidateProfile(candidate_id="CAND-MERN-JR", target_role=JobRole.MERN_STACK, years_experience=1.5)
        config = TechnicalInterviewConfig(
            session_id="SESS-JR-MERN",
            target_role=JobRole.MERN_STACK,
            experience_tier=ExperienceTier.JUNIOR_0_2_YRS,
            min_questions_per_phase={
                QuestionCategory.INTRODUCTION: 1,
                QuestionCategory.EXPERIENCE_BASED: 1,
                QuestionCategory.CONCEPTUAL: 1,
                QuestionCategory.SCENARIO_BASED: 1,
                QuestionCategory.SYSTEM_DESIGN: 0,
            },
            max_probing_depth=1,
        )
        engine = TechnicalInterviewFlowEngine(candidate_profile=p, config=config)

        answers = [
            # Introduction
            "I have built responsive React web applications with Node.js and Express backends, connecting to MongoDB with clean REST APIs.",
            # Experience / React hooks
            "I use useState for component state and useEffect for data fetching. For global state across multiple components I use Context API or Zustand to avoid prop drilling and unnecessary re-renders.",
            # Conceptual / Event loop
            "Node.js event loop runs on a single thread. When synchronous code runs, it executes on the call stack. Async I/O is offloaded to libuv thread pool so the server remains non-blocking.",
            # Scenario / MongoDB query
            "I run explain('executionStats') to inspect COLLSCAN vs IXSCAN. Then I create compound indexes following the Equality, Sort, Range ESR rule to eliminate high query latency and memory bottlenecks.",
            # Wrap-up
            "What continuous integration tools and deployment workflows does your team use for frontend and backend microservices?",
        ]

        turn_idx = 0
        while engine.current_state != InterviewFlowState.COMPLETED and turn_idx < len(answers):
            q = engine.prepare_next_question()
            if not q or engine.current_state == InterviewFlowState.COMPLETED:
                break
            ans = answers[turn_idx]
            engine.process_candidate_turn(ans)
            turn_idx += 1

        report = engine.generate_final_report()
        self.assertIsInstance(report, TechnicalInterviewReport)
        self.assertEqual(report.candidate_id, "CAND-MERN-JR")
        self.assertGreater(report.final_technical_score, 50.0)
        self.assertIn(report.recommendation, [RecommendationVerdict.STRONG_HIRE, RecommendationVerdict.LEAN_HIRE, RecommendationVerdict.BORDERLINE])
        self.assertGreaterEqual(report.total_turns, 4)

    def test_12_senior_devops_cloud_end_to_end_simulation(self):
        """Simulate senior DevOps architect interview testing advanced Kubernetes and Multi-region DR."""
        p = CandidateProfile(candidate_id="CAND-DEVOPS-SR", target_role=JobRole.DEVOPS_CLOUD, years_experience=7.0)
        config = TechnicalInterviewConfig(
            session_id="SESS-SR-DEVOPS",
            target_role=JobRole.DEVOPS_CLOUD,
            experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
            min_questions_per_phase={
                QuestionCategory.INTRODUCTION: 1,
                QuestionCategory.EXPERIENCE_BASED: 1,
                QuestionCategory.CONCEPTUAL: 1,
                QuestionCategory.SCENARIO_BASED: 1,
                QuestionCategory.SYSTEM_DESIGN: 1,
            },
            max_probing_depth=1,
        )
        engine = TechnicalInterviewFlowEngine(candidate_profile=p, config=config)

        answers = [
            # Introduction
            "Over 7 years I have architected multi-region Kubernetes clusters on AWS, automated CI/CD with GitOps pipelines, and managed infrastructure using Terraform modules.",
            # Experience / Terraform
            "We use S3 remote backends with DynamoDB state locking. We decompose monoliths into modular components and use terraform plan -refresh-only to detect cloud console drift and prevent state corruption.",
            # Conceptual / Multi-stage builds
            "Multi-stage Docker builds separate build compilers from minimal runtime images like distroless or alpine. This slashes attack surface and reduces image sizes from 1.2GB to 45MB while optimizing layer caching.",
            # Scenario / K8s CrashLoopBackOff & OOMKill
            "I check kubectl describe pod exit code 137, inspect cgroups memory limits, and review previous container logs. We rollback via ArgoCD and adjust container resource requests and limits to prevent evictions.",
            # System Design / Multi-region K8s DR
            "I architect an active-active multi-region Kubernetes setup using Route53 DNS routing, Istio service mesh, Thanos for cross-cluster Prometheus metrics, and automated failover targeting RTO < 5m and RPO < 1m.",
            # Wrap up
            "How does your engineering team approach chaos engineering and automated DR testing in production?",
        ]

        turn_idx = 0
        while engine.current_state != InterviewFlowState.COMPLETED and turn_idx < len(answers):
            q = engine.prepare_next_question()
            if not q or engine.current_state == InterviewFlowState.COMPLETED:
                break
            ans = answers[turn_idx]
            engine.process_candidate_turn(ans)
            turn_idx += 1

        report = engine.generate_final_report()
        self.assertEqual(report.candidate_id, "CAND-DEVOPS-SR")
        self.assertGreaterEqual(report.final_technical_score, 60.0)
        self.assertIn(report.recommendation, [RecommendationVerdict.STRONG_HIRE, RecommendationVerdict.LEAN_HIRE, RecommendationVerdict.BORDERLINE])
        self.assertIn(report.demonstrated_blooms_level, [BloomsTaxonomyLevel.CREATE, BloomsTaxonomyLevel.EVALUATE, BloomsTaxonomyLevel.ANALYZE])
        self.assertIn(QuestionCategory.SYSTEM_DESIGN.value, report.category_scores)

    def test_13_mid_java_backend_simulation(self):
        """Simulate mid-level Java backend engineer testing Spring Data JPA and Kafka rebalancing."""
        p = CandidateProfile(candidate_id="CAND-JAVA-MID", target_role=JobRole.JAVA_BACKEND, years_experience=3.5)
        config = TechnicalInterviewConfig(
            session_id="SESS-MID-JAVA",
            target_role=JobRole.JAVA_BACKEND,
            experience_tier=ExperienceTier.MID_3_5_YRS,
            min_questions_per_phase={
                QuestionCategory.INTRODUCTION: 1,
                QuestionCategory.EXPERIENCE_BASED: 1,
                QuestionCategory.CONCEPTUAL: 1,
                QuestionCategory.SCENARIO_BASED: 1,
                QuestionCategory.SYSTEM_DESIGN: 0,
            },
            max_probing_depth=1,
        )
        engine = TechnicalInterviewFlowEngine(candidate_profile=p, config=config)

        answers = [
            # Introduction
            "I have 3.5 years developing enterprise microservices with Spring Boot, Java, and PostgreSQL, using Kafka for asynchronous messaging.",
            # Experience / Hibernate N+1
            "We resolved Hibernate N+1 queries using JOIN FETCH in JPQL queries and @EntityGraph definitions. We verified SQL query counts using Hibernate statistics logs.",
            # Conceptual / JVM Memory
            "JVM memory consists of Heap, Metaspace, and Thread Stacks. Young generation uses Eden and Survivor spaces before objects tenure into Old Generation.",
            # Scenario / Kafka rebalances
            "We tuned max.poll.interval.ms and moved CPU-intensive tasks to asynchronous worker thread pools so consumer heartbeats never timeout. We also implemented idempotent consumer deduplication.",
            # Wrap up
            "What message broker serialization formats (Avro vs Protobuf) are standard across your backend teams?",
        ]

        turn_idx = 0
        while engine.current_state != InterviewFlowState.COMPLETED and turn_idx < len(answers):
            q = engine.prepare_next_question()
            if not q or engine.current_state == InterviewFlowState.COMPLETED:
                break
            ans = answers[turn_idx]
            engine.process_candidate_turn(ans)
            turn_idx += 1

        report = engine.generate_final_report()
        self.assertEqual(report.candidate_id, "CAND-JAVA-MID")
        self.assertGreaterEqual(report.final_technical_score, 50.0)
        self.assertIn(report.recommendation, [RecommendationVerdict.STRONG_HIRE, RecommendationVerdict.LEAN_HIRE, RecommendationVerdict.BORDERLINE])

    def test_14_senior_python_data_lakehouse_simulation(self):
        """Simulate senior Python data engineer testing PySpark skew and Delta Lake ACID pipelines."""
        p = CandidateProfile(candidate_id="CAND-PY-SR", target_role=JobRole.PYTHON_DATA_ENG, years_experience=6.0)
        config = TechnicalInterviewConfig(
            session_id="SESS-SR-PY",
            target_role=JobRole.PYTHON_DATA_ENG,
            experience_tier=ExperienceTier.SENIOR_5_PLUS_YRS,
            min_questions_per_phase={
                QuestionCategory.INTRODUCTION: 1,
                QuestionCategory.EXPERIENCE_BASED: 1,
                QuestionCategory.CONCEPTUAL: 1,
                QuestionCategory.SCENARIO_BASED: 1,
                QuestionCategory.SYSTEM_DESIGN: 1,
            },
            max_probing_depth=1,
        )
        engine = TechnicalInterviewFlowEngine(candidate_profile=p, config=config)

        answers = [
            # Introduction
            "Over 6 years I have built petabyte-scale data pipelines with PySpark, Delta Lake, and Airflow, deploying FastAPI services for low-latency feature serving.",
            # Experience / Spark Skew
            "We identified data skew via Spark UI task durations. We resolved it by salting the high-cardinality join keys with random prefixes and enabling Adaptive Query Execution (AQE).",
            # Conceptual / GIL
            "The GIL is a mutex in CPython protecting memory reference counting. For CPU-bound tasks it restricts execution to one core, while I/O-bound tasks release it during network or disk waits.",
            # Scenario / Airflow Idempotency
            "We designed idempotent Airflow DAGs using the Write-Audit-Publish pattern with Delta Lake ACID transactions and MERGE INTO operations partitioned by execution_date.",
            # System Design / 5TB Lakehouse
            "We architected a Kappa streaming platform using Kafka into Spark Structured Streaming with Delta Lake storage, leveraging Z-Ordering and Trino for sub-5-second interactive queries.",
            # Wrap up
            "What data catalog and governance tools (like Apache Atlas or OpenMetadata) does your platform integrate?",
        ]

        turn_idx = 0
        while engine.current_state != InterviewFlowState.COMPLETED and turn_idx < len(answers):
            q = engine.prepare_next_question()
            if not q or engine.current_state == InterviewFlowState.COMPLETED:
                break
            ans = answers[turn_idx]
            engine.process_candidate_turn(ans)
            turn_idx += 1

        report = engine.generate_final_report()
        self.assertEqual(report.candidate_id, "CAND-PY-SR")
        self.assertGreaterEqual(report.final_technical_score, 55.0)
        self.assertIn(report.recommendation, [RecommendationVerdict.STRONG_HIRE, RecommendationVerdict.LEAN_HIRE, RecommendationVerdict.BORDERLINE])

    def test_15_scaffolding_hint_escalation_and_recovery(self):
        """Verify progressive hints are provided when candidate struggles, followed by recovery."""
        p = CandidateProfile(candidate_id="CAND-SCAFFOLD", target_role=JobRole.MERN_STACK, years_experience=1.0)
        engine = TechnicalInterviewFlowEngine(p)
        engine.transition_to(InterviewFlowState.CONCEPTUAL_EVALUATION)

        q = engine.prepare_next_question()
        self.assertIsNotNone(q)

        # Turn 1: Weak answer -> hint provided
        action1, reply1, eval1 = engine.process_candidate_turn("I am not sure how the event loop works.")
        self.assertIn(action1, [SubTurnAction.PROVIDE_SCAFFOLDING_HINT, SubTurnAction.PROBE_DEEPER])
        self.assertEqual(engine.current_probing_depth, 1)

        # Turn 2: Recovered answer using hint
        recovered = (
            "With that hint, the call stack executes synchronous code while asynchronous callbacks "
            "are handled by libuv thread pool and queued onto the event loop task queues."
        )
        action2, reply2, eval2 = engine.process_candidate_turn(recovered)
        self.assertGreater(eval2.aggregate_score, eval1.aggregate_score)

    def test_16_session_pause_and_resume_transitions(self):
        """Verify session can transition to PAUSED and legally resume."""
        p = CandidateProfile(candidate_id="CAND-PAUSE", target_role=JobRole.JAVA_BACKEND, years_experience=2.0)
        engine = TechnicalInterviewFlowEngine(p)
        engine.transition_to(InterviewFlowState.INTRODUCTION)

        # Pause
        self.assertTrue(engine.transition_to(InterviewFlowState.PAUSED, reason="Candidate requested temporary break"))
        self.assertEqual(engine.current_state, InterviewFlowState.PAUSED)

        # Resume to INTRODUCTION
        self.assertTrue(engine.transition_to(InterviewFlowState.INTRODUCTION, reason="Candidate returned from break"))
        self.assertEqual(engine.current_state, InterviewFlowState.INTRODUCTION)

    def test_17_terminal_state_invariants(self):
        """Verify terminal state COMPLETED cannot transition to any other state."""
        p = CandidateProfile(candidate_id="CAND-TERM", target_role=JobRole.DEVOPS_CLOUD, years_experience=4.0)
        engine = TechnicalInterviewFlowEngine(p)
        engine.transition_to(InterviewFlowState.INTRODUCTION)
        engine.transition_to(InterviewFlowState.EXPERIENCE_PROBING)
        engine.transition_to(InterviewFlowState.CONCEPTUAL_EVALUATION)
        engine.transition_to(InterviewFlowState.SCENARIO_ANALYSIS)
        engine.transition_to(InterviewFlowState.WRAP_UP)
        engine.transition_to(InterviewFlowState.COMPLETED)

        self.assertEqual(engine.current_state, InterviewFlowState.COMPLETED)
        # Attempt illegal transition from terminal state
        self.assertFalse(engine.transition_to(InterviewFlowState.INTRODUCTION))
        self.assertFalse(engine.can_transition_to(InterviewFlowState.PAUSED))

    def test_18_report_generation_without_turns_raises_value_error(self):
        """Verify attempting to generate a report without turns raises ValueError."""
        p = CandidateProfile(candidate_id="CAND-EMPTY", target_role=JobRole.MERN_STACK, years_experience=2.0)
        engine = TechnicalInterviewFlowEngine(p)
        with self.assertRaises(ValueError):
            engine.generate_final_report()


if __name__ == "__main__":
    unittest.main()
