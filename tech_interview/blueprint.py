"""
Zecpath-AI: Technical Interview AI System Blueprint
===================================================
Production architectural blueprint defining the core specifications, schemas,
contracts, and subsystem topologies for role-based technical interviews.

Curriculum Reference: Day 46 - Technical Interview System Design
Deliverable 1: Technical Interview AI Blueprint
"""

from typing import List, Dict, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import time


# ==============================================================================
# 1. CORE ENUMERATIONS & TAXONOMIES
# ==============================================================================

class JobRole(str, Enum):
    """Target technical job roles supported by the interview engine."""
    MERN_STACK = "MERN_STACK"
    JAVA_BACKEND = "JAVA_BACKEND"
    DEVOPS_CLOUD = "DEVOPS_CLOUD"
    PYTHON_DATA_ENG = "PYTHON_DATA_ENG"
    FULLSTACK_GENERALIST = "FULLSTACK_GENERALIST"


class ExperienceTier(str, Enum):
    """Candidate experience tiers with explicit technical scope boundaries."""
    JUNIOR_0_2_YRS = "0-2_YRS"       # Focus: Basics, syntax, core data structures, debugging
    MID_3_5_YRS = "3-5_YRS"          # Focus: Intermediate, design patterns, DB optimization, async
    SENIOR_5_PLUS_YRS = "5+_YRS"      # Focus: Advanced, system design, scalability, distributed systems


class QuestionCategory(str, Enum):
    """Core interview phases defining the conversational structure."""
    INTRODUCTION = "INTRODUCTION"
    EXPERIENCE_BASED = "EXPERIENCE_BASED"
    CONCEPTUAL = "CONCEPTUAL"
    SCENARIO_BASED = "SCENARIO_BASED"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    WRAP_UP = "WRAP_UP"


class DifficultyLevel(int, Enum):
    """Discrete 5-point difficulty rating scale."""
    L1_BASIC = 1           # Foundational syntax, definitions, simple structures
    L2_FOUNDATIONAL = 2    # Practical implementation, core APIs, error handling
    L3_INTERMEDIATE = 3    # Design patterns, concurrency, database indexing, caching
    L4_ADVANCED = 4        # Performance tuning, distributed primitives, edge failures
    L5_SYSTEM_DESIGN = 5   # Large-scale architecture, sharding, consensus, fault tolerance


class BloomsTaxonomyLevel(str, Enum):
    """Bloom's revised cognitive taxonomy levels for assessing depth."""
    REMEMBER = "REMEMBER"        # Recall facts, syntax, definitions
    UNDERSTAND = "UNDERSTAND"    # Explain concepts, trade-offs, mechanisms
    APPLY = "APPLY"              # Execute code, write queries, solve concrete bug
    ANALYZE = "ANALYZE"          # Deconstruct failure modes, bottlenecks, performance
    EVALUATE = "EVALUATE"        # Defend architecture choices, compare technologies
    CREATE = "CREATE"            # Synthesize end-to-end distributed system architecture


class InterviewFlowState(str, Enum):
    """Finite State Machine (FSM) states for technical interview execution."""
    INITIALIZED = "INITIALIZED"
    INTRODUCTION = "INTRODUCTION"
    EXPERIENCE_PROBING = "EXPERIENCE_PROBING"
    CONCEPTUAL_EVALUATION = "CONCEPTUAL_EVALUATION"
    SCENARIO_ANALYSIS = "SCENARIO_ANALYSIS"
    SYSTEM_DESIGN_DEEPDIVE = "SYSTEM_DESIGN_DEEPDIVE"
    WRAP_UP = "WRAP_UP"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    ABORTED = "ABORTED"


class SubTurnAction(str, Enum):
    """Sub-turn adaptive conversational actions."""
    ADVANCE_QUESTION = "ADVANCE_QUESTION"
    PROBE_DEEPER = "PROBE_DEEPER"
    PROVIDE_SCAFFOLDING_HINT = "PROVIDE_SCAFFOLDING_HINT"
    FALLBACK_LATERAL = "FALLBACK_LATERAL"
    TRANSITION_STATE = "TRANSITION_STATE"


class RecommendationVerdict(str, Enum):
    """Final hiring assessment outcome."""
    STRONG_HIRE = "STRONG_HIRE"
    LEAN_HIRE = "LEAN_HIRE"
    BORDERLINE = "BORDERLINE"
    NO_HIRE = "NO_HIRE"


# ==============================================================================
# 2. DATA MODELS & CONFIGURATION SCHEMAS
# ==============================================================================

class CandidateProfile(BaseModel):
    """Input profile representing candidate resume grounding and target role."""
    candidate_id: str = Field(..., description="Unique pseudonymous candidate identifier", example="CAND-TECH-4601")
    target_role: JobRole = Field(..., description="Primary job role being interviewed for")
    years_experience: float = Field(..., ge=0.0, le=40.0, description="Total verified professional experience")
    claimed_skills: List[str] = Field(default_factory=list, description="Skills extracted from resume")
    primary_language: str = Field(default="English", description="Interview communication language")
    experience_tier: Optional[ExperienceTier] = None

    def model_post_init(self, __context: Any) -> None:
        """Automatically classify experience tier if not explicitly provided."""
        if self.experience_tier is None:
            if self.years_experience < 3.0:
                self.experience_tier = ExperienceTier.JUNIOR_0_2_YRS
            elif self.years_experience <= 5.0:
                self.experience_tier = ExperienceTier.MID_3_5_YRS
            else:
                self.experience_tier = ExperienceTier.SENIOR_5_PLUS_YRS


class TechnicalInterviewConfig(BaseModel):
    """Operational parameters governing interview execution and constraints."""
    session_id: str = Field(default="", description="Unique interview session UUID")
    target_role: JobRole
    experience_tier: ExperienceTier
    min_questions_per_phase: Dict[QuestionCategory, int] = Field(
        default={
            QuestionCategory.INTRODUCTION: 1,
            QuestionCategory.EXPERIENCE_BASED: 2,
            QuestionCategory.CONCEPTUAL: 2,
            QuestionCategory.SCENARIO_BASED: 2,
            QuestionCategory.SYSTEM_DESIGN: 1,
        }
    )
    max_probing_depth: int = Field(default=2, ge=0, le=3, description="Maximum recursive follow-up probes per question")
    enable_dynamic_scaffolding: bool = Field(default=True, description="Enable algorithmic hints on candidate struggle")
    adaptation_sensitivity: float = Field(default=0.8, ge=0.1, le=2.0, description="Difficulty adjustment step multiplier")
    equilibrium_score_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Score threshold for neutral difficulty")
    time_limit_minutes: int = Field(default=45, ge=15, le=90, description="Total interview time envelope")


class TechnicalEvaluationRubric(BaseModel):
    """Standardized 4-dimensional technical response evaluation rubric."""
    conceptual_correctness: float = Field(..., ge=0.0, le=1.0, description="Factual correctness of theory & algorithms")
    implementation_depth: float = Field(..., ge=0.0, le=1.0, description="Granularity of technical mechanics & edge cases")
    architectural_tradeoffs: float = Field(..., ge=0.0, le=1.0, description="Awareness of scaling, memory, and complexity trade-offs")
    communication_clarity: float = Field(..., ge=0.0, le=1.0, description="Conciseness, structured thought, and precision")
    aggregate_score: float = Field(..., ge=0.0, le=1.0, description="Weighted composite score")
    blooms_demonstrated: BloomsTaxonomyLevel
    detected_gaps: List[str] = Field(default_factory=list)
    positive_signals: List[str] = Field(default_factory=list)


# ==============================================================================
# 3. ARCHITECTURAL BLUEPRINT DEFINITION
# ==============================================================================

class TechnicalInterviewAIBlueprint:
    """
    Formal architectural specification and blueprint for the Role-Based
    Technical Interview AI System.

    Subsystems:
    1. Ingestion & Role Profiling Subsystem (IRPS)
    2. Adaptive Question Orchestrator (AQO)
    3. Cognitive & Technical Evaluation Engine (CTEE)
    4. State Machine Flow Coordinator (SMFC)
    5. Integrity, Statutory & Fairness Gateway (ISFG)
    """

    VERSION = "1.0.0-PROD-BLUEPRINT"
    SPECIFICATION_ID = "SPEC-ZECPATH-TECH-AI-DAY46"

    @classmethod
    def get_blueprint_manifest(cls) -> Dict[str, Any]:
        """Returns the complete architectural blueprint specification dictionary."""
        return {
            "specification_id": cls.SPECIFICATION_ID,
            "version": cls.VERSION,
            "system_title": "Zecpath-AI Scalable Role-Based Technical Interview Engine",
            "curriculum_milestone": "Day 46: Technical Interview System Design",
            "supported_roles": [r.value for r in JobRole],
            "supported_tiers": [t.value for t in ExperienceTier],
            "subsystems": {
                "Subsystem_1_IRPS": {
                    "name": "Ingestion & Role Profiling Subsystem",
                    "purpose": "Parses candidate experience, maps resume technical claims, and assigns baseline tier.",
                    "components": ["ExperienceTierClassifier", "SkillDomainResolver", "CandidateBaselineGrounder"],
                    "latency_budget_ms": 15,
                },
                "Subsystem_2_AQO": {
                    "name": "Adaptive Question Orchestrator",
                    "purpose": "Selects questions hierarchically and drives Dynamic Difficulty Adaptation (DDA).",
                    "components": ["QuestionHierarchyTaxonomy", "DynamicDifficultyProgressionEngine", "DomainCoverageTracker"],
                    "latency_budget_ms": 25,
                },
                "Subsystem_3_CTEE": {
                    "name": "Cognitive & Technical Evaluation Engine",
                    "purpose": "Multi-dimensional grading of responses across correctness, depth, trade-offs, and Bloom's taxonomy.",
                    "components": ["4DimensionRubricScorer", "BloomsTaxonomyClassifier", "DynamicProbeDetector"],
                    "latency_budget_ms": 45,
                },
                "Subsystem_4_SMFC": {
                    "name": "State Machine Flow Coordinator",
                    "purpose": "Deterministic Finite State Machine managing phases, transitions, and sub-turn actions.",
                    "components": ["TechnicalInterviewFSM", "TransitionGuardValidator", "ScaffoldingController"],
                    "latency_budget_ms": 10,
                },
                "Subsystem_5_ISFG": {
                    "name": "Integrity, Statutory & Fairness Gateway",
                    "purpose": "Enforces anti-bias masking, consent receipts, and immutable audit trails.",
                    "components": ["DemographicScrubber", "StatutoryConsentReceiptVerifier", "SessionAuditLogger"],
                    "latency_budget_ms": 20,
                },
            },
            "sla_guarantees": {
                "max_turn_latency_ms": 150,
                "fsm_transition_determinism": "100%",
                "recursion_depth_limit": 2,
                "dynamic_difficulty_bounds": [1.0, 5.0],
            },
            "statutory_compliance": [
                "EU AI Act (Annex III High-Risk Employment AI Article 13 & 14)",
                "NYC Local Law 144 Bias Audit Standard",
                "Illinois BIPA (740 ILCS 14/)",
                "EEOC Uniform Guidelines (29 CFR § 1607)",
            ]
        }

    @classmethod
    def generate_blueprint_hash(cls) -> str:
        """Computes deterministic SHA-256 integrity hash of system blueprint."""
        manifest = str(cls.get_blueprint_manifest()).encode("utf-8")
        return hashlib.sha256(manifest).hexdigest()
