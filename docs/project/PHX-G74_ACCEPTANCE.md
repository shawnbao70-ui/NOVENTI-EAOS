# PHX-G74 OIDC Refresh Fernet Key Provider Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `env|file` 密钥提供方；`kms` fail-closed；默认 env；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0093 + Architecture Gate |
| B | env/file 密钥加载 |
| C | status `refresh_encrypt_key_provider` |
| D | 契约 `test_api_gateway_g74_*` |

## 2. 核心不变量

- 默认 `env`；`file` 需 `*_KEY_FILE`  
- 永不回传密钥材料  
- 云 KMS 适配器另批  

## 3. 自动化证据

- 本地完整回归：`576 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0093 |
| Constitution Review | 通过；Gateway 边界 |
| Cross-reference Review | 通过；G64/G65/G70 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 云 KMS、支付清算、多区域另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- AWS/GCP/Azure KMS 适配器  
- 多区域  

## 6. 证据索引

- [PHX-G74 Architecture Gate](PHX-G74_ARCHITECTURE_GATE.md)
- [ADR-0093](../decisions/ADR-0093-oidc-refresh-key-provider.md)
