"""Smart Terminal — independent governed interaction layer (PHX-T13)."""

from smart_terminal.models import (
    ApprovalPresentation,
    CommitReceipt,
    DeviceTrust,
    IntentStatus,
    PlanPreview,
    PreviewStatus,
    TerminalIntent,
    TerminalSession,
    TerminalSessionStatus,
)
from smart_terminal.repository import InMemorySmartTerminalRepository, SmartTerminalRepository
from smart_terminal.service import SmartTerminalService

__all__ = [
    "ApprovalPresentation",
    "CommitReceipt",
    "DeviceTrust",
    "InMemorySmartTerminalRepository",
    "IntentStatus",
    "PlanPreview",
    "PreviewStatus",
    "SmartTerminalRepository",
    "SmartTerminalService",
    "TerminalIntent",
    "TerminalSession",
    "TerminalSessionStatus",
]
