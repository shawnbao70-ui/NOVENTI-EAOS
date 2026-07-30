"""PHX-G290 Legacy Knowledge Extract CRM + Sales pack contracts."""

from __future__ import annotations

from pathlib import Path

from eaos_sdk.catalog import load_release_manifest

from tests.contracts._baseline import (
    HISTORICAL_COMMISSION_LEDGER_REV,
    assert_current_baseline,
    assert_revision_exists,
)

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0309-legacy-knowledge-extract-crm-sales.md"
GATE = ROOT / "docs" / "project" / "PHX-G290_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G290_ACCEPTANCE.md"
EXTRACT = ROOT / "docs" / "knowledge" / "legacy-extract"
CRM = EXTRACT / "crm"
SALES = EXTRACT / "sales"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def test_g290_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G290" in adr
    assert "DAL-U163" in adr
    assert "0.2.1" in adr
    assert "0029" in adr or "Alembic" in adr


def test_g290_crm_pack_structure() -> None:
    for name in ("README.md", "INDEX.md", "customer.md", "opportunity.md", "contract.md", "quotation.md"):
        path = CRM / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "业务规则" in text or name in ("README.md", "INDEX.md")
        if name.endswith(".md") and name not in ("README.md", "INDEX.md"):
            assert "只读来源路径" in text
            assert "EZAM_CRM" in text


def test_g290_sales_pack_structure() -> None:
    for name in ("README.md", "INDEX.md", "sales_order.md"):
        assert (SALES / name).is_file(), name
    so = (SALES / "sales_order.md").read_text(encoding="utf-8")
    assert "业务规则" in so
    assert "只读来源路径" in so
    assert "convert" in so.casefold() or "convert_so" in so
    assert "已确认" in so


def test_g290_root_index_and_boundaries() -> None:
    root = (EXTRACT / "README.md").read_text(encoding="utf-8")
    assert "crm/" in root or "crm" in root
    assert "sales/" in root or "sales" in root
    assert "not" in root.casefold()
    assert "copy" in root.casefold() or "源码" in root
    assert "PHX-G290" in root


def test_g290_contract_absence_honesty() -> None:
    contract = (CRM / "contract.md").read_text(encoding="utf-8")
    assert "not a first-class" in contract.casefold() or "不是" in contract or "Weak" in contract
    assert "DOCUMENT_MODULES" in contract or "document" in contract.casefold()


def test_g290_no_source_dump_markers() -> None:
    """Knowledge packs must paraphrase — reject obvious full-file dump markers."""
    banned = ("```python\nfrom apps.", "```sql\nCREATE TABLE customers")
    for path in list(CRM.glob("*.md")) + list(SALES.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for marker in banned:
            assert marker not in text, f"{path.name} looks like a source dump"


def test_g290_tip_ledger_status_manifest() -> None:
    tip = ENG_TIP.read_text(encoding="utf-8")
    assert "PHX-G290" in tip
    assert "DAL-U163" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G290" in STATUS.read_text(encoding="utf-8")
    assert "PHX-G290" in MANIFEST.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert any(m.get("id") == "PHX-G290" for m in manifest.get("milestones", []))
    assert_current_baseline()


def test_g290_package_and_alembic_baseline() -> None:
    assert_current_baseline()
    assert_revision_exists(HISTORICAL_COMMISSION_LEDGER_REV)
    assert "0.2.1" in ADR.read_text(encoding="utf-8")
