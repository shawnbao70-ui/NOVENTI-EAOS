"""PHX-G406 remediation: authoritative tip helper + no 0049-as-current-head."""

from __future__ import annotations

from pathlib import Path

from eaos_sdk import __version__ as sdk_version

from tests.contracts._baseline import (
    EXPECTED_PACKAGE,
    EXPECTED_TIP,
    HISTORICAL_COMMISSION_LEDGER_REV,
    assert_current_baseline,
    assert_revision_exists,
    assert_revision_is_ancestor_of_head,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "tests" / "contracts"
FORBIDDEN_CURRENT_HEAD = (
    f'get_current_head() == "{HISTORICAL_COMMISSION_LEDGER_REV}"'
)


def test_g406_baseline_helper_matches_live_tip_and_package() -> None:
    assert_current_baseline(sdk_version=sdk_version)
    assert EXPECTED_TIP == "0092_finance_realized_fx_gl_bridge_g372"
    assert EXPECTED_PACKAGE == "0.2.5"


def test_g406_historical_0049_exists_as_ancestor_not_current_head_literal() -> None:
    assert_revision_exists(HISTORICAL_COMMISSION_LEDGER_REV)
    assert_revision_is_ancestor_of_head(HISTORICAL_COMMISSION_LEDGER_REV)
    assert EXPECTED_TIP != HISTORICAL_COMMISSION_LEDGER_REV


def test_g406_no_contract_claims_0049_as_current_head() -> None:
    offenders: list[str] = []
    for path in sorted(CONTRACTS.rglob("*.py")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN_CURRENT_HEAD in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], (
        "contracts must not claim 0049 as get_current_head(); "
        f"offenders={offenders}"
    )
