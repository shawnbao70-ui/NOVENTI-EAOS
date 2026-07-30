"""PHX-G157 Foundation ops / checklist hygiene after G156 contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0176-foundation-ops-checklist-hygiene-after-g156.md"
GATE = ROOT / "docs" / "project" / "PHX-G157_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G157_ACCEPTANCE.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
CHECKLIST = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"


def test_g157_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "0.2.1" in adr
    assert "G156" in adr or "role-grants" in adr.casefold() or "Role" in adr


def test_g157_runbook_documents_g154_g156_stubs() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "0.2.3" in text
    assert "PHX-G157" in text or "G157" in text
    assert "GATEWAY_WEBAUTHN_REGISTRATION_DISABLED" in text or "503" in text
    assert "ceremony_step" in text or "G154" in text
    assert "role-grants" in text.casefold() or "ROLE_GRANT_AUTO_WRITE" in text
    assert "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED" in text or "role-grants" in text
    assert "explicit PO" in text.casefold() or "PO" in text or "mint" in text.casefold()
    assert "Brain" in text and "Twin" in text


def test_g157_checklist_covers_g157_milestones() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "0.2.3" in text
    assert "G157" in text or "PHX-G157" in text
    assert "G156" in text or "role-grants" in text.casefold() or "Role" in text
    assert "Manifest" in text or "RELEASE_MANIFEST" in text


def test_g157_manifest_and_baseline() -> None:
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert "PHX-G156" in by_id
    assert "PHX-G157" in by_id
    assert by_id["PHX-G157"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"


def test_g157_ledger_and_status_sync() -> None:
    assert "DAL-U029" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G157" in STATUS.read_text(encoding="utf-8")
    assert "PHX-G157" in ENG_TIP.read_text(encoding="utf-8") or "G157" in ENG_TIP.read_text(
        encoding="utf-8"
    )
