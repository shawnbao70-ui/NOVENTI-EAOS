"""PHX-G159 Generation-1 Architecture Review Board Hold session contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0178-generation1-architecture-review-board-hold.md"
GATE = ROOT / "docs" / "project" / "PHX-G159_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G159_ACCEPTANCE.md"
QUEUE = ROOT / "docs" / "research" / "ARCHITECTURE_REVIEW_BOARD_QUEUE.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"

PROGRAMS = {
    "RP-001-enterprise-discovery": "ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md",
    "RP-002-enterprise-dna": "ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md",
    "RP-003-capability-first": "ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md",
    "RP-004-organization-neutrality": "ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md",
    "RP-005-ai-workforce-transformation": "ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md",
    "RP-006-ai-infrastructure-platform": "ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md",
    "RP-007-enterprise-evolution-engine": "ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md",
    "RP-008-smart-factory": "ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md",
    "RP-009-enterprise-brain-evolution": "ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md",
    "RP-010-future-enterprise-operating-model": "ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md",
}


def test_g159_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "Hold" in adr
    assert "DAL-G005" in adr
    assert "0.2.1" in adr
    assert "Eng" in adr or "eng" in adr.casefold()


def test_g159_all_ten_packages_hold() -> None:
    for folder, name in PROGRAMS.items():
        path = ROOT / "docs" / "research" / "programs" / folder / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "Board Decision — Hold" in text
        assert "**Hold**" in text
        assert "PHX-G159" in text
        assert "DAL-G005" in text
        assert "no Eng" in text.casefold() or "Eng ingest" in text or "Eng soft-queue" in text


def test_g159_queue_records_hold_session() -> None:
    text = QUEUE.read_text(encoding="utf-8")
    assert "NRI-AR-BOARD-QUEUE" in text
    assert "Board Decision — Hold" in text or "Hold" in text
    assert "PHX-G159" in text
    assert "DAL-G005" in text or "DAL-U031" in text
    assert "Promote" in text and "Hold" in text and "Reject" in text
    for i in range(1, 11):
        assert f"NRI-ARC-RP-{i:03d}" in text
    # Hold must not open Eng ingest
    assert "no Eng" in text.casefold() or "Eng ingest" in text or "≠ Eng" in text


def test_g159_ledger_grant_and_usage() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-G005" in ledger
    assert "DAL-U031" in ledger
    assert "PHX-G159" in ledger


def test_g159_registry_tips_status_manifest() -> None:
    assert "PHX-G159" in INDEX.read_text(encoding="utf-8") or "Board Decision — Hold" in INDEX.read_text(
        encoding="utf-8"
    )
    library = LIBRARY.read_text(encoding="utf-8")
    assert "Board Decision — Hold" in library or "Hold" in library
    tip = TIP.read_text(encoding="utf-8")
    assert "PHX-G159" in tip or "Board Decision — Hold" in tip
    eng = ENG_TIP.read_text(encoding="utf-8")
    assert "PHX-G159" in eng or "Board" in eng and "Hold" in eng
    assert "PHX-G159" in STATUS.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert by_id["PHX-G159"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"


def test_g159_fail_closed_holds() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE, QUEUE)
    )
    folded = combined.casefold()
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "payment" in folded or "支付" in combined
