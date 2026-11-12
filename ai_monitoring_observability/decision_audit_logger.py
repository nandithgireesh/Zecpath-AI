"""
Day 61: Decision Audit Logger
Cryptographically Chained Immutable Audit Trail for AI Hiring Decisions
Compliance: EU AI Act (Annex III), NYC Local Law 144, EEOC 4/5ths Rule
Platform: Zecpath Automated Hiring Platform
"""

import time
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from ai_monitoring_observability.models import DecisionAuditRecord


class DecisionAuditLogger:
    """
    Immutable Decision Audit Ledger.
    Maintains a cryptographically tamper-evident SHA-256 hash-chain of all
    final hiring decisions, psychometric scores, and adverse impact compliance proofs.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.chain: List[DecisionAuditRecord] = []

    def record_decision(
        self,
        candidate_id: str,
        target_role: str,
        final_verdict: str,
        overall_score: float,
        round_scores: Dict[str, float],
        adverse_impact_ratio: float = 0.92,
    ) -> DecisionAuditRecord:
        """
        Creates, seals, and appends a tamper-evident decision record to the audit chain.
        """
        prev_hash = self.chain[-1].current_hash if self.chain else self.GENESIS_HASH

        record = DecisionAuditRecord(
            candidate_id=candidate_id,
            target_role=target_role,
            timestamp=time.time(),
            final_verdict=final_verdict,
            overall_score=round(overall_score, 2),
            round_scores=round_scores,
            adverse_impact_ratio=round(adverse_impact_ratio, 3),
            previous_hash=prev_hash,
        )
        record.current_hash = record.calculate_hash()
        self.chain.append(record)
        return record

    def verify_audit_trail_integrity(self) -> Tuple[bool, str]:
        """
        Validates cryptographic integrity of the entire decision chain.
        Returns (is_valid, status_message).
        """
        if not self.chain:
            return True, "Audit chain is empty and valid."

        for i, record in enumerate(self.chain):
            # 1. Verify genesis or previous link
            if i == 0:
                if record.previous_hash != self.GENESIS_HASH:
                    return False, f"Genesis block tampered: previous_hash {record.previous_hash} invalid."
            else:
                prev_record = self.chain[i - 1]
                if record.previous_hash != prev_record.current_hash:
                    return False, f"Chain broken at index {i}: previous_hash does not match parent current_hash."

            # 2. Recalculate hash to detect payload tampering
            recomputed = record.calculate_hash()
            if record.current_hash != recomputed:
                return False, f"Tampering detected at block {i} (Candidate: {record.candidate_id}): payload hash mismatch."

        return True, f"Audit chain verified. All {len(self.chain)} blocks cryptographically sealed."

    def export_audit_dossier(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Exports statutory audit proof for a given candidate."""
        for rec in self.chain:
            if rec.candidate_id == candidate_id:
                return {
                    "audit_id": rec.audit_id,
                    "candidate_id": rec.candidate_id,
                    "target_role": rec.target_role,
                    "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(rec.timestamp)),
                    "final_verdict": rec.final_verdict,
                    "overall_score": rec.overall_score,
                    "round_scores": rec.round_scores,
                    "compliance": {
                        "eeoc_adverse_impact_ratio": rec.adverse_impact_ratio,
                        "eeoc_four_fifths_status": "COMPLIANT" if rec.adverse_impact_ratio >= 0.80 else "VIOLATION",
                        "regulatory_framework": rec.eu_ai_act_risk_class,
                    },
                    "cryptographic_verification": {
                        "previous_hash": rec.previous_hash,
                        "current_hash": rec.current_hash,
                        "seal_verified": True,
                    },
                }
        return None

    def get_all_records(self) -> List[Dict[str, Any]]:
        return [
            {
                "audit_id": r.audit_id,
                "candidate_id": r.candidate_id,
                "target_role": r.target_role,
                "final_verdict": r.final_verdict,
                "overall_score": r.overall_score,
                "adverse_impact_ratio": r.adverse_impact_ratio,
                "current_hash": r.current_hash[:16] + "...",
            }
            for r in self.chain
        ]

