"""PHX-G291 Legacy Knowledge Extract Finance pack contracts."""

from __future__ import annotations

from pathlib import Path

from eaos_sdk.catalog import load_release_manifest

from tests.contracts._baseline import (
    HISTORICAL_COMMISSION_LEDGER_REV,
    assert_current_baseline,
    assert_revision_exists,
)

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0310-legacy-knowledge-extract-finance.md"
GATE = ROOT / "docs" / "project" / "PHX-G291_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G291_ACCEPTANCE.md"
FINANCE = ROOT / "docs" / "knowledge" / "legacy-extract" / "finance"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_g291_adr_gate_acceptance() -> None:
    for p in (ADR, GATE, ACCEPTANCE):
        assert p.is_file()
    text = ADR.read_text(encoding="utf-8")
    assert "Accepted" in text and "PHX-G291" in text and "DAL-U164" in text
    assert "0.2.1" in text


def test_g291_finance_pack() -> None:
    for name in ("README.md", "INDEX.md", "receipts_ar.md"):
        assert (FINANCE / name).is_file(), name
    body = (FINANCE / "receipts_ar.md").read_text(encoding="utf-8")
    assert "业务规则" in body
    assert "只读来源路径" in body
    assert "ar_records" in body
    assert "receipts" in body
    assert "payment_status" in body


def test_g291_dual_ar_honesty() -> None:
    body = (FINANCE / "receipts_ar.md").read_text(encoding="utf-8")
    assert "parallel" in body.casefold() or "双" in body or "not reconciled" in body.casefold() or "无自动" in body


def test_g291_tip_ledger_status_manifest() -> None:
    assert "PHX-G291" in ENG_TIP.read_text(encoding="utf-8")
    assert "DAL-U164" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G291" in STATUS.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert any(m.get("id") == "PHX-G291" for m in manifest.get("milestones", []))
    assert_current_baseline()


def test_g291_alembic_baseline() -> None:
    assert_current_baseline()
    assert_revision_exists(HISTORICAL_COMMISSION_LEDGER_REV)
