"""PHX-G292 Legacy Knowledge Extract Delivery pack contracts."""

from __future__ import annotations

from pathlib import Path

from eaos_sdk.catalog import load_release_manifest

from tests.contracts._baseline import (
    HISTORICAL_COMMISSION_LEDGER_REV,
    assert_current_baseline,
    assert_revision_exists,
)

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0311-legacy-knowledge-extract-delivery.md"
GATE = ROOT / "docs" / "project" / "PHX-G292_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G292_ACCEPTANCE.md"
DELIVERY = ROOT / "docs" / "knowledge" / "legacy-extract" / "delivery"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_g292_adr_gate_acceptance() -> None:
    for p in (ADR, GATE, ACCEPTANCE):
        assert p.is_file()
    text = ADR.read_text(encoding="utf-8")
    assert "Accepted" in text and "PHX-G292" in text and "DAL-U165" in text


def test_g292_delivery_pack() -> None:
    for name in ("README.md", "INDEX.md", "delivery_order.md"):
        assert (DELIVERY / name).is_file(), name
    body = (DELIVERY / "delivery_order.md").read_text(encoding="utf-8")
    assert "业务规则" in body and "只读来源路径" in body
    assert "create_do" in body or "Create DO" in body
    assert "A-003" in body or "stock" in body.casefold()


def test_g292_tip_ledger_status_manifest() -> None:
    assert "PHX-G292" in ENG_TIP.read_text(encoding="utf-8")
    assert "DAL-U165" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G292" in STATUS.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert any(m.get("id") == "PHX-G292" for m in manifest.get("milestones", []))
    assert_current_baseline()


def test_g292_alembic_baseline() -> None:
    assert_current_baseline()
    assert_revision_exists(HISTORICAL_COMMISSION_LEDGER_REV)
