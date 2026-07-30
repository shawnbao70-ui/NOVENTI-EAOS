# Command Authorization Deepen — Legacy Knowledge Pack

## Purpose

本包从 command 角度深挖 EZAM CRM 9.0 的服务端鉴权：写路由覆盖、对象/租户范围、GET mutation 以及特权覆盖审计。重点不在“是否有权限页面”，而在每次业务事实改变时是否绑定 principal、policy、object、tenant、intent 和 audit。

## Modules

- [server_route_coverage.md](server_route_coverage.md)：关键写路由服务端鉴权覆盖矩阵。
- [object_tenant_scope.md](object_tenant_scope.md)：列表、详情、动作的对象/租户范围。
- [get_mutation_surface.md](get_mutation_surface.md)：GET 写操作清单、gate 与副作用。
- [audited_override.md](audited_override.md)：Admin/Super Admin 覆盖是否形成可审计 override。
- [INDEX.md](INDEX.md)：覆盖核验与跨包关系。

## Evidence Posture

- **Strong:** canonical router method/signature、checker bypass、CSRF safe methods、tenant helper、采样 service SQL/状态 guard、Brand unlock audit。
- **Medium:** standard bootstrap route winner、domain operation log 完整性。
- **Weak / UNKNOWN:** production proxy、alternative startup、DB RLS、实际 tenant 数据、外部 SIEM 与日志保留。

## Critical Honesty Findings

1. Checker 被调用时 default-deny；应用整体不是 default-deny，因为 route/service 接线是 opt-in。
2. 关键 writes 存在 Strong、Partial、Critical gap 三类；同模块也不能推断统一 coverage。
3. module RBAC 不表达 object owner、tenant、assigned approver 或 source state。
4. tenant helper 是 opt-in dual-read，允许 exact tenant 与 default/null/empty legacy rows。
5. 大量 GET mutation 绕过 CSRF；有 RBAC 或状态幂等也不能修复 HTTP intent 风险。
6. Admin/Super Admin bypass 本身不产生日志；普通业务日志无法证明发生了 override。
7. Brand Super Admin unlock 是少数显式记录 actor/reason/before-after 的特权操作。

## Hard Boundaries

- 只记录 Legacy 事实与 EAOS 迁移约束，不复制源码。
- 交叉引用 `permission-surface-deepen`、`risk-catalog`、`ship-complete-deepen`、`platform-obs`，不改其正文。
- UI 隐藏、browser confirm、Human Confirm 均不单独等价于 authorization。
- 不把业务存在性/状态校验误写成主体授权。
- 不打开 CRUD，不创建 G 号，不修改本包之外文件。

## Read-only Roots

- Legacy: `H:\Workspace\EZAM_CRM - 9.0\`
- EAOS cross-references: `docs/knowledge/legacy-extract/{permission-surface-deepen,risk-catalog,ship-complete-deepen,platform-obs}/`
