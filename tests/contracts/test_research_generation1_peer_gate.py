"""NRI Research Track — Generation-1 Peer Gate Board contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "docs" / "research" / "GENERATION1_PEER_GATE.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_g1_peer_gate_board_exists_and_lists_programs() -> None:
    assert GATE.is_file()
    text = GATE.read_text(encoding="utf-8")
    assert "NRI-G1-PEER-GATE" in text
    for rp in ("RP-001", "RP-006", "RP-008", "RP-010"):
        assert rp in text
    assert "RP-006 peer Pass" in text
    assert "self-certification" in text.casefold() or "不代填" in text or "Does not** invent" in text
    assert "execution_authority" in text or "Brain execute" in text


def test_g1_peer_gate_registered() -> None:
    assert "GENERATION1_PEER_GATE" in INDEX.read_text(encoding="utf-8")
    assert "NRI-G1-PEER-GATE" in LIBRARY.read_text(encoding="utf-8")
    assert "GENERATION1_PEER_GATE" in STATUS.read_text(encoding="utf-8") or "G1 Peer Gate" in STATUS.read_text(
        encoding="utf-8"
    )
