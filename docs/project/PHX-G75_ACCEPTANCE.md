# PHX-G75 OIDC Refresh KMS Key Provider Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `provider=kms` + `http|aws|gcp|azure`；云 SDK 可选；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0094 + Architecture Gate |
| B | http / aws / gcp / azure 薄后端 |
| C | status `refresh_encrypt_kms_backend` |
| D | 契约 `test_api_gateway_g75_*` |

## 2. 核心不变量

- `kms` 须显式 `KMS_BACKEND`  
- 云 SDK 未安装 fail-closed  
- 永不回传密钥材料；进程内缓存密钥环  

## 3. 自动化证据

- 本地完整回归：`580 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0094 |
| Constitution Review | 通过；Gateway 边界；默认无重依赖 |
| Cross-reference Review | 通过；G64/G65/G70/G74 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 多区域 KMS、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 多区域 KMS 复制 / 自动轮换作业  
- 将云 SDK 纳入默认依赖  

## 6. 证据索引

- [PHX-G75 Architecture Gate](PHX-G75_ARCHITECTURE_GATE.md)
- [ADR-0094](../decisions/ADR-0094-oidc-refresh-kms-provider.md)
