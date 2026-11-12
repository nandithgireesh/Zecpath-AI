"""
Day 55: Security & AI Governance - Access Control Manager Module
================================================================
Implements dual-layer authorization:
1. Role-Based Access Control (RBAC) - Granular role-to-permission mapping.
2. Attribute-Based Access Control (ABAC) - Contextual policies (candidate assignment,
   department scoping, active consent state).
"""

from typing import Dict, Set, Tuple, Optional, List
from security_governance_ai.models import (
    UserRole,
    Permission,
    AccessContext
)


class AccessControlManager:
    """
    Enterprise Authorization Decision Point (PDP / PEP).
    Enforces least-privilege security across candidate dossiers and model weights.
    """

    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.SUPER_ADMIN: {
            Permission.VIEW_CANDIDATE_PII,
            Permission.VIEW_AGGREGATED_SCORES,
            Permission.VIEW_RAW_TRANSCRIPTS,
            Permission.MODIFY_SCORING_WEIGHTS,
            Permission.OVERRIDE_AI_DECISION,
            Permission.EXPORT_AUDIT_LOGS,
            Permission.EXECUTE_DATA_PURGE,
            Permission.VIEW_COMPLIANCE_REPORTS,
        },
        UserRole.COMPLIANCE_AUDITOR: {
            Permission.VIEW_AGGREGATED_SCORES,
            Permission.EXPORT_AUDIT_LOGS,
            Permission.VIEW_COMPLIANCE_REPORTS,
        },
        UserRole.HIRING_MANAGER: {
            Permission.VIEW_CANDIDATE_PII,
            Permission.VIEW_AGGREGATED_SCORES,
            Permission.VIEW_RAW_TRANSCRIPTS,
            Permission.OVERRIDE_AI_DECISION,
            Permission.VIEW_COMPLIANCE_REPORTS,
        },
        UserRole.RECRUITER: {
            Permission.VIEW_CANDIDATE_PII,
            Permission.VIEW_AGGREGATED_SCORES,
        },
        UserRole.TECHNICAL_INTERVIEWER: {
            Permission.VIEW_RAW_TRANSCRIPTS,
            Permission.VIEW_AGGREGATED_SCORES,
        },
        UserRole.CANDIDATE_DATA_SUBJECT: {
            Permission.VIEW_AGGREGATED_SCORES,
        }
    }

    def __init__(self, custom_role_permissions: Optional[Dict[UserRole, Set[Permission]]] = None):
        self.role_permissions = custom_role_permissions or self.ROLE_PERMISSIONS

    def has_role_permission(self, role: UserRole, permission: Permission) -> bool:
        """Evaluates pure RBAC permission membership."""
        allowed = self.role_permissions.get(role, set())
        return permission in allowed

    def authorize(
        self,
        context: AccessContext,
        required_permission: Permission,
        target_candidate_id: Optional[str] = None,
        target_department: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Unified RBAC + ABAC Authorization Gate.
        
        Returns:
            Tuple[is_allowed: bool, reason_message: str]
        """
        # 1. RBAC Check
        if not self.has_role_permission(context.user_role, required_permission):
            return (
                False,
                f"RBAC_DENIED: Role '{context.user_role.value}' lacks permission '{required_permission.value}'."
            )

        # 2. ABAC Rule: Super Admin bypasses contextual constraints
        if context.user_role == UserRole.SUPER_ADMIN:
            return True, "AUTHORIZED_SUPER_ADMIN_OVERRIDE"

        # 3. ABAC Rule: Candidate Data Subject can ONLY view their own records (GDPR Art 15)
        if context.user_role == UserRole.CANDIDATE_DATA_SUBJECT:
            if target_candidate_id and target_candidate_id not in context.assigned_candidate_ids:
                return (
                    False,
                    f"ABAC_DENIED: Candidate '{context.user_id}' cannot view records of candidate '{target_candidate_id}'."
                )
            return True, "AUTHORIZED_DATA_SUBJECT_SELF_ACCESS"

        # 4. ABAC Rule: Technical Interviewer can only access assigned candidates
        if context.user_role == UserRole.TECHNICAL_INTERVIEWER:
            if target_candidate_id and target_candidate_id not in context.assigned_candidate_ids:
                return (
                    False,
                    f"ABAC_DENIED: Interviewer '{context.user_id}' is not assigned to candidate '{target_candidate_id}'."
                )

        # 5. ABAC Rule: Hiring Manager department boundary
        if context.user_role == UserRole.HIRING_MANAGER:
            if target_department and target_department.lower() != context.department.lower():
                return (
                    False,
                    f"ABAC_DENIED: Department mismatch. Manager in '{context.department}', target is '{target_department}'."
                )

        return True, "AUTHORIZED_RBAC_AND_ABAC_COMPLIANT"
