"""Optional SQLAlchemy composition root for the API gateway.

Enabled when ``EAOS_GATEWAY_STORE=sql`` (requires ``EAOS_DATABASE_URL``).
Default remains in-memory so contract tests and local probes stay hermetic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from kernel.infrastructure.persistence.session import create_session_factory
from kernel.infrastructure.persistence.transactional_ai_runtime import (
    TransactionalAIRuntimeService,
)
from kernel.infrastructure.persistence.transactional_brain import TransactionalBrainService
from kernel.infrastructure.persistence.transactional_event_bus import (
    TransactionalEventBus,
)
from kernel.infrastructure.persistence.transactional_identity import (
    TransactionalIdentityService,
)
from kernel.infrastructure.persistence.transactional_knowledge import (
    TransactionalKnowledgeService,
)
from kernel.infrastructure.persistence.transactional_marketplace import (
    TransactionalMarketplaceService,
)
from kernel.infrastructure.persistence.transactional_organization import (
    TransactionalOrganizationService,
)
from kernel.infrastructure.persistence.transactional_package import (
    TransactionalPackageService,
)
from kernel.infrastructure.persistence.transactional_permission import (
    TransactionalPermissionService,
)
from kernel.infrastructure.persistence.transactional_smart_terminal import (
    TransactionalSmartTerminalService,
)
from kernel.infrastructure.persistence.transactional_twin import TransactionalTwinService
from kernel.infrastructure.persistence.transactional_workflow import (
    TransactionalWorkflowService,
)
from noventi.crm.customer360_persistence import TransactionalCustomer360Service
from noventi.crm.customer_advisory_persistence import (
    TransactionalCustomerAdvisoryService,
)
from noventi.crm.persistence import TransactionalCRMService
from noventi.finance.persistence import TransactionalFinanceService
from noventi.inventory.persistence import TransactionalInventoryService
from noventi.purchase.persistence import TransactionalPurchaseService
from noventi.purchase.supplier360_persistence import TransactionalSupplier360Service


@dataclass(frozen=True)
class SqlGatewayServices:
    identity: Any
    organization: Any
    permission: Any
    workflow: Any
    knowledge: Any
    event_bus: Any
    package: Any
    twin: Any
    brain: Any
    ai: Any
    terminal: Any
    marketplace: Any
    crm: Any
    customer360: Any
    customer_advisory: Any
    finance: Any
    inventory: Any
    purchase: Any
    supplier360: Any


def gateway_store_mode() -> str:
    return os.environ.get("EAOS_GATEWAY_STORE", "memory").strip().casefold() or "memory"


def compose_sql_gateway_services(
    *,
    platform_governors: set[UUID] | frozenset[UUID] | None = None,
    grant_administrators: set[UUID] | frozenset[UUID] | None = None,
) -> SqlGatewayServices:
    """Build transactional domain services sharing one session factory."""

    if gateway_store_mode() != "sql":
        raise RuntimeError("compose_sql_gateway_services requires EAOS_GATEWAY_STORE=sql")
    factory = create_session_factory()
    governors = frozenset(platform_governors or ())
    admins = frozenset(grant_administrators or governors)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators=admins,
    )
    workflow = TransactionalWorkflowService(
        factory,
        definition_administrators=admins,
    )
    twin = TransactionalTwinService(factory)
    knowledge = TransactionalKnowledgeService(factory)
    return SqlGatewayServices(
        identity=TransactionalIdentityService(
            factory,
            platform_governors=governors,
        ),
        organization=TransactionalOrganizationService(
            factory,
            platform_governors=governors,
        ),
        permission=permission,
        workflow=workflow,
        knowledge=knowledge,
        event_bus=TransactionalEventBus(factory),
        package=TransactionalPackageService(factory),
        twin=twin,
        brain=TransactionalBrainService(factory),
        ai=TransactionalAIRuntimeService(
            factory,
            definition_administrators=admins,
        ),
        terminal=TransactionalSmartTerminalService(
            factory,
            definition_administrators=admins,
        ),
        marketplace=TransactionalMarketplaceService(factory),
        crm=TransactionalCRMService(factory),
        customer360=TransactionalCustomer360Service(factory),
        customer_advisory=TransactionalCustomerAdvisoryService(factory),
        finance=TransactionalFinanceService(factory),
        inventory=TransactionalInventoryService(factory),
        purchase=TransactionalPurchaseService(factory),
        supplier360=TransactionalSupplier360Service(factory),
    )
