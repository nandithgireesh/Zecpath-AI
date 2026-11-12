"""
Day 43 Deliverable 1: Ethics Consent Manager
============================================
Implements transparent candidate consent workflows, AEDT disclosures,
biometric audio processing disclosures (NYC Local Law 144, Illinois BIPA, GDPR),
and cryptographic consent receipts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Dict, List, Optional


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    EXPLICIT_OPT_IN = "EXPLICIT_OPT_IN"
    CONDITIONAL_OPT_IN = "CONDITIONAL_OPT_IN"
    OPTED_OUT = "OPTED_OUT"
    REVOKED = "REVOKED"


class DisclosureType(str, Enum):
    AI_EVALUATION = "AI_EVALUATION_DISCLOSURE"
    BIOMETRIC_AUDIO = "BIOMETRIC_AUDIO_DISCLOSURE"
    DATA_RETENTION = "DATA_RETENTION_POLICY_DISCLOSURE"
    HUMAN_OVERSIGHT = "HUMAN_OVERSIGHT_RIGHTS_DISCLOSURE"


@dataclass
class DisclosureNotice:
    disclosure_type: DisclosureType
    title: str
    statutory_basis: str
    summary_text: str
    mandatory: bool = True
    accepted: bool = False


@dataclass
class ConsentRecord:
    candidate_id: str
    candidate_pseudonym: str
    job_requisition_id: str
    status: ConsentStatus
    timestamp_utc: str
    disclosures_acknowledged: List[DisclosureType]
    allow_audio_recording: bool
    allow_ai_scoring: bool
    allow_anonymized_audit: bool
    receipt_hash: str
    human_interviewer_requested: bool = False
    revocation_timestamp: Optional[str] = None
    audit_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "candidate_id": self.candidate_id,
            "candidate_pseudonym": self.candidate_pseudonym,
            "job_requisition_id": self.job_requisition_id,
            "status": self.status.value,
            "timestamp_utc": self.timestamp_utc,
            "disclosures_acknowledged": [d.value for d in self.disclosures_acknowledged],
            "allow_audio_recording": self.allow_audio_recording,
            "allow_ai_scoring": self.allow_ai_scoring,
            "allow_anonymized_audit": self.allow_anonymized_audit,
            "receipt_hash": self.receipt_hash,
            "human_interviewer_requested": self.human_interviewer_requested,
            "revocation_timestamp": self.revocation_timestamp,
            "audit_notes": self.audit_notes,
        }


class EthicsConsentManager:
    """
    Coordinates enterprise consent lifecycle, regulatory disclosures,
    and opt-out human escalation paths for AI-driven interviews.
    """

    def __init__(self):
        self._records: Dict[str, ConsentRecord] = {}

    def get_mandatory_disclosures(self) -> List[DisclosureNotice]:
        """Returns the four mandatory compliance notices required before an AI session."""
        return [
            DisclosureNotice(
                disclosure_type=DisclosureType.AI_EVALUATION,
                title="Automated Employment Decision Tool (AEDT) Notice",
                statutory_basis="NYC Local Law 144 / EU AI Act Art. 52",
                summary_text=(
                    "This interview utilizes automated natural language analysis to assess semantic relevance, "
                    "communication clarity, and technical consistency. All AI metrics are subject to human reviewer oversight."
                ),
                mandatory=True,
            ),
            DisclosureNotice(
                disclosure_type=DisclosureType.BIOMETRIC_AUDIO,
                title="Acoustic & Voice Processing Disclosure",
                statutory_basis="Illinois BIPA (740 ILCS 14/) / GDPR Art. 9",
                summary_text=(
                    "Acoustic speech signals are processed in real-time to transcribe text and analyze speech latency. "
                    "Voice prints, voice biometric identification, or emotional lie detection are strictly prohibited and never performed."
                ),
                mandatory=True,
            ),
            DisclosureNotice(
                disclosure_type=DisclosureType.DATA_RETENTION,
                title="Data Retention & Purpose Limitation Notice",
                statutory_basis="GDPR Art. 5(1)(e) & Art. 17 / EEOC Recordkeeping 29 CFR § 1602",
                summary_text=(
                    "Audio recordings are permanently shredded after 14 days. Transcripts are pseudonymized after 90 days. "
                    "Evaluation scoring dossiers are retained for 365 days for regulatory audit compliance, after which they are purged."
                ),
                mandatory=True,
            ),
            DisclosureNotice(
                disclosure_type=DisclosureType.HUMAN_OVERSIGHT,
                title="Right to Human Review & Alternative Accommodations",
                statutory_basis="EU AI Act Art. 14 / EEOC Reasonable Accommodation Guidance",
                summary_text=(
                    "Candidates may request an alternative human-conducted interview at any time without penalty or prejudice. "
                    "Final hiring decisions are exclusively made by certified human bar raisers."
                ),
                mandatory=True,
            ),
        ]

    def register_consent(
        self,
        candidate_id: str,
        job_requisition_id: str,
        acknowledged_disclosures: List[DisclosureType],
        allow_audio_recording: bool = True,
        allow_ai_scoring: bool = True,
        allow_anonymized_audit: bool = True,
        request_human_interviewer: bool = False,
    ) -> ConsentRecord:
        """
        Processes candidate consent declarations, validates mandatory disclosures,
        and generates a verifiable cryptographic receipt.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        pseudonym = f"PSEUDO-{hashlib.sha256(candidate_id.encode()).hexdigest()[:10].upper()}"

        mandatory_types = {
            DisclosureType.AI_EVALUATION,
            DisclosureType.BIOMETRIC_AUDIO,
            DisclosureType.DATA_RETENTION,
            DisclosureType.HUMAN_OVERSIGHT,
        }
        acknowledged_set = set(acknowledged_disclosures)

        # Determine status
        if request_human_interviewer or not allow_ai_scoring:
            status = ConsentStatus.OPTED_OUT
            notes = ["Candidate opted out of AI scoring. Routed to Human Bar Raiser pipeline."]
        elif mandatory_types.issubset(acknowledged_set) and allow_audio_recording and allow_ai_scoring:
            status = ConsentStatus.EXPLICIT_OPT_IN
            notes = ["Full explicit opt-in granted. All statutory disclosures acknowledged."]
        else:
            status = ConsentStatus.CONDITIONAL_OPT_IN
            notes = ["Conditional consent granted. Partial restrictions applied."]

        # Cryptographic receipt
        receipt_raw = f"{candidate_id}:{job_requisition_id}:{status.value}:{now_str}:{allow_audio_recording}:{allow_ai_scoring}"
        receipt_hash = hashlib.sha256(receipt_raw.encode()).hexdigest()

        record = ConsentRecord(
            candidate_id=candidate_id,
            candidate_pseudonym=pseudonym,
            job_requisition_id=job_requisition_id,
            status=status,
            timestamp_utc=now_str,
            disclosures_acknowledged=acknowledged_disclosures,
            allow_audio_recording=allow_audio_recording,
            allow_ai_scoring=allow_ai_scoring,
            allow_anonymized_audit=allow_anonymized_audit,
            receipt_hash=receipt_hash,
            human_interviewer_requested=request_human_interviewer,
            audit_notes=notes,
        )

        self._records[candidate_id] = record
        return record

    def revoke_consent(self, candidate_id: str, reason: str = "Candidate requested revocation") -> Optional[ConsentRecord]:
        """
        Processes real-time consent revocation, freezing AI scoring and initiating human fallback.
        """
        if candidate_id not in self._records:
            return None

        record = self._records[candidate_id]
        record.status = ConsentStatus.REVOKED
        record.revocation_timestamp = datetime.now(timezone.utc).isoformat()
        record.allow_ai_scoring = False
        record.allow_audio_recording = False
        record.human_interviewer_requested = True
        record.audit_notes.append(f"Consent revoked at {record.revocation_timestamp}: {reason}")
        return record

    def get_record(self, candidate_id: str) -> Optional[ConsentRecord]:
        return self._records.get(candidate_id)

    def is_session_authorized(self, candidate_id: str) -> bool:
        """Checks whether the candidate is authorized for automated AI evaluation."""
        rec = self.get_record(candidate_id)
        if not rec:
            return False
        return rec.status in (ConsentStatus.EXPLICIT_OPT_IN, ConsentStatus.CONDITIONAL_OPT_IN) and rec.allow_ai_scoring
