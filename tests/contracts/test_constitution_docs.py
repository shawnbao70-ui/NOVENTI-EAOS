"""Constitution v2.1 and Smart Terminal documentation contracts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONSTITUTION = ROOT / "docs" / "constitution"


def test_constitution_index_contains_book00_through_book23() -> None:
    index = (CONSTITUTION / "README.md").read_text(encoding="utf-8")
    for number in range(24):
        book = f"BOOK{number:02d}"
        assert (CONSTITUTION / f"{book}.md").is_file()
        assert f"[{book}.md]({book}.md)" in index


def test_constitution_markdown_links_resolve() -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for document in CONSTITUTION.glob("*.md"):
        content = document.read_text(encoding="utf-8")
        for target in link_pattern.findall(content):
            if "://" in target or target.startswith("#"):
                continue
            path_part = target.split("#", 1)[0]
            assert (document.parent / path_part).resolve().exists(), (
                f"{document.name} has broken link: {target}"
            )


def test_book23_preserves_terminal_ownership_boundaries() -> None:
    book = (CONSTITUTION / "BOOK23.md").read_text(encoding="utf-8")
    assert "独立受治理交互层" in book
    assert "业务真相源" in book
    assert "不得直接读写数据库" in book
    assert "Permission Kernel 是授权决策真相源" in book
    assert "Workflow Kernel 是审批与路由真相源" in book
    assert "Enterprise Brain" in book and "不因此取得执行权" in book


def test_ai_taxonomy_is_consistent_across_normative_books() -> None:
    for name in ("BOOK03.md", "BOOK19.md", "BOOK22.md"):
        content = (CONSTITUTION / name).read_text(encoding="utf-8")
        for term in ("AI Employee", "Agent", "Digital Human", "AI Assistant", "Smart Terminal"):
            assert term in content


def test_architecture_uses_constitutional_and_core_kernel_distinction() -> None:
    architecture = (
        ROOT / "docs" / "architecture" / "EAOS_ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    blueprint = (
        ROOT / "docs" / "blueprint" / "KERNEL_BLUEPRINT.md"
    ).read_text(encoding="utf-8")
    terminal = (
        ROOT / "docs" / "blueprint" / "SMART_TERMINAL_BLUEPRINT.md"
    ).read_text(encoding="utf-8")
    assert "Constitutional Kernel" in architecture
    assert "Core Kernel" in architecture
    assert "Constitutional Kernel" in blueprint
    assert "独立受治理交互层" in terminal


def test_all_constitution_books_use_v21_normative_metadata() -> None:
    for number in range(24):
        content = (CONSTITUTION / f"BOOK{number:02d}.md").read_text(encoding="utf-8")
        assert "**版本：** EAOS Charter v2.1" in content
        assert "**状态：** 生效" in content
        assert "**阶段：** PHX-001" not in content
        assert "正文已充实 — PHX-001" not in content


def test_risk_taxonomy_uses_strictest_applicable_control() -> None:
    for name in ("BOOK05.md", "BOOK07.md", "BOOK10.md", "BOOK13.md", "BOOK17.md"):
        content = (CONSTITUTION / name).read_text(encoding="utf-8")
        assert "高影响" in content
        assert "高风险" in content
        assert "商业敏感" in content
        assert "最严格控制" in content


def test_knowledge_and_event_have_unique_technical_ownership() -> None:
    book19 = (CONSTITUTION / "BOOK19.md").read_text(encoding="utf-8")
    kernel_blueprint = (
        ROOT / "docs" / "blueprint" / "KERNEL_BLUEPRINT.md"
    ).read_text(encoding="utf-8")
    event_blueprint = (
        ROOT / "docs" / "blueprint" / "EVENT_BLUEPRINT.md"
    ).read_text(encoding="utf-8")
    assert "Knowledge Kernel | Shared Platform Capability" in book19
    assert "Knowledge Governance Port（非 Core 域）" in kernel_blueprint
    assert "规范技术层是 Shared Platform Capability" in event_blueprint
