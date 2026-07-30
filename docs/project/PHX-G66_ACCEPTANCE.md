# PHX-G66 Tenant IdP Federation Binding Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway  
**退出门禁：** 平台面 bind/list/unbind；可选 OIDC fail-closed；默认关闭强制；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0085 + Architecture Gate |
| B | 进程内绑定存储 + 平台 API |
| C | `EAOS_TENANT_IDP_FEDERATION` OIDC 强制 |
| D | 契约 `test_api_gateway_g66_*` |

## 2. 核心不变量

- Body 禁止 `tenant_id` / `platform_scope`；路径承载租户  
- 序列化用 `bound_tenant_id`；不回传密钥  
- 默认不强制；开启后无 active 绑定 → 403  
- 无 Alembic；无联邦 UI  

## 3. 自动化证据

- 本地完整回归：`544 passed`（`tests/contracts`）  
- Alembic head：仍为 `0026_oidc_refresh_bindings_g63`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0085 |
| Constitution Review | 通过；平台面；无租户体提升 |
| Cross-reference Review | 通过；G55/G61 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0026` |
| Gap Analysis | SQL/UI/JWT 强制、支付清算、网格 CRD 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 联邦 UI / 策略矩阵 / social login  
- SQL 适配器 / JWT 路径强制绑定  
- 网格 CRD / 多区域 / KMS  

## 6. 证据索引

- [PHX-G66 Architecture Gate](PHX-G66_ARCHITECTURE_GATE.md)
- [ADR-0085](../decisions/ADR-0085-tenant-idp-federation-binding.md)
