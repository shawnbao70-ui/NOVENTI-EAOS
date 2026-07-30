"""Shared closed response DTOs (UuidResult / BooleanResult — PHX-G170)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UuidResult(_ClosedModel):
    id: UUID
    data: UUID
    audit_id: UUID | str | None = None
    ok: bool | None = None


class BooleanResult(_ClosedModel):
    data: bool
    audit_id: UUID | str | None = None


class OkResponse(_ClosedModel):
    ok: bool = True
    audit_id: UUID | str | None = None


class AuthorizedData(_ClosedModel):
    authorized: Literal[True] = True


class AuthorizedResult(_ClosedModel):
    """Closed success envelope for Brain execute / Twin authorize (PHX-G335)."""

    data: AuthorizedData
    audit_id: UUID | str | None = None
