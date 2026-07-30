# PHX-G153 Foundation Ops / Compatibility / Checklist Hygiene Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation；docs-only）  
**归属：** Phoenix Governance / Foundation release hygiene  
**规范源：** ADR-0172  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U025**

## 1. 门禁目标

对齐 Foundation `0.2.1` 运维与发布卫生文档与已验收的 G145–G152 表面：Runbook Smoke/Out-of-scope、Compatibility additive notes、Release Checklist Manifest milestones — **不**打开 live mint / 支付 / Brain / Twin。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Docs-only release hygiene |
| Runbook | Milestones G144–G153；stub 503 + Held fences |
| Compatibility | Baseline `0.2.1` / `0029`；G145–G152 additive |
| Checklist | Manifest G145–G152 + recent Acceptance |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Live mint；Role→grant mint；支付；Brain execute；Twin authorize；新 Alembic |

## 3. Exit Criteria

1. ADR-0172 Accepted。  
2. Gate / Acceptance + three release docs + Manifest G153 + DAL-U025 + status sync 齐。  
3. `test_docs_g153_foundation_ops_hygiene.py` 与相关 DAL / G144 / G152 合约绿。  

见 [PHX-G153_ACCEPTANCE.md](PHX-G153_ACCEPTANCE.md)。
