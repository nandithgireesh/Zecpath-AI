"""
Day 55: Security & AI Governance - Cryptographic Audit Trail Engine
===================================================================
Maintains a tamper-evident, sequentially chained audit log of all:
1. Scoring events (raw scores, weighted components, Bayesian smoothing adjustments).
2. Decision events (AI automated classifications, confidence scores, human overrides).
3. Access violations, consent registrations, and data purge lifecycles.
"""

import uuid
from typing import List, Dict, Optional, Tuple, Any
from security_governance_ai.models import (
    UserRole,
    AuditEventType,
    AuditLogEntry
)


class AuditTrailEngine:
    """
    Enterprise Tamper-Evident Audit Trail Subsystem.
    Uses SHA-256 forward-linked cryptographic chaining to detect retroactive log tampering.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self):
        self._ledger: List[AuditLogEntry] = []

    @property
    def total_entries(self) -> int:
        return len(self._ledger)

    def get_latest_hash(self) -> str:
        if not self._ledger:
            return self.GENESIS_HASH
        return self._ledger[-1].entry_hash

    def append_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        actor_role: UserRole,
        candidate_id: str,
        action_details: Dict[str, Any]
    ) -> AuditLogEntry:
        """
        Creates and seals a new chronologically linked audit entry.
        """
        seq = len(self._ledger)
        prev_hash = self.get_latest_hash()

        entry = AuditLogEntry(
            entry_id=f"AUDIT-{seq:06d}-{uuid.uuid4().hex[:8].upper()}",
            sequence_number=seq,
            event_type=event_type,
            actor_id=actor_id,
            actor_role=actor_role,
            candidate_id=candidate_id,
            action_details=action_details,
            previous_entry_hash=prev_hash
        )
        entry.seal_entry()
        self._ledger.append(entry)
        return entry

    def log_score_calculation(
        self,
        candidate_id: str,
        actor_id: str,
        actor_role: UserRole,
        raw_composite_score: float,
        variance_smoothed_score: float,
        coherence_index: float,
        component_breakdown: Dict[str, float]
    ) -> AuditLogEntry:
        """Logs score calculation details for regulatory explainability."""
        details = {
            "action": "SCORING_ARBITRATION",
            "raw_composite_score": round(raw_composite_score, 2),
            "variance_smoothed_score": round(variance_smoothed_score, 2),
            "coherence_index": round(coherence_index, 2),
            "components": component_breakdown
        }
        return self.append_event(
            event_type=AuditEventType.SCORE_CALCULATED,
            actor_id=actor_id,
            actor_role=actor_role,
            candidate_id=candidate_id,
            action_details=details
        )

    def log_decision_finalization(
        self,
        candidate_id: str,
        actor_id: str,
        actor_role: UserRole,
        final_decision: str,
        decision_substatus: str,
        confidence_score: float,
        dynamic_threshold_used: float,
        model_version: str = "OPT-REFINE-DAY54-PROD"
    ) -> AuditLogEntry:
        """Logs irreversible candidate classification decision."""
        details = {
            "action": "DECISION_FINALIZED",
            "decision": final_decision,
            "substatus": decision_substatus,
            "confidence_score": round(confidence_score, 2),
            "dynamic_threshold": round(dynamic_threshold_used, 2),
            "model_version": model_version
        }
        return self.append_event(
            event_type=AuditEventType.DECISION_FINALIZED,
            actor_id=actor_id,
            actor_role=actor_role,
            candidate_id=candidate_id,
            action_details=details
        )

    def log_human_override(
        self,
        candidate_id: str,
        human_evaluator_id: str,
        human_evaluator_role: UserRole,
        original_ai_decision: str,
        overridden_decision: str,
        justification_reason: str
    ) -> AuditLogEntry:
        """Logs human-in-the-loop override per EU AI Act Article 14."""
        details = {
            "action": "HUMAN_OVERRIDE_INTERVENTION",
            "original_ai_decision": original_ai_decision,
            "overridden_decision": overridden_decision,
            "justification": justification_reason,
            "article_14_conforming": True
        }
        return self.append_event(
            event_type=AuditEventType.DECISION_OVERRIDDEN,
            actor_id=human_evaluator_id,
            actor_role=human_evaluator_role,
            candidate_id=candidate_id,
            action_details=details
        )

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Traverses the audit ledger and validates hash links.
        Returns:
            Tuple[is_valid: bool, error_message: Optional[str]]
        """
        if not self._ledger:
            return True, None

        for idx, entry in enumerate(self._ledger):
            # 1. Check sequence number
            if entry.sequence_number != idx:
                return False, f"Sequence discontinuity at index {idx}: expected {idx}, found {entry.sequence_number}"

            # 2. Check previous hash continuity
            expected_prev = self.GENESIS_HASH if idx == 0 else self._ledger[idx - 1].entry_hash
            if entry.previous_entry_hash != expected_prev:
                return False, f"Broken cryptographic chain at index {idx}: previous_hash mismatch."

            # 3. Check internal entry hash integrity
            recomputed = entry.compute_hash()
            if entry.entry_hash != recomputed:
                return False, f"Data tampering detected at index {idx} ({entry.entry_id}): hash corrupted!"

        return True, None

    def get_candidate_audit_history(self, candidate_id: str) -> List[AuditLogEntry]:
        """Retrieves all chronological audit records for a specific candidate."""
        return [entry for entry in self._ledger if entry.candidate_id == candidate_id]
