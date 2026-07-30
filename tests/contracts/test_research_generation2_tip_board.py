"""NRI Research Track — Generation-2 Tip Board contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"


def test_g2_tip_board_exists_and_states_g1_complete() -> None:
    assert TIP.is_file()
    text = TIP.read_text(encoding="utf-8")
    assert "NRI-G2-TIP" in text
    assert "RP-001" in text and "RP-010" in text
    assert "complete" in text.casefold() or "完成" in text
    assert "Accepted" in text or "WP" in text
    assert "optional" in text.casefold() or "可选" in text
    assert "T2" in text and "T3" in text
    assert "Architecture Review" in text
    assert "self-cert" in text.casefold() or "自证" in text or "not self-certify" in text.casefold()
    assert "Promotion Rules" in text or "RESEARCH_PROMOTION_RULES" in text
    assert "RP-011" in text or "new RP" in text.casefold()
    assert "Constitution" in text or "Const" in text or "Blueprint" in text or "BP" in text
    assert "Brain execute" in text or "Brain" in text
    assert "Eng" in text
    assert "DAL-U011" in text


def test_g2_tip_board_registered_and_linked() -> None:
    assert "GENERATION2_TIP_BOARD" in INDEX.read_text(encoding="utf-8")
    assert "NRI-G2-TIP" in INDEX.read_text(encoding="utf-8")
    assert "NRI-G2-TIP" in LIBRARY.read_text(encoding="utf-8")
    assert "GENERATION2_TIP_BOARD" in LIBRARY.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "GENERATION2_TIP_BOARD" in status or "NRI-G2-TIP" in status
    assert "DAL-U011" in status or "G2" in status
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U011" in ledger
    assert "GENERATION2_TIP_BOARD" in ledger or "NRI-G2-TIP" in ledger
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert "GENERATION2_TIP_BOARD" in changelog or "NRI-G2-TIP" in changelog
