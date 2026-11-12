"""
Day 55: Security & AI Governance - Comprehensive Test Suite
===========================================================
16 Unit and Integration Tests covering:
- Chained audit trail logging for scores and decisions
- Forward cryptographic SHA-256 hash chaining and tamper detection
- AES-256-GCM authenticated storage encryption and decryption
- Role-Based Access Control (RBAC) permission boundaries
- Attribute-Based Access Control (ABAC) contextual policy enforcement
- Consent registration, verification, and revocation lifecycle
- Data retention tiering (Active, Dispute, Statutory, Purge)
- Automated PII redaction and de-identification
- GDPR Article 17 Erasure and Certificate of Destruction
"""

import unittest
from security_governance_ai.models import (
    UserRole,
    Permission,
    AccessContext,
    ConsentScope,
    ConsentStatus,
    RetentionTier,
    RetentionPolicy,
    CertificateOfDestruction
)
from security_governance_ai.audit_trail_engine import AuditTrailEngine
from security_governance_ai.secure_storage_vault import SecureStorageVault
from security_governance_ai.access_control_manager import AccessControlManager
from security_governance_ai.consent_and_privacy_manager import ConsentAndPrivacyManager


class TestDay55SecurityGovernance(unittest.TestCase):

    def setUp(self):
        self.audit_engine = AuditTrailEngine()
        self.vault = SecureStorageVault()
        self.access_manager = AccessControlManager()
        self.privacy_manager = ConsentAndPrivacyManager()

    def test_01_models_and_cryptographic_seals(self):
        """Verifies deterministic SHA-256 seal generation on certificate of destruction."""
        cert = CertificateOfDestruction(
            certificate_id="CERT-TEST-001",
            candidate_id="CAN-101",
            requested_by="user@zecser.com",
            compliance_officer_id="OFFICER-007",
            purged_artifacts=["transcript.json", "audio.wav"]
        )
        cert.seal_certificate()
        self.assertEqual(len(cert.sha256_audit_seal), 64)
        saved_hash = cert.sha256_audit_seal
        cert.seal_certificate()
        self.assertEqual(cert.sha256_audit_seal, saved_hash)

    def test_02_audit_trail_score_logging(self):
        """Verifies score calculation event logging in audit trail."""
        entry = self.audit_engine.log_score_calculation(
            candidate_id="CAN-PRIYA-001",
            actor_id="SCORING-ENGINE-V1",
            actor_role=UserRole.SUPER_ADMIN,
            raw_composite_score=89.88,
            variance_smoothed_score=90.55,
            coherence_index=94.02,
            component_breakdown={"ATS": 92.0, "Tech": 91.0, "HR": 88.0}
        )
        self.assertEqual(entry.sequence_number, 0)
        self.assertEqual(entry.previous_entry_hash, "0" * 64)
        self.assertEqual(len(entry.entry_hash), 64)
        self.assertEqual(self.audit_engine.total_entries, 1)

    def test_03_audit_trail_decision_logging(self):
        """Verifies decision finalization logging in audit trail."""
        entry = self.audit_engine.log_decision_finalization(
            candidate_id="CAN-PRIYA-001",
            actor_id="ARBITRATION-SERVICE",
            actor_role=UserRole.SUPER_ADMIN,
            final_decision="SELECTED",
            decision_substatus="SELECTED_DEFINITIVE",
            confidence_score=99.0,
            dynamic_threshold_used=83.50
        )
        self.assertEqual(entry.action_details["decision"], "SELECTED")
        self.assertEqual(entry.action_details["substatus"], "SELECTED_DEFINITIVE")

    def test_04_audit_trail_chain_integrity_valid(self):
        """Verifies chain integrity across multiple sequential logs."""
        self.audit_engine.log_score_calculation(
            candidate_id="CAN-1", actor_id="EVAL", actor_role=UserRole.SUPER_ADMIN,
            raw_composite_score=85.0, variance_smoothed_score=86.0, coherence_index=92.0, component_breakdown={}
        )
        self.audit_engine.log_decision_finalization(
            candidate_id="CAN-1", actor_id="EVAL", actor_role=UserRole.SUPER_ADMIN,
            final_decision="SELECTED", decision_substatus="SELECTED_DEFINITIVE",
            confidence_score=95.0, dynamic_threshold_used=82.0
        )
        is_valid, err = self.audit_engine.verify_chain_integrity()
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_05_audit_trail_tamper_detection(self):
        """Verifies tampering with an audit entry breaks the cryptographic chain."""
        self.audit_engine.log_score_calculation(
            candidate_id="CAN-1", actor_id="EVAL", actor_role=UserRole.SUPER_ADMIN,
            raw_composite_score=85.0, variance_smoothed_score=86.0, coherence_index=92.0, component_breakdown={}
        )
        self.audit_engine.log_decision_finalization(
            candidate_id="CAN-1", actor_id="EVAL", actor_role=UserRole.SUPER_ADMIN,
            final_decision="HOLD_REVIEW", decision_substatus="HOLD_SECONDARY",
            confidence_score=80.0, dynamic_threshold_used=82.0
        )

        # Adversary attempts to retroactively change decision to SELECTED without recomputing hash
        self.audit_engine._ledger[1].action_details["decision"] = "SELECTED"

        is_valid, err = self.audit_engine.verify_chain_integrity()
        self.assertFalse(is_valid)
        self.assertIn("tampering detected", err.lower())

    def test_06_human_override_logging(self):
        """Verifies EU AI Act Art. 14 Human-in-the-loop override logging."""
        entry = self.audit_engine.log_human_override(
            candidate_id="CAN-202",
            human_evaluator_id="MGR-JOHN-DOE",
            human_evaluator_role=UserRole.HIRING_MANAGER,
            original_ai_decision="HOLD_REVIEW",
            overridden_decision="SELECTED",
            justification_reason="Candidate showed exceptional open-source kernel contributions."
        )
        self.assertEqual(entry.action_details["action"], "HUMAN_OVERRIDE_INTERVENTION")
        self.assertTrue(entry.action_details["article_14_conforming"])

    def test_07_aes256_encryption_decryption_roundtrip(self):
        """Verifies AES-256-GCM encryption and authenticated decryption roundtrip."""
        secret_transcript = "Candidate explained distributed Raft consensus and log compaction."
        artifact = self.vault.encrypt_artifact(
            candidate_id="CAN-PRIYA-001",
            artifact_type="TRANSCRIPT",
            plaintext=secret_transcript
        )
        self.assertTrue(len(artifact.ciphertext_base64) > 10)
        self.assertEqual(artifact.encryption_algorithm, "AES-256-GCM")
        self.assertEqual(len(artifact.initialization_vector_hex), 24)  # 12 bytes = 24 hex chars
        self.assertEqual(len(artifact.auth_tag_hex), 32)              # 16 bytes = 32 hex chars

        decrypted = self.vault.decrypt_artifact(artifact)
        self.assertEqual(decrypted, secret_transcript)

    def test_08_aes256_ciphertext_tampering_rejected(self):
        """Verifies GCM auth tag rejects modified ciphertext."""
        artifact = self.vault.encrypt_artifact(
            candidate_id="CAN-101",
            artifact_type="REPORT_JSON",
            plaintext="Confidential hiring recommendation report"
        )
        # Corrupt auth tag
        corrupted_tag = "0" * 32
        artifact.auth_tag_hex = corrupted_tag

        with self.assertRaises(Exception):
            self.vault.decrypt_artifact(artifact)

    def test_09_rbac_permissions_super_admin(self):
        """Verifies SUPER_ADMIN possesses all permissions."""
        ctx = AccessContext(
            user_id="ADMIN-1",
            user_role=UserRole.SUPER_ADMIN,
            organization_id="ZECSER-HQ",
            department="EXECUTIVE"
        )
        for perm in Permission:
            allowed, _ = self.access_manager.authorize(ctx, perm)
            self.assertTrue(allowed)

    def test_10_rbac_permissions_recruiter_restricted(self):
        """Verifies RECRUITER cannot override AI decisions or execute data purges."""
        ctx = AccessContext(
            user_id="REC-1",
            user_role=UserRole.RECRUITER,
            organization_id="ZECSER-HQ",
            department="TALENT_ACQUISITION"
        )
        # Allowed
        allowed, _ = self.access_manager.authorize(ctx, Permission.VIEW_AGGREGATED_SCORES)
        self.assertTrue(allowed)
        # Denied
        allowed_override, reason = self.access_manager.authorize(ctx, Permission.OVERRIDE_AI_DECISION)
        self.assertFalse(allowed_override)
        self.assertIn("RBAC_DENIED", reason)

        allowed_purge, _ = self.access_manager.authorize(ctx, Permission.EXECUTE_DATA_PURGE)
        self.assertFalse(allowed_purge)

    def test_11_abac_interviewer_assignment_enforcement(self):
        """Verifies technical interviewer cannot access candidates they were not assigned to."""
        ctx = AccessContext(
            user_id="INT-ALICE",
            user_role=UserRole.TECHNICAL_INTERVIEWER,
            organization_id="ZECSER-HQ",
            department="ENGINEERING",
            assigned_candidate_ids=["CAN-ALICE-1", "CAN-ALICE-2"]
        )
        # Assigned candidate
        allowed, _ = self.access_manager.authorize(
            ctx, Permission.VIEW_RAW_TRANSCRIPTS, target_candidate_id="CAN-ALICE-1"
        )
        self.assertTrue(allowed)

        # Unassigned candidate
        denied, reason = self.access_manager.authorize(
            ctx, Permission.VIEW_RAW_TRANSCRIPTS, target_candidate_id="CAN-BOB-99"
        )
        self.assertFalse(denied)
        self.assertIn("ABAC_DENIED", reason)

    def test_12_abac_candidate_self_access(self):
        """Verifies candidate data subject can only access their own records."""
        ctx = AccessContext(
            user_id="CAND-PRIYA",
            user_role=UserRole.CANDIDATE_DATA_SUBJECT,
            organization_id="PUBLIC",
            department="APPLICANT",
            assigned_candidate_ids=["CAND-PRIYA"]
        )
        # Own record
        allowed, _ = self.access_manager.authorize(
            ctx, Permission.VIEW_AGGREGATED_SCORES, target_candidate_id="CAND-PRIYA"
        )
        self.assertTrue(allowed)

        # Other candidate's record
        denied, _ = self.access_manager.authorize(
            ctx, Permission.VIEW_AGGREGATED_SCORES, target_candidate_id="CAND-OTHER"
        )
        self.assertFalse(denied)

    def test_13_consent_registration_and_revocation(self):
        """Verifies consent lifecycle management."""
        c_id = "CAN-CONSENT-1"
        records = self.privacy_manager.register_consent(
            candidate_id=c_id,
            scopes=[ConsentScope.AI_ASSESSMENT, ConsentScope.VOICE_TELEMETRY]
        )
        self.assertEqual(len(records), 2)
        self.assertTrue(self.privacy_manager.has_active_consent(c_id, ConsentScope.AI_ASSESSMENT))

        # Revoke voice telemetry
        revoked = self.privacy_manager.revoke_consent(c_id, ConsentScope.VOICE_TELEMETRY)
        self.assertEqual(revoked.status, ConsentStatus.REVOKED)
        self.assertFalse(self.privacy_manager.has_active_consent(c_id, ConsentScope.VOICE_TELEMETRY))
        # AI assessment remains granted
        self.assertTrue(self.privacy_manager.has_active_consent(c_id, ConsentScope.AI_ASSESSMENT))

    def test_14_retention_tier_classification(self):
        """Verifies legal retention tiering based on days elapsed."""
        self.assertEqual(self.privacy_manager.classify_retention_tier(15), RetentionTier.ACTIVE_ASSESSMENT)
        self.assertEqual(self.privacy_manager.classify_retention_tier(60), RetentionTier.DISPUTE_WINDOW)
        self.assertEqual(self.privacy_manager.classify_retention_tier(365), RetentionTier.STATUTORY_AUDIT)
        self.assertEqual(self.privacy_manager.classify_retention_tier(800), RetentionTier.PURGE_ELIGIBLE)

    def test_15_automated_pii_redaction(self):
        """Verifies de-identification of emails, phone numbers, and candidate names."""
        raw_text = "Contact Priya Sharma at priya.sharma@example.com or +1 (555) 019-2834 regarding SSN 000-12-3456."
        redacted = self.privacy_manager.redact_pii(raw_text, candidate_name="Priya Sharma")
        self.assertNotIn("priya.sharma@example.com", redacted)
        self.assertNotIn("(555) 019-2834", redacted)
        self.assertNotIn("000-12-3456", redacted)
        self.assertNotIn("Priya", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertIn("[REDACTED_GOV_ID]", redacted)

    def test_16_gdpr_erasure_certificate_generation(self):
        """Verifies Certificate of Destruction issuance and consent revocation upon erasure."""
        c_id = "CAN-GDPR-ERASE"
        self.privacy_manager.register_consent(c_id, [ConsentScope.AI_ASSESSMENT])

        cert = self.privacy_manager.execute_gdpr_erasure(
            candidate_id=c_id,
            requested_by="legal@applicant.org",
            compliance_officer_id="DPO-OFFICER-1",
            artifact_list=["dossier.pdf", "raw_audio.wav", "vector_embeddings.bin"]
        )
        self.assertTrue(cert.certificate_id.startswith("CERT-DESTRUCT-"))
        self.assertEqual(len(cert.sha256_audit_seal), 64)
        # Consents revoked
        self.assertFalse(self.privacy_manager.has_active_consent(c_id, ConsentScope.AI_ASSESSMENT))


if __name__ == "__main__":
    unittest.main()
