"""Shared Gateway DTO helpers (PHX-G170 UuidResult unification)."""

from __future__ import annotations

from typing import Any
from uuid import UUID


def uuid_result(
    resource_id: UUID,
    *,
    audit_id: UUID | None = None,
    ok: bool | None = None,
) -> dict[str, Any]:
    """Return a dual-key UuidResult: ``id`` and ``data`` carry the same UUID.

    Pre-G170 domains used either ``{id}`` or ``{data}``. Emitting both keeps
    existing clients working while closing the dialect fence.
    """

    value = str(resource_id)
    payload: dict[str, Any] = {"id": value, "data": value}
    if ok is not None:
        payload["ok"] = ok
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload
