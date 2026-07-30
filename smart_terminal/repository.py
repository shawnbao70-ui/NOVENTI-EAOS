"""In-memory repository for Smart Terminal workspace state."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol
from uuid import UUID

from kernel.shared.errors import ErrorCode, KernelError
from smart_terminal.models import (
    PlanPreview,
    TerminalExtension,
    TerminalIntent,
    TerminalSession,
)


class SmartTerminalRepository(Protocol):
    def add_session(self, session: TerminalSession) -> None: ...

    def get_session(self, session_id: UUID) -> TerminalSession | None: ...

    def save_session(
        self,
        session: TerminalSession,
        *,
        expected_version: int,
    ) -> None: ...

    def add_intent(self, intent: TerminalIntent) -> None: ...

    def get_intent(self, intent_id: UUID) -> TerminalIntent | None: ...

    def save_intent(
        self,
        intent: TerminalIntent,
        *,
        expected_version: int,
    ) -> None: ...

    def add_preview(self, preview: PlanPreview) -> None: ...

    def get_preview(self, preview_id: UUID) -> PlanPreview | None: ...

    def save_preview(
        self,
        preview: PlanPreview,
        *,
        expected_version: int,
    ) -> None: ...

    def list_previews_for_intent(self, intent_id: UUID) -> list[PlanPreview]: ...

    def add_extension(self, extension: TerminalExtension) -> None: ...

    def get_extension(self, extension_id: UUID) -> TerminalExtension | None: ...

    def save_extension(
        self,
        extension: TerminalExtension,
        *,
        expected_version: int,
    ) -> None: ...

    def list_extensions(self, *, tenant_id: UUID) -> list[TerminalExtension]: ...


class InMemorySmartTerminalRepository:
    def __init__(self) -> None:
        self._sessions: dict[UUID, TerminalSession] = {}
        self._intents: dict[UUID, TerminalIntent] = {}
        self._previews: dict[UUID, PlanPreview] = {}
        self._extensions: dict[UUID, TerminalExtension] = {}

    def add_session(self, session: TerminalSession) -> None:
        self._sessions[session.id] = deepcopy(session)

    def get_session(self, session_id: UUID) -> TerminalSession | None:
        session = self._sessions.get(session_id)
        return deepcopy(session) if session is not None else None

    def save_session(
        self,
        session: TerminalSession,
        *,
        expected_version: int,
    ) -> None:
        current = self._sessions.get(session.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "terminal session version conflict")
        self._sessions[session.id] = deepcopy(session)

    def add_intent(self, intent: TerminalIntent) -> None:
        self._intents[intent.id] = deepcopy(intent)

    def get_intent(self, intent_id: UUID) -> TerminalIntent | None:
        intent = self._intents.get(intent_id)
        return deepcopy(intent) if intent is not None else None

    def save_intent(
        self,
        intent: TerminalIntent,
        *,
        expected_version: int,
    ) -> None:
        current = self._intents.get(intent.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "terminal intent version conflict")
        self._intents[intent.id] = deepcopy(intent)

    def add_preview(self, preview: PlanPreview) -> None:
        self._previews[preview.id] = deepcopy(preview)

    def get_preview(self, preview_id: UUID) -> PlanPreview | None:
        preview = self._previews.get(preview_id)
        return deepcopy(preview) if preview is not None else None

    def save_preview(
        self,
        preview: PlanPreview,
        *,
        expected_version: int,
    ) -> None:
        current = self._previews.get(preview.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "plan preview version conflict")
        self._previews[preview.id] = deepcopy(preview)

    def list_previews_for_intent(self, intent_id: UUID) -> list[PlanPreview]:
        return [
            deepcopy(item)
            for item in self._previews.values()
            if item.intent_id == intent_id
        ]

    def add_extension(self, extension: TerminalExtension) -> None:
        self._extensions[extension.id] = deepcopy(extension)

    def get_extension(self, extension_id: UUID) -> TerminalExtension | None:
        item = self._extensions.get(extension_id)
        return deepcopy(item) if item is not None else None

    def save_extension(
        self,
        extension: TerminalExtension,
        *,
        expected_version: int,
    ) -> None:
        current = self._extensions.get(extension.id)
        if current is None or current.version_num != expected_version:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "terminal extension version conflict",
            )
        self._extensions[extension.id] = deepcopy(extension)

    def list_extensions(self, *, tenant_id: UUID) -> list[TerminalExtension]:
        return [
            deepcopy(item)
            for item in self._extensions.values()
            if item.tenant_id == tenant_id
        ]
