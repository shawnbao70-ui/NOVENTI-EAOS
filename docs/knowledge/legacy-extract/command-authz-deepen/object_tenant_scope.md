# 对象与租户范围检查（Object / Tenant Scope）

**Evidence strength:** Strong for sampled SQL and tenant helper semantics; production DB RLS UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页区分 coarse module RBAC、owner scope 与 tenant scope。Legacy 列表常按 salesperson/owner 过滤，但详情和 command 按裸 ID 读取/更新；tenant helper 是 repository opt-in，且匹配当前 tenant 之外还读取 `default`、NULL、空字符串 legacy 行，不能解释为严格隔离。

## 2. Domain Scope Matrix

| Domain | List scope | Detail scope | Write scope | Tenant posture |
|---|---|---|---|---|
| Customer | ordinary sales按 salesperson/owner | detail 未见同 owner复验 | follow-up/delete by ID | inconsistent |
| Quote | role/owner过滤部分存在 | detail主要 module view | status/convert by quote ID | weak |
| Sales Order | ordinary sales按 salesperson | detail module view only | status/create DO by SO ID | weak |
| Receipt | list按销售归属 | detail Receipts view | create/update by IDs | weak |
| Delivery Order | list/KPI scope不一致 | module view | create/complete/reopen by ID | weak |
| Inventory | generally global module view | ID detail | adjust/delete by ID | tenant helper not universal |
| Finance AR/AP | mixed joins/role filters | module-level | source ID writes | weak |
| Approval | list user semantics partial | record by ID | decision by ID, no approver | critical |
| User/Role | admin-oriented list | ID-based | edit/delete ID | tenant scope absent |
| Tenant Center | metadata tenant APIs | resolver/profile | admin gate not proven | framework only |

## 3. Business Rules

| ID | Rule |
|---|---|
| OTS-R01 | module `view/edit` permission 不表达“哪一条对象”。 |
| OTS-R02 | 列表 owner filter 不自动传播到 detail/action。 |
| OTS-R03 | Sales list 的 salesperson 限制与 SO detail 只查 module view 并存。 |
| OTS-R04 | Receipt list 销售归属过滤不等于 Receipt detail object policy。 |
| OTS-R05 | Customer detail/follow-up 可按 ID 访问而未复验 owner。 |
| OTS-R06 | Quote status/Convert SO 只持 quote ID，且无 principal gate。 |
| OTS-R07 | Create DO 只持 SO ID，未校验 SO owner/tenant。 |
| OTS-R08 | Approval decision 未比较当前 user 与 assigned approver。 |
| OTS-R09 | Admin/Manager 常被服务层硬编码为全量范围。 |
| OTS-R10 | `role_permissions.data_scope` 未由 central checker enforce。 |
| OTS-R11 | 当前 tenant 缺失时 tenant context 回退 `default`。 |
| OTS-R12 | `tenant_match_sql` 接受 exact tenant 以及 default/null/empty。 |
| OTS-R13 | dual-read 是迁移兼容，不是隔离保证。 |
| OTS-R14 | `append_tenant_filter` 需要 repository 主动调用。 |
| OTS-R15 | `table_has_tenant=False` 可显式跳过 filter。 |
| OTS-R16 | `stamp_tenant` 只在调用者使用时给 outgoing values 补 tenant。 |
| OTS-R17 | 裸 `UPDATE ... WHERE id=?` 不自动获得 tenant predicate。 |
| OTS-R18 | tenant column 存在不证明所有读写 scoped。 |
| OTS-R19 | list/KPI/detail 使用不同 query 时可产生范围漂移。 |
| OTS-R20 | EAOS 必须使用授权查询，将 tenant+object scope 与 repository command 绑定。 |
| OTS-R21 | `apps/*/repository.py` 主路径未检出 `tenant_id` 引用。 |
| OTS-R22 | DO list 对普通销售有 owner filter，而 Delivery Dashboard 聚合为全局。 |
| OTS-R23 | Customer detail route 未见 module view gate且 repository 只按 ID。 |

## 4. Process

### 4.1 Legacy common path

列表 query按角色附加 owner predicate → 用户获得/猜测 ID → detail/command按 ID 查询 → module permission（若有）→ 未复验 owner/tenant → 返回或写入。

### 4.2 Tenant helper path

从 request/session建立 tenant context（缺失=`default`）→ repository选择调用 `append_tenant_filter` → predicate接受 exact/default/null/empty → query。未调用 helper 的 repository 不受其约束。

## 5. Validation

| ID | Validation | Legacy |
|---|---|---|
| OTS-V01 | every get-by-id binds tenant | Missing/inconsistent |
| OTS-V02 | every write binds tenant | Missing/inconsistent |
| OTS-V03 | ordinary user object owner matches principal | Missing/inconsistent |
| OTS-V04 | list/detail/action share one scope policy | Missing |
| OTS-V05 | assigned approver matches decision actor | Missing |
| OTS-V06 | missing tenant context must deny | Violated: default fallback |
| OTS-V07 | no cross-tenant default/null dual-read | Violated by compatibility helper |
| OTS-V08 | tenant stamp mandatory on insert | Opt-in |
| OTS-V09 | data_scope centrally enforced | Missing |
| OTS-V10 | Admin tenant reach is bounded/audited | Missing/UNKNOWN |
| OTS-V11 | existence errors do not leak inaccessible IDs | Inconsistent |
| OTS-V12 | KPI scope equals list/detail scope | Missing/inconsistent |

## 6. Data Semantics

| Concept | Meaning |
|---|---|
| module RBAC | coarse resource/action permission |
| object scope | permission over one record ID |
| owner scope | salesperson/creator/team relationship |
| tenant scope | company/tenant data boundary |
| authorized query | query embedding scope predicate |
| list filter | presentation/query subset only |
| `data_scope` | role metadata not centrally consumed |
| current tenant | context string, default fallback |
| exact tenant row | row tenant_id equals context |
| legacy row | default/null/empty tenant_id |
| dual-read | current tenant plus legacy rows |
| `append_tenant_filter` | opt-in SELECT transformer |
| `stamp_tenant` | opt-in outgoing value enrichment |
| naked ID update | `WHERE id=?` without owner/tenant |
| IDOR | cross-object access via predictable/known ID |
| global role | service convention for Admin/Manager, not tenant policy |
| repository main path | raw cursor SQL without tenant helper |
| KPI scope drift | dashboard aggregate broader than list |

## 7. State Vocabulary

| State | Meaning |
|---|---|
| scoped | tenant/owner predicate enforced in data access |
| module-only | checker passes but object scope absent |
| dual-read | compatibility visibility across tenant+legacy rows |
| default tenant | fallback context, not anonymous denial |
| object-scope hole | list restricted, detail/action broader |

## 8. UNKNOWN + 已查路径

| UNKNOWN | 已查路径 |
|---|---|
| PostgreSQL production RLS | adapters/migrations/docs |
| actual tenant_id population rate | schemas/scripts; production data unavailable |
| all repositories using append_tenant_filter | core/apps searches |
| all inserts using stamp_tenant | core/apps searches |
| Manager intended owner/data scope | services/module docs |
| cross-tenant Admin policy | tenant center/permission center |
| team/department hierarchy enforcement | platform org/sales services |
| object-not-found response normalization | sampled routers/services |
| default/null rows migration completion | migrations/reports |
| Permission Assessment data-scope activation ever shipped | `docs/reports/Permission_Assessment_Report.md` (P-M01 unused tables) |
| Tenant bridge dual-read retirement schedule | `docs/reports/V41_V14_Tenant_Bridge_Vol2_Report.md` |

## 9. Evidence Table

| Read-only path | Evidence |
|---|---|
| `core/database/tenant_scope.py` | dual-read and opt-in helper |
| `core/runtime/tenant_context.py` | default tenant context |
| `core/security/middleware.py` | session-to-tenant context |
| `core/permission/checker.py` | no object/data_scope enforcement |
| `core/auth/repository.py` | role permission metadata |
| `apps/customer/services.py` | customer owner/list/detail behavior |
| `apps/customer/router.py` | detail/follow-up/delete actions |
| `apps/quotation/router.py` | quote ID commands |
| `apps/quotation/services.py` | quote fetch/state |
| `apps/sales/services.py` | sales owner list and ID detail/convert |
| `apps/sales/router.py` | SO ID commands |
| `apps/finance/services.py` | receipt list/detail scope |
| `apps/finance/router.py` | receipt/AR actions |
| `apps/inventory/services.py` | DO ID actions |
| `apps/inventory/services.py` | owner-filtered DO list vs global dashboard |
| `apps/_tenant_query.py` | narrow scoped/stamp wrappers |
| `core/database/repository_base.py` | opt-in tenant_fetch helpers |
| `apps/approval/services.py` | approval decision without assigned actor condition |
| `apps/tenant_center/services.py` | tenant metadata framework |
| `database/v41_tenant_column_schema.py` | additive tenant columns |
| `docs/knowledge/legacy-extract/platform-obs/identity_obs.md` | tenant observation cross-reference |
| `docs/knowledge/legacy-extract/permission-surface-deepen/ui_vs_server_rbac.md` | object-scope risk cross-reference |
| `docs/reports/Permission_Assessment_Report.md` | data_scope/field permission tables unused (0 queries) |
| `docs/reports/V41_V14_Tenant_Bridge_Vol2_Report.md` | tenant bridge report; dual-read intent vs isolation |
| `runtime/v14/legacy_support.py` | users/roles/role_permissions seed; no object-scope enforcement |
| `templates/` (list vs detail CTAs) | list visibility ≠ detail/object authorization |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
