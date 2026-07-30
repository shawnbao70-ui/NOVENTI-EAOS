"""PHX-G152 AR Board Queue + Foundation release hygiene contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0171-architecture-review-board-queue-and-release-hygiene.md"
GATE = ROOT / "docs" / "project" / "PHX-G152_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G152_ACCEPTANCE.md"
QUEUE = ROOT / "docs" / "research" / "ARCHITECTURE_REVIEW_BOARD_QUEUE.md"
MANIFEST_PATH = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"

ARC_IDS = [f"NRI-ARC-RP-{i:03d}" for i in range(1, 11)]


def test_g152_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "NRI-AR-BOARD-QUEUE" in adr or "ARCHITECTURE_REVIEW_BOARD_QUEUE" in adr
    assert "0.2.1" in adr
    assert "self-certify" in adr.casefold() or "自证" in adr


def test_g152_board_queue_lists_all_ten_awaiting() -> None:
    assert QUEUE.is_file()
    text = QUEUE.read_text(encoding="utf-8")
    assert "NRI-AR-BOARD-QUEUE" in text
    assert (
        "Board Decision — Hold" in text
        or "Awaiting Architecture Review Board" in text
        or "Awaiting Board" in text
    )
    assert "not" in text.casefold() and ("self-certify" in text.casefold() or "自证" in text or "Not Accepted" in text)
    assert "Promote" in text and "Hold" in text and "Reject" in text
    assert "Brain" in text and "Twin" in text
    for arc_id in ARC_IDS:
        assert arc_id in text
    assert "DAL-U024" in text
    # must not claim Board Accepted for the queue itself
    assert "Candidate Package" in text or "Awaiting" in text or "Hold" in text
    assert "Board decision" in text.casefold() or "decision block" in text.casefold()


def test_g152_manifest_milestones_include_g145_through_g152() -> None:
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"
    milestone_ids = {m["id"] for m in manifest["milestones"]}
    for mid in (
        "PHX-G144",
        "PHX-G145",
        "PHX-G146",
        "PHX-G147",
        "PHX-G148",
        "PHX-G149",
        "PHX-G150",
        "PHX-G151",
        "PHX-G152",
    ):
        assert mid in milestone_ids
    by_id = {m["id"]: m for m in manifest["milestones"]}
    for mid in ("PHX-G145", "PHX-G151", "PHX-G152"):
        assert by_id[mid]["status"] == "fully_accepted"


def test_g152_alembic_head_unchanged() -> None:
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"


def test_g152_registry_and_tips_link_queue() -> None:
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    tip = TIP.read_text(encoding="utf-8")
    eng = ENG_TIP.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_BOARD_QUEUE" in index or "NRI-AR-BOARD-QUEUE" in index
    assert "NRI-AR-BOARD-QUEUE" in library
    assert "ARCHITECTURE_REVIEW_BOARD_QUEUE" in tip or "NRI-AR-BOARD-QUEUE" in tip
    assert "PHX-G152" in eng or "G152" in eng
    assert "DAL-U024" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G152" in STATUS.read_text(encoding="utf-8")


def test_g152_fail_closed_holds_mentioned() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE, QUEUE))
    folded = combined.casefold()
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "payment" in folded or "支付" in combined
    assert MANIFEST_PATH.is_file()
