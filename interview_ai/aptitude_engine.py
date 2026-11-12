"""
Day 38: Aptitude AI Design (Deliverable 1)
=========================================
Central engine for Cognitive and Situational Evaluation:
- Reasoning-based question taxonomy & bank
- Situational Judgment Test (SJT) scenario bank across 5 operational dilemmas
- IDEA & CARL ideal answer structure mappings
- Evaluates candidate responses using LogicalReasoningScorer & ScenarioEvaluator
- Seamless integration with HR interview flow and ATS dossier exports
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from interview_ai.aptitude_models import (
    CognitiveDimension,
    ScenarioCategory,
    FrameworkType,
    IdealAnswerStructure,
    ReasoningQuestion,
    SituationalScenario,
    ScenarioEvaluationResult,
    CognitiveMaturityLevel,
)
from interview_ai.logical_reasoning_scorer import LogicalReasoningScorer
from interview_ai.scenario_evaluator import ScenarioEvaluator
from interview_ai.hr_models import RoleTrack


class AptitudeAIEngine:
    """
    Central orchestration engine for Day 38 Aptitude AI.
    Generates tailored reasoning questions, presents situational dilemmas,
    and coordinates quantitative cognitive evaluation.
    """

    def __init__(self):
        self.logic_scorer = LogicalReasoningScorer()
        self.scenario_evaluator = ScenarioEvaluator(self.logic_scorer)
        self.reasoning_questions: Dict[str, ReasoningQuestion] = {}
        self.scenarios: Dict[str, SituationalScenario] = {}
        self._initialize_question_and_scenario_banks()

    def _initialize_question_and_scenario_banks(self):
        """Seed the engine with realistic enterprise reasoning questions and situational dilemmas."""
        
        # -------------------------------------------------------------
        # 1. Reasoning-Based Questions
        # -------------------------------------------------------------
        q_root_cause = ReasoningQuestion(
            question_id="Q_REASON_01",
            dimension=CognitiveDimension.ROOT_CAUSE_ANALYSIS,
            title="Distributed Database Latency Spike Diagnostic",
            prompt=(
                "During peak traffic, p99 API latency spikes from 80ms to 4.5 seconds, but CPU "
                "utilization on all web servers remains below 25%. How would you methodically isolate "
                "the root cause without restarting the cluster?"
            ),
            target_premises=[
                "Database connection pool exhaustion",
                "Lock contention or slow database queries",
                "Downstream third-party synchronous API blocking",
                "Network switch / egress saturation",
            ],
            required_tradeoffs=[
                "Diagnostic telemetry depth versus live cluster performance overhead",
                "Immediate mitigation (rate limiting / circuit breaker) versus root cause preservation",
            ],
            ideal_structure=IdealAnswerStructure(
                framework=FrameworkType.IDEA,
                stage_1_identify="Identify that low CPU indicates an I/O wait, connection lock, or downstream latency bottleneck.",
                stage_2_constraints="Constraint: Zero cluster restart allowed; must maintain live transaction integrity.",
                stage_3_evaluation="Evaluate telemetry: database lock queues, thread pool dump, slow query log, connection pool status.",
                stage_4_action_plan="Action: Inspect connection pool metrics, isolate slow queries, enable circuit breakers, conduct post-mortem.",
            )
        )

        q_tradeoff = ReasoningQuestion(
            question_id="Q_REASON_02",
            dimension=CognitiveDimension.TRADE_OFF_EVALUATION,
            title="Data Consistency vs Availability Architecture",
            prompt=(
                "You are designing a distributed payment ledger that operates across multiple global regions. "
                "Under network partition conditions, would you favor strict consistency or high availability, "
                "and how would you justify the resulting operational trade-offs to business stakeholders?"
            ),
            target_premises=[
                "CAP theorem fundamental limits (CP vs AP)",
                "Financial ledger double-spending risks",
                "Idempotency and reconciliation pipelines",
            ],
            required_tradeoffs=[
                "Strong consistency with transient unavailability versus eventual consistency with reconciliation complexity",
                "Customer transaction failure vs reconciliation financial risk",
            ],
            ideal_structure=IdealAnswerStructure(
                framework=FrameworkType.IDEA,
                stage_1_identify="Identify that payment processing mandates zero double-spend, making strict consistency non-negotiable for transfers.",
                stage_2_constraints="Constraint: Global network latency partitions are inevitable; regulatory compliance requires auditability.",
                stage_3_evaluation="Evaluate CP approach (fail-closed for ledger) paired with AP approach for non-financial read telemetry.",
                stage_4_action_plan="Action: Implement distributed consensus (Raft/Paxos) for ledger, queue pending orders, and provide clear user messaging.",
            )
        )

        self.reasoning_questions[q_root_cause.question_id] = q_root_cause
        self.reasoning_questions[q_tradeoff.question_id] = q_tradeoff

        # -------------------------------------------------------------
        # 2. Situational Judgment Scenarios (SJTs)
        # -------------------------------------------------------------
        sjt_incident = SituationalScenario(
            scenario_id="SJT_INCIDENT_01",
            category=ScenarioCategory.SYSTEM_INCIDENT_ESCALATION,
            title="Critical Production Outage During Black Friday Flash Sale",
            context_brief=(
                "Ten minutes into the annual Black Friday flash sale, the checkout checkout service begins "
                "throwing HTTP 500 errors on 40% of transactions. The marketing team is actively running paid ads "
                "driving 50,000 requests/minute. The team lead believes a recent optimization PR deployed 30 minutes ago "
                "might be the cause, but rolling it back will discard database schema migrations."
            ),
            primary_conflict="Emergency triage and revenue loss prevention versus database corruption risk.",
            constraints=[
                "High concurrency: 50,000 active requests per minute",
                "Schema migration is backward-incompatible with previous binary version",
                "Senior VP of Sales is demanding immediate resolution on the incident bridge",
            ],
            optimal_action_cues=[
                "isolate failure domain",
                "enable feature flag",
                "enable degraded mode",
                "redirect traffic to standby queue",
                "communicate transparently on status bridge",
                "revert or hotfix migration safely",
                "post-mortem analysis",
            ],
            high_risk_action_cues=[
                "force restart production database without backup",
                "panic and deploy untested emergency code directly to prod",
                "ignore customer error rates and continue ads",
                "blame the junior developer publicly",
            ],
            ideal_structure=IdealAnswerStructure(
                framework=FrameworkType.IDEA,
                stage_1_identify="Identify: Core conflict is immediate transaction failure affecting 40% of checkouts amidst high-volume ads.",
                stage_2_constraints="Constraints: Irreversible schema migration prevents naive git revert; live revenue at stake.",
                stage_3_evaluation="Evaluate: Option A (full rollback with data loss) vs Option B (graceful queueing + feature-flag bypass of faulty logic).",
                stage_4_action_plan="Action: 1. Pause ads, 2. Toggle faulty feature flag to safe path, 3. Establish incident updates, 4. Root-cause post-mortem.",
            )
        )

        sjt_ethical = SituationalScenario(
            scenario_id="SJT_ETHICAL_01",
            category=ScenarioCategory.ETHICAL_DILEMMA,
            title="Confidential Data Logging & Delivery Deadline Pressure",
            context_brief=(
                "Two days before an enterprise client delivery deadline, you discover that a legacy microservice "
                "is writing unencrypted customer plaintext credit card CVVs and personal emails to Elasticsearch debug logs. "
                "Fixing this properly requires rewriting the logging pipeline, which will delay the deadline by 4 days, "
                "costing the company a $20,000 SLA penalty. Your engineering manager suggests 'waiting until next sprint' "
                "to clean up the logs after the delivery bonus is secured."
            ),
            primary_conflict="Compliance, data security, and ethics versus short-term corporate financial bonus and deadlines.",
            constraints=[
                "Strict PCI-DSS and GDPR regulatory penalties for unencrypted PII storage",
                "SLA penalty of $20,000 if deadline slips 4 days",
                "Managerial pressure to ignore the breach until next quarter",
            ],
            optimal_action_cues=[
                "escalate security risk",
                "purge or scrub sensitive log index immediately",
                "temporary log filter or redaction regex",
                "transparent disclosure to compliance officer",
                "refuse unethical suppression",
                "align on emergency security patch window",
            ],
            high_risk_action_cues=[
                "agree to hide the issue until next sprint",
                "delete all logs without audit to destroy evidence",
                "leak proprietary client data to external press",
                "ignore PCI-DSS violation to get the bonus",
            ],
            ideal_structure=IdealAnswerStructure(
                framework=FrameworkType.IDEA,
                stage_1_identify="Identify: PII/PCI-DSS violation poses existential regulatory and legal liability exceeding any $20,000 SLA penalty.",
                stage_2_constraints="Constraints: Immediate compliance violation; contractual SLA penalty; managerial resistance.",
                stage_3_evaluation="Evaluate: Option A (comply with manager and risk criminal/PCI audit) vs Option B (immediate hotfix regex filter + transparent leadership escalation).",
                stage_4_action_plan="Action: 1. Deploy immediate redaction filter on logging daemon, 2. Purge compromised index, 3. Escalate to Security Officer, 4. Transparent client communication.",
            )
        )

        sjt_stakeholder = SituationalScenario(
            scenario_id="SJT_STAKEHOLDER_01",
            category=ScenarioCategory.STAKEHOLDER_CONFLICT,
            title="Conflicting Technical Standards vs Client Customization",
            context_brief=(
                "A tier-1 enterprise client threatening to churn demands a custom single-tenant database sync script "
                "that directly bypasses your core platform APIs and authentication layer. The Product Director wants "
                "to grant the client's request immediately to save the $500k contract. As the lead engineer, you know "
                "this bypass violates core security architecture and creates massive technical debt."
            ),
            primary_conflict="Preserving architectural integrity and system security versus client retention revenue.",
            constraints=[
                "$500,000 contract value at immediate risk",
                "Requested script breaches zero-trust auth architecture",
                "Client deadline is in 7 business days",
            ],
            optimal_action_cues=[
                "understand client underlying business need",
                "propose secure alternative architecture",
                "webhook or bulk export API",
                "collaborate with product director",
                "protect core authentication boundary",
                "executive alignment meeting",
            ],
            high_risk_action_cues=[
                "silently disable authentication for the client",
                "dogmatically refuse to talk to the client",
                "bypass security review without authorization",
            ],
            ideal_structure=IdealAnswerStructure(
                framework=FrameworkType.IDEA,
                stage_1_identify="Identify: Client needs data sync capability, but requesting an insecure direct database bypass.",
                stage_2_constraints="Constraints: $500k retention deadline vs non-negotiable security integrity of multi-tenant platform.",
                stage_3_evaluation="Evaluate: Uncompromised security (authenticated export pipeline) vs custom backdoor (unacceptable risk).",
                stage_4_action_plan="Action: Meet with client technical team, uncover underlying sync requirement, deliver high-speed secure API solution within deadline.",
            )
        )

        self.scenarios[sjt_incident.scenario_id] = sjt_incident
        self.scenarios[sjt_ethical.scenario_id] = sjt_ethical
        self.scenarios[sjt_stakeholder.scenario_id] = sjt_stakeholder

    def get_reasoning_question(self, question_id: str) -> Optional[ReasoningQuestion]:
        """Fetch reasoning question by ID."""
        return self.reasoning_questions.get(question_id)

    def get_scenario(self, scenario_id: str) -> Optional[SituationalScenario]:
        """Fetch situational judgment scenario by ID."""
        return self.scenarios.get(scenario_id)

    def get_recommended_scenario_for_role(self, role_track: RoleTrack) -> SituationalScenario:
        """Select the most representative scenario for the candidate's target role track."""
        if role_track == RoleTrack.TECHNICAL:
            return self.scenarios["SJT_INCIDENT_01"]
        elif role_track == RoleTrack.NON_TECHNICAL:
            return self.scenarios["SJT_STAKEHOLDER_01"]
        else:
            return self.scenarios["SJT_ETHICAL_01"]

    def evaluate_reasoning_response(
        self,
        question_id: str,
        candidate_response: str,
    ) -> Any:
        """Evaluate a dedicated analytical reasoning question response."""
        question = self.get_reasoning_question(question_id)
        return self.logic_scorer.evaluate(candidate_response, question)

    def evaluate_situational_scenario(
        self,
        scenario_id: str,
        candidate_response: str,
    ) -> ScenarioEvaluationResult:
        """Evaluate a full Situational Judgment Scenario response."""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario ID '{scenario_id}' not found in registry.")
        return self.scenario_evaluator.evaluate_scenario(scenario, candidate_response)
