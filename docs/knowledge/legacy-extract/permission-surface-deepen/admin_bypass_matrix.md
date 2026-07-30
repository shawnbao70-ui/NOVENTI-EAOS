# 管理员绕过矩阵（Admin Bypass Matrix）— Legacy Knowledge

**Evidence strength:** Strong for checker and sampled route gates; role population in production is UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

Legacy `has_permission` 对规范化后的 `Admin` 与 `Super Admin` 无条件返回 allow。此绕过仅在 route/template/service 实际调用 checker 时发生；无 gate 的路由不是“管理员绕过”，而是所有可达主体都绕过 permission matrix。Manager、Finance Admin、System Admin 等相似名字不属于已确认 privileged role。

## 2. Admin Bypass Matrix

| Surface | Non-admin policy | Admin/Super Admin | No-gate implication |
|---------|------------------|-------------------|---------------------|
| Permission Center | view/edit row | unconditional allow | N/A |
| Users list | Users view + exact session role `Admin` | checker allows, but exact-role second gate may reject Super Admin | some edit/add/delete gaps |
| Roles | Roles action + protected-role rules | allow checker; protected delete still blocked | route-specific |
| Quote Approve | Quotes edit | allow | N/A |
| Quote status | no route check | same as any reachable user | universal hole |
| Quote→SO | UI Sales add only | UI button allowed | endpoint universal hole |
| SO Approve | Sales Orders edit | allow | N/A |
| Create DO | UI Delivery add only | UI allowed | endpoint universal hole |
| Convert DO | Sales Orders edit | allow | N/A |
| DO Ship/Complete/Reopen | Delivery edit | allow | GET risk remains |
| Inventory Adjust/Delete | Inventory edit/delete | allow | GET delete risk remains |
| Finance receipt/post AR | resource action | allow | some finance routes no gate |
| Approval Center decision | no gate | same as any reachable user | universal hole |
| Brand save | explicit admin role family | allowed | differs from document designer |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| ABM-R1 | privileged role 比较先 strip 再 lower | case/space variants accepted |
| ABM-R2 | 仅 `admin`、`super admin` 两值确认 privileged | 类似名称不自动 privileged |
| ABM-R3 | username 存在时 checker 回查 users.role | DB role 优先于 session role |
| ABM-R4 | DB 无 role 才回退 session role | stale session 可成为 fallback |
| ABM-R5 | privileged check 发生在 permission-row lookup 前 | row deny 对管理员无效 |
| ABM-R6 | 管理员所有已定义 action 都 allow | view/add/edit/delete/export/import/print/approve |
| ABM-R7 | 未知 action 对管理员也先 allow | bypass 不受 action vocabulary 限制 |
| ABM-R8 | 无 username 时 privileged session role 也不生效 | principal username prerequisite |
| ABM-R9 | route 不调用 checker 时 role 无意义 | 普通用户和管理员同样可达 |
| ABM-R10 | UI checker 同样绕过 | 管理员看到所有 gated controls |
| ABM-R11 | service业务前置条件不会因 checker bypass 自动跳过 | existence/status/stock 可仍阻断 |
| ABM-R12 | protected role 删除规则是额外业务 guard | 管理员未必可删 Admin/Super Admin |
| ABM-R13 | role_permissions matrix 仍可展示 privileged role | 展示 row 不代表执行限制 |
| ABM-R14 | module alias 不影响 privileged allow | alias lookup 被跳过 |
| ABM-R15 | Manager 未被 checker 特权化 | 依赖普通 matrix |
| ABM-R16 | Brand 的局部 admin role list 可能比 checker 更宽/不同 | policy source 漂移 |
| ABM-R17 | Admin bypass 不解决 owner/tenant scope | 反而明确跨对象全局访问 |
| ABM-R18 | Admin bypass 不解决 GET/CSRF 风险 | privileged session 仍可被诱导 |
| ABM-R19 | audit actor 若 handler 无 request 则不可归因 | admin 身份不会被记录 |
| ABM-R20 | EAOS 不应迁移 role-string unconditional bypass | 应使用显式、可审计 break-glass/capability |
| ABM-R21 | `/users`、`/roles` 存在 checker 后的 exact `session.role=="Admin"` 二次门 | Super Admin 可通过 checker 却被后门禁拒绝 |
| ABM-R22 | Manager 的 `data_scope`/广范围来自 seed 或服务硬编码 | 不是 privileged checker bypass |

## 4. Process

1. 从 request session 取 username。
2. 按 username 回查当前 DB role；无结果时回退 session role。
3. role 规范化。
4. 若为 Admin/Super Admin，立即 allow。
5. 否则按 module alias 找 permission row，再按 action column。
6. 路由继续执行自己的业务校验；若路由从未调用 checker，则以上流程不存在。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| ABM-V1 | username 必须存在 | Hard |
| ABM-V2 | DB role 优先 session role | Hard |
| ABM-V3 | privileged role trim/lower | Hard |
| ABM-V4 | privileged role 只允许两个名字 | Hard |
| ABM-V5 | permission row deny 可约束管理员 | Explicitly bypassed |
| ABM-V6 | unknown action 默认 deny | True only non-admin |
| ABM-V7 | protected roles 不可删除 | Hard in role path |
| ABM-V8 | role with users 不可删除 | Hard in role path |
| ABM-V9 | all admin actions audited | Missing/inconsistent |
| ABM-V10 | privileged access requires re-auth/MFA | Missing/UNKNOWN |
| ABM-V11 | admin scope tenant-bound | Missing/UNKNOWN |
| ABM-V12 | no-gate endpoint restricted to admin | False |
| ABM-V13 | Super Admin 与 Admin 在所有独立门禁等价 | False |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| Admin | privileged role string |
| Super Admin | privileged role string |
| Manager | ordinary role unless rows grant actions |
| users.role | primary runtime role |
| session role | fallback role |
| privileged_role | unconditional checker allow |
| role_permissions | ignored for privileged roles |
| module alias | non-admin lookup expansion |
| unknown action | non-admin deny, privileged allow |
| protected role | role deletion restriction |
| user count | role deletion dependency |
| Permission Center matrix | configuration/display, not admin constraint |
| no-gate route | universal permission bypass |
| business guard | non-RBAC condition after allow |
| object scope | not encoded in role matrix |
| break-glass | absent as explicit audited construct |
| exact-role gate | checker 外大小写敏感的平行 ACL |
| data_scope | persisted/displayed scope，未由 checker执行 |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| privileged | checker short-circuit allow |
| ordinary | matrix-evaluated role |
| fallback role | session role when DB role unavailable |
| protected | cannot be deleted, separate from runtime bypass |
| universal hole | no checker for any role |
| break-glass | desired governed escalation, not observed legacy state |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| production users assigned privileged names | auth repository/schema/seed only |
| role rename/case variants in live DB | role management/runtime DDL |
| Admin MFA/re-auth policy enforcement | login center/core auth/security |
| admin action audit completeness | routers/services/audit reports |
| Admin tenant scope | tenant helpers/repositories |
| `System Admin`/localized names intended privilege | permission module catalog/templates |
| stale session role after DB user removal | checker/session/auth service |
| reverse proxy privileged path rules | deployment docs |
| Brand custom admin list full equivalence | brand residual/templates |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `core/permission/checker.py` | role resolution and bypass |
| `core/permission/module_catalog.py` | matrix vocabulary |
| `core/auth/session.py` | session role/username |
| `core/auth/repository.py` | user/role/permission persistence |
| `apps/permission_center/v14_residual.py` | matrix self-protection |
| `templates/permission_center.html` | privileged display |
| `apps/platform/org_pages.py` | role management surfaces |
| `apps/platform/v14_residual.py` | user/role route inconsistencies |
| `apps/quotation/router.py` | quote policy examples |
| `apps/sales/router.py` | guarded and no-gate examples |
| `apps/inventory/router.py` | inventory/delivery policy |
| `apps/finance/router.py` | finance mixed coverage |
| `apps/approval/router.py` | universal decision hole |
| `apps/brand_center/v14_residual.py` | local admin-role policy |
| `database/v151_permission_center_schema.py` | permission metadata |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | EAOS risk baseline |
| `docs/knowledge/legacy-extract/platform-obs/identity_obs.md` | EAOS identity observation |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
