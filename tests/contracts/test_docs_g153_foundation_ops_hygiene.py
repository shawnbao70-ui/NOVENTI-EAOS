"""PHX-G153 Foundation ops / compatibility / checklist hygiene contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0172-foundation-ops-compatibility-checklist-hygiene.md"
GATE = ROOT / "docs" / "project" / "PHX-G153_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G153_ACCEPTANCE.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
COMPAT = ROOT / "docs" / "release" / "COMPATIBILITY.md"
CHECKLIST = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"


def test_g153_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "0.2.1" in adr
    assert "OPERATIONS_RUNBOOK" in adr or "Runbook" in adr
    assert "COMPATIBILITY" in adr or "Compatibility" in adr


def test_g153_runbook_documents_stubs_and_holds() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "0.2.3" in text
    assert "PHX-G153" in text or "G153" in text
    assert "PHX-G151" in text or "webauthn" in text.casefold()
    assert "503" in text or "GATEWAY_WEBAUTHN" in text
    assert "mint" in text.casefold() or "Held" in text or "deferred" in text.casefold()
    assert "Brain" in text and "Twin" in text
    assert "支付" in text or "payment" in text.casefold()
    assert "0092_finance_realized_fx_gl_bridge_g372" in text


def test_g153_compatibility_notes_additive_g145_g152() -> None:
    text = COMPAT.read_text(encoding="utf-8")
    assert "0.2.3" in text
    assert "0.2.1" in text
    assert "0029" in text
    assert "G145" in text or "PHX-G145" in text
    assert "G151" in text or "PHX-G151" in text or "webauthn" in text.casefold()
    assert "G152" in text or "PHX-G152" in text or "additive" in text.casefold()
    assert "payment" in text.casefold() or "支付" in text


def test_g153_checklist_covers_manifest_milestones() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "0.2.3" in text
    assert "PHX-G152" in text or "G145" in text
    assert "Manifest" in text or "RELEASE_MANIFEST" in text
    assert "payment" in text.casefold() or "支付" in text


def test_g153_manifest_and_baseline() -> None:
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"
    milestone_ids = {m["id"] for m in manifest["milestones"]}
    assert "PHX-G152" in milestone_ids
    assert "PHX-G153" in milestone_ids
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert by_id["PHX-G153"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"


def test_g153_ledger_and_status_sync() -> None:
    assert "DAL-U025" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G153" in STATUS.read_text(encoding="utf-8")
    assert "PHX-G153" in ENG_TIP.read_text(encoding="utf-8") or "G153" in ENG_TIP.read_text(
        encoding="utf-8"
    )
