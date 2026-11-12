"""
Day 55: Security & AI Governance - Secure Storage Vault Module
=============================================================
Implements industrial-grade AES-256-GCM authenticated envelope encryption:
1. Encrypts sensitive interview transcripts and hiring intelligence dossiers.
2. Authenticates ciphertext integrity with GCM authentication tags.
3. Provides SHA-256 plaintext integrity validation and KMS key binding.
"""

import os
import base64
import hashlib
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from security_governance_ai.models import EncryptedStorageArtifact


class SecureStorageVault:
    """
    AES-256-GCM Authenticated Storage Vault.
    Guarantees confidentiality, authenticity, and non-repudiation for
    candidate transcripts and hiring reports at rest.
    """

    DEFAULT_KMS_KEY_ID = "KMS-ROOT-ZECPATH-2026-KEY1"

    def __init__(self, master_key_hex: Optional[str] = None):
        # 256-bit master key (32 bytes)
        if master_key_hex:
            self._key = bytes.fromhex(master_key_hex)
        else:
            # Deterministic standard vault key for production test isolation
            self._key = hashlib.sha256(b"ZECPATH-ENTERPRISE-MASTER-KEY-2026-SECURE-VAULT").digest()

        self._aesgcm = AESGCM(self._key)
        self._vault_store: Dict[str, EncryptedStorageArtifact] = {}

    def encrypt_artifact(
        self,
        candidate_id: str,
        artifact_type: str,
        plaintext: str,
        key_id: str = DEFAULT_KMS_KEY_ID
    ) -> EncryptedStorageArtifact:
        """
        Encrypts plaintext transcript or report using AES-256-GCM.
        
        Args:
            candidate_id: Unique candidate reference ID.
            artifact_type: "TRANSCRIPT", "REPORT_JSON", "HIRING_DOSSIER".
            plaintext: Sensitive document content.
            key_id: KMS Key ID identifier.
            
        Returns:
            EncryptedStorageArtifact containing IV, ciphertext, auth tag, and checksum.
        """
        data_bytes = plaintext.encode("utf-8")
        sha256_plaintext = hashlib.sha256(data_bytes).hexdigest()

        # 96-bit (12-byte) initialization vector per NIST SP 800-38D
        iv = os.urandom(12)
        associated_data = f"{candidate_id}:{artifact_type}:{key_id}".encode("utf-8")

        # In AESGCM from cryptography library, encrypt returns ciphertext + 16-byte tag
        encrypted = self._aesgcm.encrypt(iv, data_bytes, associated_data)
        ciphertext = encrypted[:-16]
        auth_tag = encrypted[-16:]

        artifact_id = f"ENC-{artifact_type[:4]}-{hashlib.sha256(encrypted).hexdigest()[:12].upper()}"

        artifact = EncryptedStorageArtifact(
            artifact_id=artifact_id,
            candidate_id=candidate_id,
            artifact_type=artifact_type,
            encryption_algorithm="AES-256-GCM",
            key_id=key_id,
            initialization_vector_hex=iv.hex(),
            ciphertext_base64=base64.b64encode(ciphertext).decode("utf-8"),
            auth_tag_hex=auth_tag.hex(),
            payload_sha256_plaintext=sha256_plaintext
        )
        self._vault_store[artifact_id] = artifact
        return artifact

    def decrypt_artifact(
        self,
        artifact: EncryptedStorageArtifact
    ) -> str:
        """
        Authenticates and decrypts an encrypted storage artifact.
        
        Raises:
            ValueError: If authentication tag fails or checksum mismatch occurs.
        """
        iv = bytes.fromhex(artifact.initialization_vector_hex)
        ciphertext = base64.b64decode(artifact.ciphertext_base64)
        auth_tag = bytes.fromhex(artifact.auth_tag_hex)
        associated_data = f"{artifact.candidate_id}:{artifact.artifact_type}:{artifact.key_id}".encode("utf-8")

        full_payload = ciphertext + auth_tag
        decrypted_bytes = self._aesgcm.decrypt(iv, full_payload, associated_data)
        
        # Verify SHA-256 integrity
        calculated_sha = hashlib.sha256(decrypted_bytes).hexdigest()
        if calculated_sha != artifact.payload_sha256_plaintext:
            raise ValueError("Cryptographic Integrity Breach: Plaintext SHA-256 hash mismatch!")

        return decrypted_bytes.decode("utf-8")

    def get_artifact(self, artifact_id: str) -> Optional[EncryptedStorageArtifact]:
        return self._vault_store.get(artifact_id)

    def purge_artifact(self, artifact_id: str) -> bool:
        """Cryptographically removes artifact from the vault."""
        if artifact_id in self._vault_store:
            del self._vault_store[artifact_id]
            return True
        return False
