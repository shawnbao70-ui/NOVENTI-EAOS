# PHX-G214 OpenAPI OIDC MFA Enrollment Details Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory / Auth  
**规范源：** ADR-0233  
**授权：** DAL-G003 + DAL-G004（DAL-U087）

## 1. 门禁目标

为 OIDC amr/acr denial 的 MFA enrollment URL 键闭合 schema honesty。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Schema | mfa_enrollment_url on Amr/Acr + ErrorResponse.details |
| Inventory | G214 / ops 1.0.33 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0233 + auth schemas + inventory + tests + DAL-U087 + tip/status 齐。  
