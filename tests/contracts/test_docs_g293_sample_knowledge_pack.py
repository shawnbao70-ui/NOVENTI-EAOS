"""PHX-G293 Sample Knowledge Pack contracts."""

from __future__ import annotations

from pathlib import Path

from eaos_sdk.catalog import load_release_manifest

from tests.contracts._baseline import (
    HISTORICAL_COMMISSION_LEDGER_REV,
    assert_current_baseline,
    assert_revision_exists,
)

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0319-sample-knowledge-pack.md"
GATE = ROOT / "docs" / "project" / "PHX-G293_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G293_ACCEPTANCE.md"
PACK = ROOT / "docs" / "knowledge" / "sample-pack"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_docs_g293_adr_gate_acceptance() -> None:
    for p in (ADR, GATE, ACCEPTANCE):
        assert p.is_file()
    text = ADR.read_text(encoding="utf-8")
    assert "Accepted" in text and "PHX-G293" in text and "DAL-U229" in text
    assert "0.2.1" in text
    assert "0029" in text


def test_docs_g293_sample_pack_files() -> None:
    for name in (
        "README.md",
        "INDEX.md",
        "assembled_chain.md",
        "usage.md",
        "fail_closed.md",
    ):
        assert (PACK / name).is_file(), name


def test_docs_g293_cross_links_and_boundaries() -> None:
    readme = (PACK / "README.md").read_text(encoding="utf-8")
    index = (PACK / "INDEX.md").read_text(encoding="utf-8")
    chain = (PACK / "assembled_chain.md").read_text(encoding="utf-8")
    usage = (PACK / "usage.md").read_text(encoding="utf-8")
    fail = (PACK / "fail_closed.md").read_text(encoding="utf-8")

    assert "legacy-extract/crm" in readme or "../legacy-extract/crm" in readme
    assert "legacy-extract/sales" in readme or "../legacy-extract/sales" in readme
    assert "legacy-extract/finance" in readme or "../legacy-extract/finance" in readme
    assert "legacy-extract/delivery" in readme or "../legacy-extract/delivery" in readme
    assert "CRUD" in readme or "≠ CRUD" in readme
    assert "PHX-G290" in index and "PHX-G291" in index and "PHX-G292" in index
    assert "customer.md" in index and "sales_order.md" in index
    assert "receipts_ar.md" in index and "delivery_order.md" in index
    assert "dual" in chain.casefold() or "双" in chain
    assert "Terminal" in usage and "Research" in usage
    assert "Brain" in fail and "Twin" in fail
    assert "fail-closed" in fail.casefold() or "Closed" in fail


def test_docs_g293_tip_ledger_status_manifest() -> None:
    tip = ENG_TIP.read_text(encoding="utf-8")
    assert "PHX-G293" in tip
    assert "Sample knowledge pack" in tip or "Sample Knowledge Pack" in tip
    assert "DAL-U229" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G293" in STATUS.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert any(m.get("id") == "PHX-G293" for m in manifest.get("milestones", []))
    assert_current_baseline()


def test_docs_g293_alembic_baseline() -> None:
    assert_current_baseline()
    assert_revision_exists(HISTORICAL_COMMISSION_LEDGER_REV)
