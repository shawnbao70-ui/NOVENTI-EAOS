"""Transactional Package Platform contracts."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    PackageInstallationRecord,
    PackageManifestRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPackageService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MANIFEST = ROOT / "packages" / "sample_ops" / "manifest.json"


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _context(
    tenant_id=None,
    *,
    subject_id=None,
    subject_type=SubjectType.SERVICE,
    platform=False,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=subject_type,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    initial = _context(tenant.data)
    admin = identity.register_subject(
        initial,
        subject_type=SubjectKind.HUMAN,
        display_name="Package Admin",
    )
    assert admin.data is not None
    return (
        tenant.data,
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
    )


def test_transactional_sample_ops_round_trip() -> None:
    engine = _engine()
    tenant_id, admin = _foundation(engine)
    factory = create_session_factory(engine)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.subject_id},
    )
    packages = TransactionalPackageService(factory)
    for resource_type, actions in (
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose", "publish"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=admin.subject_id,
            resource_type=resource_type,
            actions=actions,
        ).ok

    payload = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
    registered = packages.register_manifest(
        admin,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload["surfaces"],
        actions=payload["actions"],
        required_permissions=payload["required_permissions"],
        declared_events=payload["declared_events"],
    )
    assert registered.ok and registered.data is not None
    assert packages.publish_manifest(admin, manifest_id=registered.data).ok
    installed = packages.install_package(admin, manifest_id=registered.data)
    assert installed.ok and installed.data is not None
    resolved = packages.resolve_action(admin, action_key="ops.brief.compose")
    assert resolved.ok and resolved.data is not None

    with factory() as session:
        assert session.scalar(
            select(PackageManifestRecord).where(
                PackageManifestRecord.id == registered.data
            )
        ) is not None
        assert session.scalar(
            select(PackageInstallationRecord).where(
                PackageInstallationRecord.id == installed.data
            )
        ) is not None
