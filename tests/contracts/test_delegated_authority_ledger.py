"""PHX Delegated Authority Ledger contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
PLAYBOOK = ROOT / "docs" / "project" / "DUAL_TRACK_GOVERNANCE.md"
GATE = ROOT / "docs" / "research" / "GENERATION1_PEER_GATE.md"


def test_delegated_authority_ledger_exists_and_records_g001_u001() -> None:
    assert LEDGER.is_file()
    text = LEDGER.read_text(encoding="utf-8")
    assert "PHX-DAL" in text
    assert "DAL-G003" in text
    assert "DAL-U001" in text and "DAL-U002" in text
    assert "DAL-U003" in text and "DAL-U004" in text
    assert "DAL-U005" in text
    assert "DAL-U006" in text
    assert "DAL-U007" in text
    assert "DAL-U008" in text
    assert "DAL-U009" in text
    assert "DAL-U010" in text
    assert "DAL-U011" in text
    assert "DAL-U012" in text
    assert "DAL-U013" in text
    assert "DAL-U014" in text
    assert "DAL-U015" in text
    assert "DAL-U016" in text
    assert "DAL-U017" in text
    assert "DAL-U018" in text
    assert "DAL-U019" in text
    assert "DAL-U020" in text
    assert "DAL-U021" in text
    assert "DAL-U022" in text
    assert "DAL-U023" in text
    assert "DAL-U024" in text
    assert "DAL-U025" in text
    assert "DAL-U026" in text
    assert "DAL-U027" in text
    assert "DAL-U028" in text
    assert "DAL-U029" in text
    assert "DAL-U030" in text
    assert "DAL-U031" in text
    assert "DAL-U032" in text
    assert "DAL-U034" in text or "DAL-U035" in text
    assert "DAL-U035" in text
    assert "DAL-G004" in text
    assert "DAL-G005" in text
    assert "DAL-G006" in text
    assert "DAL-G007" in text
    assert "DAL-G008" in text or "WebAuthn" in text
    assert "DAL-U037" in text or "PHX-G160" in text
    assert "PHX-G162" in text or "payment" in text.casefold()
    assert "PHX-G159" in text or "Hold" in text
    assert "PHX-G161" in text or "Role→grant" in text or "live mint" in text.casefold()
    assert "PHX-G160" in text or "WebAuthn" in text
    assert "NRI-ARC-RP-002" in text or "RP-002" in text
    assert "NRI-ARC-RP-003" in text or "RP-003" in text
    assert "NRI-ARC-RP-004" in text or "RP-004" in text
    assert "NRI-ARC-RP-006" in text or "RP-006" in text
    assert "NRI-ARC-RP-008" in text or "RP-008" in text
    assert "NRI-ARC-RP-010" in text or "RP-010" in text
    assert "PHX-G144" in text or "0.2.1" in text
    assert "PHX-G145" in text or "WebAuthn" in text
    assert "PHX-G146" in text or "Role" in text
    assert "PHX-G147" in text or "OIDC" in text
    assert "PHX-G148" in text or "OpenAPI" in text
    assert "PHX-G149" in text or "ENG_SOFT_QUEUE_TIP" in text
    assert "PHX-G150" in text or "AUTONOMOUS_EXECUTION" in text or "AED" in text
    assert "GENERATION2_TIP_BOARD" in text or "NRI-G2-TIP" in text
    assert "NRI-ARC-RP-001" in text or "ARCHITECTURE_REVIEW_CANDIDATE" in text or "RP-001" in text
    assert "NRI-ARC-RP-007" in text or "RP-007" in text
    assert "NRI-ARC-RP-005" in text or "RP-005" in text
    assert "NRI-ARC-RP-009" in text or "RP-009" in text
    assert "2026-07-27" in text
    assert "Usage Log" in text
    assert "Active Grants" in text
    assert "Active" in text
    assert "1" in text and "2" in text and "3" in text and "4" in text
    assert "peer" in text.casefold()
    assert "Constitution" in text or "宪章" in text or "Charter" in text
    assert "臻宇" in text
    assert "HARD HOLD" in text or "HARD HOLDS" in text or "AED" in text or "Autonomous Execution" in text


def test_delegated_authority_ledger_is_linked() -> None:
    assert "DELEGATED_AUTHORITY_LEDGER" in STATUS.read_text(encoding="utf-8")
    assert "DELEGATED_AUTHORITY_LEDGER" in PLAYBOOK.read_text(encoding="utf-8")
    assert "DELEGATED_AUTHORITY_LEDGER" in GATE.read_text(encoding="utf-8")
