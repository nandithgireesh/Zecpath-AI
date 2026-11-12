# Deliverable 3: Unified Candidate Score Object & Data Architecture
**System:** Zecpath-AI Multi-Modal Enterprise Interview Pipeline  
**Module:** `unified_scoring/models.py` & `unified_scoring/unified_score_object.py`  
**Scope:** Pydantic Object Model, Enterprise ATS JSON Schema & Recruiter Dossier Serialization  
**Standard:** Enterprise HRIS / ATS Interoperability (Workday, Greenhouse, Lever)  

---

## 1. Executive Summary & Purpose

In modern talent acquisition workflows, disparate hiring evaluations are frequently siloed across independent databases, third-party screening platforms, and HR email threads. This fragmentation leads to lost candidate context, subjective interview debriefs, and an inability to conduct end-to-end audits of algorithmic hiring recommendations.

**Deliverable 3: The Unified Candidate Score Object** (`UnifiedCandidateScoreObject`) resolves this fragmentation by establishing an end-to-end, single-source-of-truth data structure that encapsulates every metric, weighting decision, situational signal, and risk discount across all three evaluation rounds:
1. **Round 1:** ATS Resume Parsing & Skill Extraction
2. **Round 2:** Conversational AI Pre-Screening Call
3. **Round 3:** Multi-Turn Behavioral & Situational HR Interview

---

## 2. Pydantic Schema Specification

The `UnifiedCandidateScoreObject` is strictly typed using Pydantic v2, guaranteeing field validation, type safety, and automatic schema generation:

```python
class UnifiedCandidateScoreObject(BaseModel):
    # Candidate & Role Identification
    candidate_id: str = Field(..., description="Unique enterprise candidate ID")
    candidate_name: str = Field(..., description="Full legal candidate name")
    target_role: str = Field(..., description="Job role applied for")
    role_family: RoleFamily = Field(..., description="Assigned role track archetype")
    evaluation_date: str = Field(..., description="ISO 8601 evaluation timestamp")
    
    # Ingested Round Inputs
    round_inputs: Dict[RoundType, RoundScoreInput] = Field(..., description="Raw inputs from Rounds 1, 2, and 3")
    
    # Cross-Round Weighting & Contributions
    weight_profile_used: CrossRoundWeightProfile = Field(..., description="Applied role-based weight profile")
    round_contributions: Dict[RoundType, RoundContribution] = Field(..., description="Weighted point breakdown per round")
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Overall weighted composite score")
    
    # Calibrated Hiring Fit Analytics
    hiring_fit: HiringFitBreakdown = Field(..., description="Multi-dimensional fit percentages & percentile")
    
    # Synthesized Decision & Leveling
    final_decision: HiringDecisionTier = Field(..., description="Consensus recommendation tier")
    readiness_level: ReadinessLevel = Field(..., description="Deployment readiness classification")
    calibrated_role_tier: str = Field(..., description="Specific recommended title or leveling tier")
    executive_verdict: str = Field(..., description="Executive recruiter verdict paragraph")
    
    # Qualitative Diagnostics & Audit
    key_strengths: List[str] = Field(default_factory=list, description="Top positive attributes across rounds")
    developmental_areas: List[str] = Field(default_factory=list, description="Targeted improvement areas")
    safety_gate_passed: bool = Field(default=True, description="Whether all mandatory round gates were satisfied")
    gate_failure_reasons: List[str] = Field(default_factory=list, description="Reasons for any gate rejections")
    audit_metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit hash, version, and calibration stamp")
```

---

## 3. Standardized Enterprise ATS JSON Payload

The unified score object automatically serializes into an ATS/HRIS compliant JSON structure:

```json
{
  "candidate_id": "SIM-CONF-01",
  "candidate_name": "Aditi Rao",
  "target_role": "Senior Cloud Platform Architect",
  "role_family": "TECHNICAL_ENGINEERING",
  "evaluation_date": "2026-09-30T12:00:00.000000",
  "round_inputs": {
    "ATS_RESUME": {
      "round_type": "ATS_RESUME",
      "round_name": "ATS Resume & Skill Matching (Round 1)",
      "raw_score": 88.0,
      "normalized_score": 88.0,
      "confidence_weight": 1.0,
      "dimension_breakdown": {
        "skill_score": 90.0,
        "experience_score": 86.0
      },
      "strengths": ["Strong Kubernetes and multi-cloud architecture alignment."],
      "flags_or_penalties": []
    },
    "CONVERSATIONAL_SCREENING": {
      "round_type": "CONVERSATIONAL_SCREENING",
      "round_name": "Conversational Pre-Screening (Round 2)",
      "raw_score": 85.0,
      "normalized_score": 85.0,
      "confidence_weight": 1.0,
      "dimension_breakdown": {
        "clarity_score": 86.0,
        "behavioral_score": 84.0
      },
      "strengths": ["Articulate response delivery, immediate availability."],
      "flags_or_penalties": []
    },
    "HR_INTERVIEW": {
      "round_type": "HR_INTERVIEW",
      "round_name": "In-Depth HR Interview & Aptitude (Round 3)",
      "raw_score": 90.3,
      "normalized_score": 90.3,
      "confidence_weight": 1.0,
      "dimension_breakdown": {
        "behavioral_score": 90.0,
        "communication_score": 88.0,
        "aptitude_score": 92.0,
        "cultural_fit": 85.0
      },
      "strengths": ["Structured STAR/IDEA incident triage, blameless post-mortem."],
      "flags_or_penalties": []
    }
  },
  "weight_profile_used": {
    "role_family": "TECHNICAL_ENGINEERING",
    "display_name": "Technical & Engineering Track",
    "ats_weight": 0.25,
    "screening_weight": 0.30,
    "hr_interview_weight": 0.45,
    "minimum_thresholds": {
      "ATS_RESUME": 50.0,
      "CONVERSATIONAL_SCREENING": 50.0,
      "HR_INTERVIEW": 55.0
    },
    "rationale": "Emphasizes deep technical reasoning and CAP theorem trade-offs in Round 3 (45%)."
  },
  "round_contributions": {
    "ATS_RESUME": {
      "round_type": "ATS_RESUME",
      "display_name": "ATS Resume & Skill Matching (Round 1)",
      "raw_score": 88.0,
      "effective_weight": 0.25,
      "weighted_points": 22.0,
      "passed_gate": true,
      "gate_threshold": 50.0,
      "status_note": "PASSED GATE"
    },
    "CONVERSATIONAL_SCREENING": {
      "round_type": "CONVERSATIONAL_SCREENING",
      "display_name": "Conversational Pre-Screening (Round 2)",
      "raw_score": 85.0,
      "effective_weight": 0.30,
      "weighted_points": 25.5,
      "passed_gate": true,
      "gate_threshold": 50.0,
      "status_note": "PASSED GATE"
    },
    "HR_INTERVIEW": {
      "round_type": "HR_INTERVIEW",
      "display_name": "In-Depth HR Interview & Aptitude (Round 3)",
      "raw_score": 90.3,
      "effective_weight": 0.45,
      "weighted_points": 40.64,
      "passed_gate": true,
      "gate_threshold": 55.0,
      "status_note": "PASSED GATE"
    }
  },
  "composite_score": 88.1,
  "hiring_fit": {
    "technical_competence_fit": 90.0,
    "communication_clarity_fit": 87.1,
    "behavioral_culture_fit": 84.6,
    "adaptability_trajectory_fit": 87.7,
    "risk_and_integrity_discount": 0.0,
    "net_hiring_fit_percentage": 87.7,
    "calibrated_percentile": 91.3,
    "fit_summary": "Elite cross-round alignment across technical depth, verbal articulation, and cultural ownership."
  },
  "final_decision": "STRONG_HIRE",
  "readiness_level": "IMMEDIATE_FAST_TRACK",
  "calibrated_role_tier": "Senior / Lead Senior Cloud Platform Architect",
  "executive_verdict": "Exceptional candidate demonstrating elite cross-round mastery (Fit: 87.7%, 91.3th percentile). Immediate fast-track hire recommended.",
  "key_strengths": [
    "Strong keyword skill alignment with job description.",
    "Satisfied baseline communication and role eligibility requirements.",
    "Demonstrated competency in structured problem-solving and situational triage."
  ],
  "developmental_areas": [],
  "safety_gate_passed": true,
  "gate_failure_reasons": [],
  "audit_metadata": {
    "audit_hash": "ZEC-UNIFIED-8C7E29F1A4D0B811",
    "engine_version": "2.0-unified",
    "calibration_standard": "Enterprise Bar Raiser v2.0"
  }
}
```

---

## 4. Recruiter Executive Markdown Format

The `UnifiedScoreObjectFormatter` also renders clean Markdown dossiers suitable for direct consumption by human hiring managers and bar raisers:
- **Header Banner:** Immediate visibility into Candidate Name, Target Role, and Role Track.
- **Verdict Callout:** Final Decision (`STRONG_HIRE`), Net Fit (`87.7%`), Percentile (`91.3th`), and Calibrated Leveling.
- **Scorecard Table:** Visual breakdown of Raw Score, Applied Weight, Weighted Points, and Safety Gate Status for every round.
- **Dimension Table:** 4-axis fit analysis showing Technical, Communication, Behavioral, and Trajectory scores.
- **Audit Verification:** Cryptographic SHA-256 audit hash and gating log ensuring tamper-evident evaluation records.

---

## 5. Security, Traceability & Compliance Guarantees

1. **Cryptographic Immutability:** Each score object embeds an automated SHA-256 hash computed over candidate ID, role, composite score, and timestamp. Any post-hoc score modification invalidates the audit hash.
2. **Explainable AI Compliance:** Every weighted point and risk discount is explicitly itemized, meeting EEOC (Equal Employment Opportunity Commission) and EU AI Act (Article 10) auditability standards.
3. **Automated Persistence:** Master score objects are saved to `data/unified_scores/{candidate_id}_unified_score.json` and `*.md` for automated ingestion into downstream enterprise applicant tracking systems.
