# 特权覆盖与可审计性（Audited Override）

**Evidence strength:** Strong for checker bypass and sampled audit writes; deployment log retention UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页判断 Admin/Super Admin 的授权短路是否被识别为“override”，并是否记录 actor、target、reason、before/after、time、tenant 与 re-auth。结论：central checker 直接 return True，不产生 override event；业务 command 即使另写 operation/history，也通常只记录普通动作，无法证明该动作依赖特权覆盖。Enterprise Brand 的 Super Admin unlock 是少数显式命名并记录 actor/reason/before-after 的例外。

## 2. Override / Audit Matrix

| Surface | Override mechanism | Audit | Honest result |
|---|---|---|---|
| `has_permission` Admin/Super Admin | unconditional short-circuit | none in checker | unaudited privilege decision |
| Permission Center admin edit | checker bypass | resource update path may log inconsistently | no override reason |
| User add | checker bypass or row grant | operation log actor/action | not marked override |
| User edit/delete | bypass/no gate | edit weak; delete none | incomplete |
| Quote/SO Type A | bypass + Human Confirm | actor may be logged in business flow | intent, not override audit |
| DO Ship/Post AR | bypass + Human Confirm | actor passed | business audit, no bypass marker |
| Approval decision | no gate | approval history operator | unauthorized path can look audited |
| Expense approve | no gate | `approve_by='BOSS'` | actor label is not principal |
| Receipt create | bypass or grant | write_log actor | no reason/before-after |
| Complete/Reopen | bypass + service gate | no observed operation log | unaudited |
| Brand Super Admin unlock | exact role gate | JSON history + audit actor/reason/old/new | strongest explicit override |
| no-gate routes | none | varies | cannot call it privileged override |

## 3. Business Rules

| ID | Rule |
|---|---|
| AOV-R01 | Admin/Super Admin bypass occurs inside checker before permission-row lookup. |
| AOV-R02 | Checker does not emit an audit event on bypass. |
| AOV-R03 | Bypass does not require reason, ticket, expiry or second approver. |
| AOV-R04 | Bypass does not require re-authentication or MFA. |
| AOV-R05 | A later business log cannot prove checker would otherwise deny. |
| AOV-R06 | No-gate command is not an override; all reachable principals skip policy. |
| AOV-R07 | Request-less command cannot reliably record authenticated actor. |
| AOV-R08 | Approval history records operator but decision route has no approver/RBAC gate. |
| AOV-R09 | Audit presence therefore does not prove authorization correctness. |
| AOV-R10 | `approve_by='BOSS'` and actor=`SYSTEM` are labels, not principal evidence. |
| AOV-R11 | Human Confirm records intent in selected Type A flows, not privileged justification. |
| AOV-R12 | Complete/Reopen use privileged-capable checker but lack observed reason/audit. |
| AOV-R13 | Admin bypass does not preserve denied permission row or policy decision context. |
| AOV-R14 | Exact `session.role=="Admin"` gates are parallel ACL, not audited override. |
| AOV-R15 | Super Admin Brand unlock is explicit privileged operation. |
| AOV-R16 | Brand unlock stores actor, fixed reason, old/new and history time. |
| AOV-R17 | Brand audit uses JSON/file-backed records; retention/integrity differs from DB logs. |
| AOV-R18 | Brand audit read endpoint authorization and tenant scope require separate review. |
| AOV-R19 | Central operation logs are command-specific opt-in dependencies. |
| AOV-R20 | EAOS must distinguish policy allow, deny, override request and override approval. |
| AOV-R21 | Human Confirm 对 privileged role 没有豁免，但它仍不是 re-auth。 |
| AOV-R22 | SO Approve 接收 actor 参数但未见等价 operation log 消费。 |
| AOV-R23 | `security_audit_logs` helper 未见 active 调用，表存在不证明覆盖。 |
| AOV-R24 | V15.1 Audit Center registry/rules/events/logs 以 metadata/implemented=0 为主。 |
| AOV-R25 | `demo`/`System`/`admin` fallback actor 可污染审计归因。 |

## 4. Process

### 4.1 Ordinary privileged bypass

Request → resolve DB/session role → `privileged_role` true → allow immediately → command executes → optional business log. No durable record says permission row was bypassed, why, for how long, or under whose authorization.

### 4.2 Explicit Brand unlock exception

POST unlock → exact Super Admin role check → actor from request → reset lock state → append history with action/time/actor → record audit with fixed reason and old/new values.

## 5. Validation

| ID | Validation | Legacy |
|---|---|---|
| AOV-V01 | override requires authenticated principal | Checker yes; no-gate routes no |
| AOV-V02 | override requires explicit capability | Missing; role string bypass |
| AOV-V03 | override requires reason | Missing except fixed Brand reason |
| AOV-V04 | override requires target/object scope | Missing/inconsistent |
| AOV-V05 | override requires tenant scope | Missing/inconsistent |
| AOV-V06 | override records policy originally denied | Missing |
| AOV-V07 | override records before/after | Missing broadly; Brand yes |
| AOV-V08 | override requires re-auth/MFA | Missing/UNKNOWN |
| AOV-V09 | override expires / one-time intent | Missing |
| AOV-V10 | override is immutable/tamper-evident | Missing/UNKNOWN |
| AOV-V11 | audit actor cannot be hardcoded | Violated |
| AOV-V12 | audit endpoint itself authorized | Inconsistent/UNKNOWN |

## 6. Data Semantics

| Concept | Meaning |
|---|---|
| privileged bypass | checker short-circuit for Admin/Super Admin |
| override | explicit exception to a denied policy; not modeled centrally |
| ordinary allow | permission row grants action |
| no-gate | no policy decision at all |
| actor | authenticated subject attributed to action |
| operator | approval history text field |
| reason | justification; often absent or fixed |
| before/after | changed values needed for audit reconstruction |
| Human Confirm | intent acknowledgement |
| re-auth | fresh identity proof; not observed |
| break-glass | time-bound emergency override; not modeled |
| operation log | optional domain write_log sink |
| approval history | decision action/operator/time record |
| hardcoded actor | SYSTEM/BOSS label |
| brand audit | file-backed tenant-keyed event collection |
| override marker | absent indicator that bypass was used |
| tenant key | Brand audit partition input |
| security audit schema | table/helper presence without active write coverage |
| audit catalog | metadata registry, not proof of runtime events |
| fallback actor | placeholder identity used when request identity is absent |

## 7. State Vocabulary

| State | Meaning |
|---|---|
| allowed | checker or parallel ACL permits |
| denied | checker returns false |
| bypassed | privileged role returns allow before row |
| unguarded | no policy evaluation |
| overridden | explicit denied-policy exception; generally absent |
| break-glass | governed emergency state; UNKNOWN/not modeled |

## 8. UNKNOWN + 已查路径

| UNKNOWN | 已查路径 |
|---|---|
| central logs capture every checker call | checker/audit/logging searches |
| production log retention/immutability | config/reports/log services |
| Admin MFA/re-auth enforcement | login center/core auth/security |
| Brand audit endpoint server authorization | enterprise branding routes/service |
| Brand JSON concurrent-write/tamper controls | audit/service/config |
| operation_logs tenant scope | schemas/repositories |
| external SIEM ingestion | integrations/deployment docs |
| override reason UI outside Brand | templates/routes searches |
| actual use of hardcoded actors in production | finance services/runtime |

## 9. Evidence Table

| Read-only path | Evidence |
|---|---|
| `core/permission/checker.py` | bypass without audit |
| `core/auth/routes.py` | user log/gate contrast |
| `core/auth/repository.py` | user/role persistence |
| `apps/permission_center/v14_residual.py` | privileged matrix management |
| `apps/approval/router.py` | operator from request but no gate |
| `apps/approval/services.py` | approval history insert |
| `apps/approval/repository.py` | history fields/commit |
| `apps/finance/router.py` | actor passing |
| `apps/finance/services.py` | operation logs and hardcoded BOSS |
| `apps/sales/router.py` | Type A actor/Human Confirm |
| `apps/inventory/router.py` | Ship/Post AR actor and Complete/Reopen |
| `apps/inventory/services.py` | action-specific audit behavior |
| `v15/enterprise_branding/routes.py` | exact Super Admin unlock gate |
| `v15/enterprise_branding/service.py` | unlock history/audit |
| `v15/enterprise_branding/audit.py` | actor/reason/old/new JSON schema |
| `core/security/middleware.py` | no privileged re-auth |
| `apps/login_center/services.py` | policy metadata vs runtime |
| `database/v151_audit_center_schema.py` | audit catalog metadata/implemented flags |
| `apps/audit_center/repository.py` | catalog persistence boundary |
| `runtime/v14/legacy_support.py` | operation/security audit helpers and fallbacks |
| `docs/knowledge/legacy-extract/permission-surface-deepen/admin_bypass_matrix.md` | bypass authority cross-reference |
| `docs/knowledge/legacy-extract/permission-surface-deepen/opt_in_checks.md` | opt-in enforcement cross-reference |
| `docs/reports/Permission_Assessment_Report.md` | privileged bypass documented; advanced audit scopes unused |
| `runtime/v14/legacy_support.py` | operation_logs + security_audit_logs DDL; write path opt-in |
| `templates/` (Type A approve pages) | Human Confirm UI ≠ override reason/audit |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
