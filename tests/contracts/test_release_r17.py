"""PHX-R17 Release Train contracts — manifest, SDK, adapters, compatibility."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE
from uuid import uuid4

import yaml
from alembic.config import Config
from alembic.script import ScriptDirectory

from api.adapters import list_adapters, require_adapter
from eaos_platform.marketplace.service import MarketplaceService
from eaos_sdk import (
    __version__ as sdk_version,
    build_tenant_context,
    list_openapi_contracts,
    load_release_manifest,
    unwrap,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
COMPAT_PATH = ROOT / "docs" / "release" / "COMPATIBILITY.md"
RUNBOOK_PATH = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
CHECKLIST_PATH = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
PYPROJECT = ROOT / "pyproject.toml"


def test_release_docs_exist() -> None:
    assert MANIFEST_PATH.is_file()
    assert COMPAT_PATH.is_file()
    assert RUNBOOK_PATH.is_file()
    assert CHECKLIST_PATH.is_file()
    assert "additive-only" in COMPAT_PATH.read_text(encoding="utf-8").casefold()


def test_release_manifest_matches_package_and_alembic() -> None:
    # R17 established Foundation 0.2.0; current package baseline tracks EXPECTED_PACKAGE.
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert sdk_version == "0.2.5"
    text = PYPROJECT.read_text(encoding="utf-8")
    assert f'version = "{EXPECTED_PACKAGE}"' in text

    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == manifest["alembic_head"]
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"


def test_openapi_inventory_complete_and_valid() -> None:
    contracts = list_openapi_contracts()
    assert len(contracts) == 14
    for relative in contracts:
        path = ROOT / relative
        assert path.is_file(), relative
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert loaded["openapi"].startswith("3.1")


def test_api_adapters_match_manifest() -> None:
    adapters = list_adapters()
    assert {item.openapi_path for item in adapters} == set(list_openapi_contracts())
    identity = require_adapter("identity")
    assert identity.transport == "openapi-3.1"


def test_sdk_context_and_unwrap() -> None:
    ctx = build_tenant_context(
        tenant_id=uuid4(),
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
    )
    assert ctx.platform_scope is False
    assert ctx.tenant_id is not None
    assert unwrap(KernelResult.success(42)) == 42


def test_marketplace_deferred_commercial_still_fail_closed() -> None:
    class _AllowAll:
        def is_eligible(self, *, subject_id, tenant_id) -> bool:
            return True

    admin = uuid4()
    permission = PermissionService(
        grant_administrators={admin},
        principal_eligibility=_AllowAll(),
    )
    market = MarketplaceService(permission)
    tenant_id = uuid4()
    ctx = ExecutionContext(
        subject_id=admin,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert permission.grant(
        ctx,
        principal_subject_id=admin,
        resource_type="marketplace_listing",
        actions={"create", "read", "price"},
    ).ok
    created = market.create_listing(
        ctx,
        package_key="noventi.release.probe",
        package_version="1.0.0",
        required_permissions=["pkg.probe:read"],
        declared_events=[],
        data_scope="tenant.probe",
    )
    assert created.data is not None
    assert market.set_pricing(ctx, listing_id=created.data, price="1").ok
    denied = market.deny_unsupported_commercial(
        ctx,
        operation="capture_payment",
        listing_id=created.data,
    )
    assert denied.error_code == ErrorCode.MARKETPLACE_COMMERCIAL_POLICY_REQUIRED
