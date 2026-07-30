"""PHX-G144 Foundation 0.2.1 release train contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk import __version__ as sdk_version
from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0163-foundation-0-2-1-release-train.md"
GATE = ROOT / "docs" / "project" / "PHX-G144_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G144_ACCEPTANCE.md"
MANIFEST_PATH = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"


def test_g144_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "0.2.1" in adr
    assert "additive-only" in adr.casefold() or "additive-only" in GATE.read_text(encoding="utf-8").casefold()


def test_g144_package_baseline_is_0_2_1() -> None:
    # G144 established 0.2.1; current published baseline tracks EXPECTED_PACKAGE.
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert MANIFEST_PATH.is_file()


def test_g144_alembic_head_unchanged() -> None:
    # G144 freeze no longer binds tip; current tip remains 0092 (G376 cut, no migration).
    manifest = load_release_manifest()
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"


def test_g144_fail_closed_holds_mentioned() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "fail-closed" in folded or "支付清算" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "role" in folded and "grant" in folded
    # G144 train held WebAuthn product page and Role→grant closed; G145/G146 later
    # opened thin posture only — ceremony / auto-write remain deferred relative
    # to this train's Out set.
    assert "webauthn" in folded


def test_g144_dal_or_changelog_references_train() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert (
        "DAL-U005" in ledger
        or "G144" in ledger
        or "Eng 1" in ledger
        or "PHX-G144" in ledger
        or "DAL-U005" in changelog
        or "PHX-G144" in changelog
        or "G144" in changelog
    )
