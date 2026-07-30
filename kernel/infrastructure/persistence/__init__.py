"""SQLAlchemy persistence foundation."""

from kernel.infrastructure.persistence.ai_runtime_models import (
    AIAgentRunRecord,
    AIMemoryEntryRecord,
    AIToolDeclarationRecord,
)
from kernel.infrastructure.persistence.ai_runtime_repository import (
    SQLAlchemyAIRuntimeRepository,
)
from kernel.infrastructure.persistence.brain_models import BrainInsightRecord
from kernel.infrastructure.persistence.brain_repository import (
    SQLAlchemyBrainRepository,
)
from kernel.infrastructure.persistence.marketplace_models import (
    MarketplaceAcquisitionRecord,
    MarketplaceDisputeRecord,
    MarketplaceInvoiceRecord,
    MarketplaceListingRecord,
    MarketplacePricingRecord,
    MarketplaceRevenueShareRecord,
)
from kernel.infrastructure.persistence.marketplace_repository import (
    SQLAlchemyMarketplaceRepository,
)
from kernel.infrastructure.persistence.transactional_marketplace import (
    TransactionalMarketplaceService,
)
from kernel.infrastructure.persistence.package_models import (
    PackageInstallationRecord,
    PackageManifestRecord,
)
from kernel.infrastructure.persistence.package_repository import (
    SQLAlchemyPackageRepository,
)
from kernel.infrastructure.persistence.twin_models import TwinSnapshotRecord
from kernel.infrastructure.persistence.twin_repository import (
    SQLAlchemyTwinRepository,
)
from kernel.infrastructure.persistence.transactional_brain import (
    TransactionalBrainService,
)
from kernel.infrastructure.persistence.transactional_twin import (
    TransactionalTwinService,
)
from kernel.infrastructure.persistence.smart_terminal_models import (
    TerminalExtensionRecord,
    TerminalIntentRecord,
    TerminalPreviewRecord,
    TerminalSessionRecord,
)
from kernel.infrastructure.persistence.smart_terminal_repository import (
    SQLAlchemySmartTerminalRepository,
)
from kernel.infrastructure.persistence.transactional_package import (
    TransactionalPackageService,
)
from kernel.infrastructure.persistence.transactional_smart_terminal import (
    TransactionalSmartTerminalService,
)
from kernel.infrastructure.persistence.audit_models import AuditEventRecord
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.event_models import (
    EventDeadLetterRecord,
    EventDeliveryRecord,
    EventOutboxRecord,
    EventRecord,
    EventSubscriptionRecord,
)
from kernel.infrastructure.persistence.event_repository import SQLAlchemyEventRepository
from kernel.infrastructure.persistence.identity_repository import (
    SQLAlchemyIdentityRepository,
)
from kernel.infrastructure.persistence.identity_organization import (
    SQLAlchemyMembershipEligibility,
    TransactionalIdentityOrganizationCoordinator,
)
from kernel.infrastructure.persistence.identity_models import (
    AIAssignmentRecord,
    AIEmployeeProfileRecord,
    CredentialRecord,
    PlatformIdentityGovernorRecord,
    SessionRecord,
    SubjectExternalRefRecord,
    SubjectRecord,
)
from kernel.infrastructure.persistence.idp_issuer_models import IdpIssuerBindingRecord
from kernel.infrastructure.persistence.idp_issuer_repository import (
    SQLAlchemyIdpIssuerRepository,
)
from kernel.infrastructure.persistence.eaos_declared_role_models import (
    EaosDeclaredRoleRecord,
)
from kernel.infrastructure.persistence.eaos_declared_role_repository import (
    SQLAlchemyEaosDeclaredRoleRepository,
)
from kernel.infrastructure.persistence.oidc_refresh_models import OidcRefreshBindingRecord
from kernel.infrastructure.persistence.oidc_refresh_repository import (
    SQLAlchemyOidcRefreshRepository,
)
from kernel.infrastructure.persistence.tenant_idp_models import TenantIdpBindingRecord
from kernel.infrastructure.persistence.tenant_idp_repository import (
    SQLAlchemyTenantIdpRepository,
)
from kernel.infrastructure.persistence.knowledge_models import (
    KnowledgeEntityRecord,
    KnowledgeLinkRecord,
    KnowledgeProvenanceRecord,
)
from kernel.infrastructure.persistence.knowledge_repository import (
    SQLAlchemyKnowledgeRepository,
)
from kernel.infrastructure.persistence.metadata import Base, metadata
from kernel.infrastructure.persistence.organization_models import (
    EnterpriseRecord,
    MembershipRecord,
    OrganizationUnitRecord,
    TenantRecord,
)
from kernel.infrastructure.persistence.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from kernel.infrastructure.persistence.organization_permission import (
    SQLAlchemyScopeResolver,
)
from kernel.infrastructure.persistence.permission_models import (
    GrantRecord,
    PermissionDecisionRecord,
    PolicyRecord,
    PolicyRuleRecord,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.session import (
    create_postgresql_engine,
    create_session_factory,
)
from kernel.infrastructure.persistence.transactional_ai_runtime import (
    TransactionalAIRuntimeService,
)
from kernel.infrastructure.persistence.transactional_identity import (
    TransactionalIdentityService,
)
from kernel.infrastructure.persistence.transactional_event_bus import (
    TransactionalEventBus,
)
from kernel.infrastructure.persistence.transactional_knowledge import (
    TransactionalKnowledgeService,
)
from kernel.infrastructure.persistence.transactional_organization import (
    TransactionalOrganizationService,
)
from kernel.infrastructure.persistence.transactional_permission import (
    TransactionalPermissionService,
)
from kernel.infrastructure.persistence.transactional_workflow import (
    TransactionalWorkflowService,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.infrastructure.persistence.workflow_models import (
    WorkflowDefinitionRecord,
    WorkflowHistoryRecord,
    WorkflowInstanceRecord,
    WorkflowSignalReceiptRecord,
    WorkflowTaskRecord,
)
from kernel.infrastructure.persistence.workflow_repository import (
    SQLAlchemyWorkflowRepository,
)

__all__ = [
    "AIAgentRunRecord",
    "AIAssignmentRecord",
    "AIEmployeeProfileRecord",
    "AIMemoryEntryRecord",
    "AIToolDeclarationRecord",
    "AuditEventRecord",
    "Base",
    "BrainInsightRecord",
    "CredentialRecord",
    "EventDeadLetterRecord",
    "EventDeliveryRecord",
    "EventOutboxRecord",
    "EventRecord",
    "EventSubscriptionRecord",
    "EnterpriseRecord",
    "GrantRecord",
    "IdpIssuerBindingRecord",
    "EaosDeclaredRoleRecord",
    "SQLAlchemyEaosDeclaredRoleRepository",
    "OidcRefreshBindingRecord",
    "TenantIdpBindingRecord",
    "KnowledgeEntityRecord",
    "KnowledgeLinkRecord",
    "KnowledgeProvenanceRecord",
    "MarketplaceAcquisitionRecord",
    "MarketplaceDisputeRecord",
    "MarketplaceInvoiceRecord",
    "MarketplaceListingRecord",
    "MarketplacePricingRecord",
    "MarketplaceRevenueShareRecord",
    "MembershipRecord",
    "OrganizationUnitRecord",
    "PackageInstallationRecord",
    "PackageManifestRecord",
    "PermissionDecisionRecord",
    "PlatformIdentityGovernorRecord",
    "PolicyRecord",
    "PolicyRuleRecord",
    "SessionRecord",
    "SQLAlchemyAIRuntimeRepository",
    "SQLAlchemyAuditLog",
    "SQLAlchemyBrainRepository",
    "SQLAlchemyEventRepository",
    "SQLAlchemyIdentityRepository",
    "SQLAlchemyIdpIssuerRepository",
    "SQLAlchemyOidcRefreshRepository",
    "SQLAlchemyTenantIdpRepository",
    "SQLAlchemyKnowledgeRepository",
    "SQLAlchemyMarketplaceRepository",
    "SQLAlchemyMembershipEligibility",
    "SQLAlchemyOrganizationRepository",
    "SQLAlchemyPackageRepository",
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyScopeResolver",
    "SQLAlchemySmartTerminalRepository",
    "SQLAlchemyTwinRepository",
    "SQLAlchemyWorkflowRepository",
    "SQLAlchemyUnitOfWork",
    "SubjectExternalRefRecord",
    "SubjectRecord",
    "TenantRecord",
    "TerminalExtensionRecord",
    "TerminalIntentRecord",
    "TerminalPreviewRecord",
    "TerminalSessionRecord",
    "TransactionalAIRuntimeService",
    "TransactionalBrainService",
    "TransactionalIdentityService",
    "TransactionalIdentityOrganizationCoordinator",
    "TransactionalEventBus",
    "TransactionalKnowledgeService",
    "TransactionalMarketplaceService",
    "TransactionalOrganizationService",
    "TransactionalPackageService",
    "TransactionalPermissionService",
    "TransactionalSmartTerminalService",
    "TransactionalTwinService",
    "TransactionalWorkflowService",
    "TwinSnapshotRecord",
    "WorkflowDefinitionRecord",
    "WorkflowHistoryRecord",
    "WorkflowInstanceRecord",
    "WorkflowSignalReceiptRecord",
    "WorkflowTaskRecord",
    "create_postgresql_engine",
    "create_session_factory",
    "metadata",
]
