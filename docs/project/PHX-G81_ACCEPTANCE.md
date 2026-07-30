# PHX-G81 OIDC Claim→Role JWT Mint Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** claim→`eaos_roles` mint；可选 require；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0100 + Architecture Gate |
| B | `oidc_claim_role` + mint `eaos_roles` |
| C | oidc status 字段 |
| D | 契约 `test_api_gateway_g81_*` |

## 2. 核心不变量

- 空配置 = 关闭  
- 不写 Permission grants  
- G79/G80 仍先于角色映射执行  

## 3. 自动化证据

- 本地完整回归：`621 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0100 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G79/G80 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | social login、MFA 注册、Permission sync、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- SQL 映射表 / Permission Kernel 自动授权  
- Social login / MFA 注册 UX  
- `ExecutionContext.roles` 产品化（见 PHX-G82）  

## 6. 证据索引

- [PHX-G81 Architecture Gate](PHX-G81_ARCHITECTURE_GATE.md)
- [ADR-0100](../decisions/ADR-0100-oidc-claim-role-mint.md)
