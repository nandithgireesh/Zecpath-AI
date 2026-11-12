"""
Day 55: Security & AI Governance - Domain Models
================================================
Enterprise data structures and schemas for:
- Role-Based Access Control (RBAC) & Attribute-Based Access Control (ABAC)
- Consent Lifecycle Management & GDPR Privacy Scope
- Cryptographic Audit Trail Chaining (Score & Decision Logs)
- AES-256-GCM Secure Storage & Integrity Seals
- Data Retention Policies & Certificates of Destruction
"""

import json
import hashlib
from enum import Enum
from typing import List, Dict, Optional, Set, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# ==============================================================================
# 1. ACCESS CONTROL ENUMS & RBAC/ABAC SCHEMAS
# ==============================================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    COMPLIANCE_AUDITOR = "COMPLIANCE_AUDITOR"
    HIRING_MANAGER = "HIRING_MANAGER"
    RECRUITER = "RECRUITER"
    TECHNICAL_INTERVIEWER = "TECHNICAL_INTERVIEWER"
    CANDIDATE_DATA_SUBJECT = "CANDIDATE_DATA_SUBJECT"


class Permission(str, Enum):
    VIEW_CANDIDATE_PII = "VIEW_CANDIDATE_PII"
    VIEW_AGGREGATED_SCORES = "VIEW_AGGREGATED_SCORES"
    VIEW_RAW_TRANSCRIPTS = "VIEW_RAW_TRANSCRIPTS"
    MODIFY_SCORING_WEIGHTS = "MODIFY_SCORING_WEIGHTS"
    OVERRIDE_AI_DECISION = "OVERRIDE_AI_DECISION"
    EXPORT_AUDIT_LOGS = "EXPORT_AUDIT_LOGS"
    EXECUTE_DATA_PURGE = "EXECUTE_DATA_PURGE"
    VIEW_COMPLIANCE_REPORTS = "VIEW_COMPLIANCE_REPORTS"


class AccessContext(BaseModel):
    """Contextual metadata passed during ABAC policy arbitration."""
    user_id: str
    user_role: UserRole
    organization_id: str
    department: str
    assigned_candidate_ids: List[str] = Field(default_factory=list)
    client_ip: str = "127.0.0.1"
    request_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# 2. CONSENT & PRIVACY MANAGEMENT SCHEMAS
# ==============================================================================

class ConsentScope(str, Enum):
    AI_ASSESSMENT = "AI_ASSESSMENT"
    VOICE_TELEMETRY = "VOICE_TELEMETRY"
    CODE_SANDBOX_EVAL = "CODE_SANDBOX_EVAL"
    BENCHMARK_ANONYMIZATION = "BENCHMARK_ANONYMIZATION"
    THIRD_PARTY_ATS_SYNC = "THIRD_PARTY_ATS_SYNC"


class ConsentStatus(str, Enum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class ConsentRecord(BaseModel):
    """Explicit candidate consent agreement for multi-modal AI evaluation."""
    candidate_id: str
    consent_id: str
    scope: ConsentScope
    status: ConsentStatus = ConsentStatus.GRANTED
    timestamp_granted: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revocation_timestamp: Optional[str] = None
    terms_version: str = "v2.4-2026"
    ip_address_hash: str = ""


# ==============================================================================
# 3. CRYPTOGRAPHIC AUDIT TRAIL LOG MODELS
# ==============================================================================

class AuditEventType(str, Enum):
    SCORE_CALCULATED = "SCORE_CALCULATED"
    DECISION_FINALIZED = "DECISION_FINALIZED"
    DECISION_OVERRIDDEN = "DECISION_OVERRIDDEN"
    CONSENT_REGISTERED = "CONSENT_REGISTERED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    TRANSCRIPT_ENCRYPTED = "TRANSCRIPT_ENCRYPTED"
    DATA_PURGED = "DATA_PURGED"
    ACCESS_VIOLATION = "ACCESS_VIOLATION"


class AuditLogEntry(BaseModel):
    """
    Immutable audit record chained cryptographically to the preceding entry
    via SHA-256 hash chaining (Merkle-ordered ledger).
    """
    entry_id: str
    sequence_number: int = Field(..., ge=0)
    event_type: AuditEventType
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor_id: str
    actor_role: UserRole
    candidate_id: str
    action_details: Dict[str, Any]
    previous_entry_hash: str = Field(..., description="Hash of sequence N-1 (Genesis = 64 zeros)")
    entry_hash: str = ""

    def compute_hash(self) -> str:
        payload = {
            "entry_id": self.entry_id,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type.value,
            "timestamp_utc": self.timestamp_utc,
            "actor_id": self.actor_id,
            "actor_role": self.actor_role.value,
            "candidate_id": self.candidate_id,
            "action_details": self.action_details,
            "previous_hash": self.previous_entry_hash,
        }
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def seal_entry(self) -> None:
        self.entry_hash = self.compute_hash()


# ==============================================================================
# 4. SECURE STORAGE & ENCRYPTION SCHEMAS
# ==============================================================================

class EncryptedStorageArtifact(BaseModel):
    """Represents an AES-256-GCM encrypted transcript or dossier file."""
    artifact_id: str
    candidate_id: str
    artifact_type: str = Field(..., description="TRANSCRIPT, REPORT_JSON, AUDIO_VECTOR")
    encryption_algorithm: str = "AES-256-GCM"
    key_id: str = "KMS-ROOT-ZECPATH-2026-KEY1"
    initialization_vector_hex: str
    ciphertext_base64: str
    auth_tag_hex: str
    payload_sha256_plaintext: str
    encrypted_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# 5. DATA RETENTION & CERTIFICATE OF DESTRUCTION
# ==============================================================================

class RetentionTier(str, Enum):
    ACTIVE_ASSESSMENT = "ACTIVE_ASSESSMENT"      # 0 to 30 days: full multi-modal telemetry
    DISPUTE_WINDOW = "DISPUTE_WINDOW"            # 30 to 180 days: anonymized dossier & scores
    STATUTORY_AUDIT = "STATUTORY_AUDIT"          # 180 to 730 days (2 yrs): compliance hash & audit trail
    PURGE_ELIGIBLE = "PURGE_ELIGIBLE"            # > 730 days: cryptographically destroyed


class RetentionPolicy(BaseModel):
    policy_id: str = "POL-DATA-RETENTION-2026"
    active_assessment_days: int = 30
    dispute_window_days: int = 180
    statutory_audit_days: int = 730
    auto_redaction_enabled: bool = True
    enforce_erasure_guarantee: bool = True


class CertificateOfDestruction(BaseModel):
    """Legally defensible cryptographic proof of candidate data erasure under GDPR/EEOC."""
    certificate_id: str
    candidate_id: str
    erasure_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    requested_by: str
    compliance_officer_id: str
    purged_artifacts: List[str]
    method: str = "NIST_SP_800_88_CRYPTOGRAPHIC_ERASURE"
    sha256_audit_seal: str = ""

    def seal_certificate(self) -> None:
        payload = {
            "cert_id": self.certificate_id,
            "candidate_id": self.candidate_id,
            "timestamp": self.erasure_timestamp_utc,
            "purged": self.purged_artifacts,
            "method": self.method
        }
        self.sha256_audit_seal = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
