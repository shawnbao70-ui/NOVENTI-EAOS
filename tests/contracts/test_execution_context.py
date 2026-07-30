"""L0 context contract tests — KERNEL_CONTRACT_TEST_PLAN N-01 family."""

from __future__ import annotations

from uuid import uuid4

import pytest

from kernel.shared.context import ExecutionContext, SubjectType, require_context
from kernel.shared.errors import ErrorCode, KernelError


def _base_ctx(**kwargs) -> ExecutionContext:
    data = {
        "subject_id": uuid4(),
        "subject_type": SubjectType.HUMAN,
        "correlation_id": str(uuid4()),
        "request_time": ExecutionContext.utc_now(),
        "tenant_id": uuid4(),
    }
    data.update(kwargs)
    return ExecutionContext(**data)


def test_require_context_ok() -> None:
    require_context(_base_ctx(), tenant_data_plane=True)


def test_n01_missing_tenant_fail_closed() -> None:
    ctx = _base_ctx(tenant_id=None)
    with pytest.raises(KernelError) as exc:
        require_context(ctx, tenant_data_plane=True)
    assert exc.value.code == ErrorCode.CTX_MISSING_TENANT


def test_missing_subject() -> None:
    # frozen dataclass — construct with empty uuid still "present"; simulate blank correlation
    ctx = _base_ctx(correlation_id="  ")
    with pytest.raises(KernelError) as exc:
        require_context(ctx, tenant_data_plane=True)
    assert exc.value.code == ErrorCode.CTX_MISSING_CORRELATION


def test_platform_scope_forbidden_on_tenant_plane() -> None:
    ctx = _base_ctx(platform_scope=True)
    with pytest.raises(KernelError) as exc:
        require_context(ctx, tenant_data_plane=True)
    assert exc.value.code == ErrorCode.CTX_INVALID


def test_platform_scope_allows_missing_tenant() -> None:
    ctx = _base_ctx(tenant_id=None, platform_scope=True)
    require_context(ctx, tenant_data_plane=False)
