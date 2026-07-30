# PHX-G82 JWT eaos_roles → ExecutionContext Roles Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / ExecutionContext  
**退出门禁：** JWT `eaos_roles` → `ExecutionContext.roles` + `/v1/context`；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0101 + Architecture Gate |
| B | `ExecutionContext.roles` + JWT 解析 |
| C | serialize / body 防提升 |
| D | 契约 `test_api_gateway_g82_*` |

## 2. 核心不变量

- 缺省/dev header → `roles=[]`  
- body 不可覆盖 `roles`  
- 不写 Permission grants  

## 3. 自动化证据

- 本地完整回归：`627 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0101 |
| Constitution Review | 通过；Gateway 信任边界；无 body 提升 |
| Cross-reference Review | 通过；G37/G81 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | Permission sync、social login、MFA 注册、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Permission Kernel 按 `roles` 自动授权  
- Social login / MFA 注册 UX  
- 平台面 JWT 角色消费  

## 6. 证据索引

- [PHX-G82 Architecture Gate](PHX-G82_ARCHITECTURE_GATE.md)
- [ADR-0101](../decisions/ADR-0101-jwt-eaos-roles-execution-context.md)
