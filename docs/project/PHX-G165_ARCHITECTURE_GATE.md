# PHX-G165 Terminal Declared Package Surface Projection Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package Platform / Demo Gateway  
**规范源：** ADR-0184  
**授权：** DAL-G003 + DAL-G004（DAL-U038）；AED v1.1；cue「你决定，我要完整的强大的系统」

## 1. 门禁目标

在不打开 HARD HOLDS、不 bump 包/Alembic 的前提下，将 Terminal Product/Ops 绑定到已安装 Package surfaces/actions，并经 Operator 移交完成受治理路径。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Projection | Terminal consumes Gateway package surfaces/actions |
| Commit path | Handoff → Operator only |
| Demo seed | sample_ops + sample_product installed |
| Fixture | DEMO_* offline fallback only |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Brain/Twin enable；Cap→grant；external PSP；Const/BP rewrite |

## 3. Exit Criteria

1. ADR-0184 Accepted。  
2. Gate / Acceptance + demo seed + Terminal bind + DAL-U038 + tip/status sync 齐。  
3. `test_api_gateway_g165_*` 绿。  

见 [PHX-G165_ACCEPTANCE.md](PHX-G165_ACCEPTANCE.md)。
