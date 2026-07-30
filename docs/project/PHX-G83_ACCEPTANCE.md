# PHX-G83 Opt-in Context Roles Evaluate Grant Map Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Permission Kernel  
**退出门禁：** 可选 role→(type,action) map 参与 evaluate；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0102 + Architecture Gate |
| B | `role_grant_map` + evaluate/explain |
| C | evidence `matched_roles` + HTTP explanation |
| D | 契约 `test_permission_g83_*` / `test_api_gateway_g83_*` |

## 2. 核心不变量

- 空 map = 关闭  
- deny > role allow  
- 不写 DB grants  

## 3. 自动化证据

- 本地完整回归：`635 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0102 |
| Constitution Review | 通过；opt-in；无 body 提升 roles |
| Cross-reference Review | 通过；G22/G82 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | Role 表、grant 写入、social、MFA、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role 目录 / 自动写 grant  
- Social login / MFA 注册 UX  
- 平台面 JWT 角色消费  

## 6. 证据索引

- [PHX-G83 Architecture Gate](PHX-G83_ARCHITECTURE_GATE.md)
- [ADR-0102](../decisions/ADR-0102-permission-role-grant-map.md)
