# ADR-0233 — OpenAPI OIDC MFA Enrollment Details Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G214  
**归属：** OpenAPI Inventory / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U087**；PO cue「充分授权…自主开发…加快」

## 背景

G210 已命名 OIDC amr/acr details。Live emit 在配置
`EAOS_OIDC_MFA_ENROLLMENT_URL` 时额外附加 `mfa_enrollment_url`，schema 未声明。

## 决策

1. `OidcAmrRequiredDetails` / `OidcAcrRequiredDetails` 文档化可选
   `mfa_enrollment_url`（uri）。  
2. `ErrorResponse.details` 同步声明该键。  
3. auth **1.3.17**；Inventory `milestone=PHX-G214`；
   `t0188_status=mount_parity_complete_oidc_mfa_enrollment_details_honest`；
   ops **1.0.33**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Changing MFA enrollment runtime behavior  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G214_ARCHITECTURE_GATE.md](../project/PHX-G214_ARCHITECTURE_GATE.md)  
