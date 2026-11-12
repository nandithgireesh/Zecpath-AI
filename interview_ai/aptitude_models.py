"""
Day 38: Aptitude AI Logic Models & State Schemas
=================================================
Defines foundational data structures for Cognitive and Situational Evaluation:
- CognitiveDimension (Root Cause, Trade-offs, Systems, Estimation, Hypothesis)
- ScenarioCategory (System Incident, Stakeholder Conflict, Ethical Dilemma, etc.)
- CognitiveMaturityLevel (Exemplary, Proficient, Competent, Superficial, Deficient)
- ReasoningQuestion & SituationalScenario definitions with ideal answer structure mappings
- LogicalReasoningBreakdown & ProblemSolvingClarityBreakdown evaluation schemas
- ScenarioEvaluationResult schema for ATS dossier integration
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# =========================================================================
# 1. Core Enumerations
# =========================================================================

class CognitiveDimension(str, Enum):
    """Core cognitive reasoning dimensions evaluated in candidate aptitude."""
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"          # Deconstructing symptoms to find origin failure
    TRADE_OFF_EVALUATION = "trade_off_evaluation"        # Balancing competing constraints (speed vs quality, CAP)
    SYSTEMIC_THINKING = "systemic_thinking"              # Understanding cascading second-order impacts
    RESOURCE_ESTIMATION = "resource_estimation"          # Fermi estimation, capacity constraints, scale bounds
    HYPOTHESIS_TESTING = "hypothesis_testing"            # Formulating falsifiable test steps and verification


class ScenarioCategory(str, Enum):
    """Situational Judgment Test (SJT) operational scenario domains."""
    SYSTEM_INCIDENT_ESCALATION = "system_incident_escalation"  # Production outages, downtime, SLA breaches
    STAKEHOLDER_CONFLICT = "stakeholder_conflict"              # Divergent expectations between PM, Client, and Dev
    ETHICAL_DILEMMA = "ethical_dilemma"                        # Data privacy, security shortcuts, intellectual property
    AMBIGUOUS_REQUIREMENT = "ambiguous_requirement"            # Incomplete specifications, early stage MVP pivots
    RESOURCE_CRUNCH = "resource_crunch"                        # Severe time, compute, or staffing shortages


class CognitiveMaturityLevel(str, Enum):
    """Calibrated cognitive reasoning maturity tiers."""
    EXEMPLARY = "EXEMPLARY"          # Score >= 85: Structured, counter-factual, nuanced trade-off mastery
    PROFICIENT = "PROFICIENT"        # Score 70 - 84: Logical, methodical problem-solving with minor gaps
    COMPETENT = "COMPETENT"          # Score 55 - 69: Adequate practical reasoning but occasional intuition leaps
    SUPERFICIAL = "SUPERFICIAL"      # Score 40 - 54: Surface-level answers lacking root-cause or trade-off depth
    DEFICIENT = "DEFICIENT"          # Score < 40: Chaotic, fallacious, or evasive problem-solving


class FrameworkType(str, Enum):
    """Ideal cognitive response structuring frameworks."""
    IDEA = "IDEA"  # Identify premise, Define constraints, Evaluate alternatives, Action & mitigation
    CARL = "CARL"  # Context, Action, Reasoning, Learning
    STAR_R = "STAR_R"  # Situation, Task, Action, Result with explicit Reasoning


# =========================================================================
# 2. Reasoning Questions & Scenario Specifications
# =========================================================================

class IdealAnswerStructure(BaseModel):
    """Prescribed cognitive milestones for ideal scenario answers."""
    framework: FrameworkType = FrameworkType.IDEA
    stage_1_identify: str = Field(..., description="Problem deconstruction & premise identification")
    stage_2_constraints: str = Field(..., description="Boundary conditions, assumptions, resource bounds")
    stage_3_evaluation: str = Field(..., description="Option evaluation, trade-off trade-offs, pros & cons")
    stage_4_action_plan: str = Field(..., description="Concrete execution sequence, mitigations & post-mortem")


class ReasoningQuestion(BaseModel):
    """Structured analytical and logical reasoning question."""
    question_id: str
    dimension: CognitiveDimension
    title: str
    prompt: str
    target_premises: List[str] = Field(default_factory=list, description="Core facts candidate must address")
    required_tradeoffs: List[str] = Field(default_factory=list, description="Key trade-offs candidate must weigh")
    ideal_structure: IdealAnswerStructure


class SituationalScenario(BaseModel):
    """Situational Judgment Scenario (SJT) modeling real-world dilemmas."""
    scenario_id: str
    category: ScenarioCategory
    title: str
    context_brief: str
    primary_conflict: str
    constraints: List[str] = Field(default_factory=list)
    optimal_action_cues: List[str] = Field(default_factory=list, description="Evidence of high-maturity resolution")
    high_risk_action_cues: List[str] = Field(default_factory=list, description="Anti-patterns or reckless behaviors")
    ideal_structure: IdealAnswerStructure


# =========================================================================
# 3. Scoring Breakdown Models
# =========================================================================

class LogicalReasoningBreakdown(BaseModel):
    """Detailed diagnostic breakdown of logical reasoning capabilities."""
    premise_identification_score: float = Field(..., ge=0.0, le=100.0)
    causal_inference_score: float = Field(..., ge=0.0, le=100.0)
    tradeoff_depth_score: float = Field(..., ge=0.0, le=100.0)
    fallacy_deductions: float = Field(0.0, ge=0.0, le=50.0)
    detected_fallacies: List[str] = Field(default_factory=list)
    calibrated_logic_score: float = Field(..., ge=0.0, le=100.0)


class ProblemSolvingClarityBreakdown(BaseModel):
    """Detailed diagnostic breakdown of problem-solving clarity."""
    structural_signposting_score: float = Field(..., ge=0.0, le=100.0)
    causal_linkage_density_score: float = Field(..., ge=0.0, le=100.0)
    depth_to_breadth_ratio: float = Field(..., ge=0.0)
    decisiveness_score: float = Field(..., ge=0.0, le=100.0)
    calibrated_clarity_score: float = Field(..., ge=0.0, le=100.0)


class ScenarioEvaluationResult(BaseModel):
    """Consolidated cognitive aptitude and situational judgment assessment."""
    scenario_id: str
    scenario_title: str
    category: ScenarioCategory
    candidate_response: str
    
    # Core Dimension Scores (0 - 100)
    logical_reasoning: LogicalReasoningBreakdown
    problem_solving_clarity: ProblemSolvingClarityBreakdown
    situational_effectiveness_score: float = Field(..., ge=0.0, le=100.0)
    risk_mitigation_score: float = Field(..., ge=0.0, le=100.0)
    stakeholder_awareness_score: float = Field(..., ge=0.0, le=100.0)
    
    # Composite Aptitude
    composite_aptitude_score: float = Field(..., ge=0.0, le=100.0)
    cognitive_maturity: CognitiveMaturityLevel
    
    # Qualitative Diagnostics
    framework_adherence_percent: float = Field(..., ge=0.0, le=100.0)
    observed_strengths: List[str] = Field(default_factory=list)
    cognitive_flags: List[str] = Field(default_factory=list)
    recruiter_coaching_notes: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
