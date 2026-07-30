# PHX-G212 OpenAPI Host-Acquire Details Per-Code Shape Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory / Marketplace  
**规范源：** ADR-0231  
**授权：** DAL-G003 + DAL-G004（DAL-U085）

## 1. 门禁目标

为 host-acquire allowlist deny 闭合已知 details 形状；不开放 non-allowlist invent。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Schema | HostAcquireAllowlistDenialDetails（marketplace） |
| Inventory | G212 / ops 1.0.32 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0231 + marketplace schema + inventory + tests + DAL-U085 + tip/status 齐。  
