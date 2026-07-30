"""NRI Research Track — RP-001 peer package + RP-005 evidence pack contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP001 = ROOT / "docs" / "research" / "programs" / "RP-001-enterprise-discovery"
RP005 = ROOT / "docs" / "research" / "programs" / "RP-005-ai-workforce-transformation"
PEER = RP001 / "PEER_REVIEW_PACKAGE.md"
EVID005 = RP005 / "EVIDENCE_PACK.md"
DELIV005 = RP005 / "DELIVERABLES-RP-005.md"
ANRF = RP005 / "AI_NATIVE_ROLE_FRAMEWORK.md"
INV_DIR = RP005 / "inventories"
RI_FILES = (
    INV_DIR / "RI-01-office-synthetic.md",
    INV_DIR / "RI-02-ops-synthetic.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp001_peer_review_package_pass_not_self_author() -> None:
    assert PEER.is_file()
    text = PEER.read_text(encoding="utf-8")
    assert "NRI-RP-001-PEER" in text
    assert "臻宇" in text
    assert "No self-certification" in text or "self-certif" in text.casefold()
    assert "Pass — WP Draft Allowed" in text
    assert "Pass → WP Draft Allowed" in text or "WP Draft Allowed" in text
    assert "Constitution" in text and "Runtime" in text
    # Peer Pass precedes WP content Acceptance (now Accepted under CA delegation)
    wp = (RP001 / "WHITE_PAPER-RP-001.md").read_text(encoding="utf-8")
    assert "**Status:** Accepted White Paper" in wp
    assert "Approval:** Accepted" in wp or "**Approval:** Accepted" in wp


def test_rp005_evidence_pack_and_deliverables() -> None:
    assert EVID005.is_file()
    assert DELIV005.is_file()
    evid = EVID005.read_text(encoding="utf-8")
    deliv = DELIV005.read_text(encoding="utf-8")
    anrf = ANRF.read_text(encoding="utf-8")
    assert "NRI-RP-005-EVID" in evid
    assert "C-AW-01" in evid and "C-AW-10" in evid
    assert "RI-01" in evid and "RI-02" in evid
    assert "V-AW-01" in evid
    assert "never" in evid.casefold()
    assert "Role→grant" in evid or "grant" in evid.casefold()
    assert "NRI-RP-005-DELIV" in deliv
    for n in range(1, 17):
        assert f"| {n} |" in deliv
    assert "EVIDENCE_PACK.md" in anrf
    assert "DELIVERABLES-RP-005.md" in anrf


def test_wave1_registry_points_to_peer_and_rp005_pack() -> None:
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "PEER_REVIEW_PACKAGE" in index or "Peer Review Package" in index
    assert "NRI-RP-001-PEER" in library
    assert "NRI-RP-005-EVID" in library
    assert "NRI-RP-005-DELIV" in library
    assert "PEER_REVIEW" in status or "peer" in status.casefold()
    assert "RP-005" in status


def test_rp005_synthetic_inventories_complete() -> None:
    assert (INV_DIR / "README.md").is_file()
    for path in RI_FILES:
        assert path.is_file(), path
        text = path.read_text(encoding="utf-8")
        assert "mode: synthetic" in text
        assert "role_classes_count: 14" in text
        assert "actor_separation_ok: yes" in text
        assert "title_neq_grant_ok: yes" in text
        assert "auto_grant_minted: never" in text
        assert "Constitution" in text and "Runtime" in text
    evid = EVID005.read_text(encoding="utf-8")
    assert "Synthetic Complete" in evid
    assert "role inventories completed | **Yes**" in evid or (
        "inventories completed" in evid and "**Yes**" in evid
    )
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-RP-005-RI-01" in library
    assert "NRI-RP-005-RI-02" in library
    status = STATUS.read_text(encoding="utf-8")
    assert "RI-01" in status or "RI-01/RI-02" in status
