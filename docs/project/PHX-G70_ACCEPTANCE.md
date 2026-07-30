# PHX-G70 OIDC Refresh Re-encrypt On Read Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** 可选读时迁主密钥；默认 off；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0089 + Architecture Gate |
| B | `get_oidc_session` 检测 + re-seal |
| C | status `refresh_reencrypt_on_read` |
| D | 契约 `test_api_gateway_g70_*` |

## 2. 核心不变量

- `EAOS_OIDC_REFRESH_REENCRYPT_ON_READ` 默认 off  
- 仅加密开启时生效；`pop` 不重写  
- 主密钥可解则不写；仅旧密钥可解则迁主密钥  

## 3. 自动化证据

- 本地完整回归：`560 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0089 |
| Constitution Review | 通过；Gateway/Persistence |
| Cross-reference Review | 通过；G64/G65 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | KMS/批量迁移、支付清算、网格 CRD 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 外部 KMS / 批量离线迁移  
- 网格 CRD / 多区域  

## 6. 证据索引

- [PHX-G70 Architecture Gate](PHX-G70_ARCHITECTURE_GATE.md)
- [ADR-0089](../decisions/ADR-0089-oidc-refresh-reencrypt-on-read.md)
