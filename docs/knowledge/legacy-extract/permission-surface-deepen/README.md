# Permission Surface Deepen — Legacy Knowledge Pack

## Purpose

本包深挖 Legacy 权限“表面”与运行时执行之间的距离：UI 按钮隐藏、router/service RBAC、Convert/DO 双路由、管理员短路，以及逐路由 opt-in 检查。

## Modules

- [UI vs Server RBAC](ui_vs_server_rbac.md)：UI 可见性与服务端授权一致性。
- [Convert / DO Route Gaps](convert_do_route_gaps.md)：`create_do` / `convert_do` 的 owner、gate 与重复创建缺口。
- [Admin Bypass Matrix](admin_bypass_matrix.md)：Admin/Super Admin 短路及其边界。
- [Opt-in Checks](opt_in_checks.md)：全局安全 middleware 与逐路由权限调用的区别。
- [INDEX](INDEX.md)：证据强度、交界和覆盖核验。

## Evidence Posture

- **Strong:** `core/permission/checker.py` 的 role/module/action 判定、Admin bypass；canonical route method/signature；CSRF safe methods；采样模板按钮 gate。
- **Medium:** standard bootstrap 的 route winner、service-internal gate 与实际安装关系。
- **Weak / UNKNOWN:** 生产反向代理、非标准启动方式、数据库 RLS、全量 endpoint 覆盖率和运行期角色数据。

## Critical Honesty Findings

1. Legacy checker 在被调用时通常 default-deny；系统缺口在于调用是逐 route opt-in，并非全局强制。
2. UI `has_permission` 只影响可见性；`convert_so`、`create_do`、Quote status、Approval decision 等服务端入口存在缺口。
3. `/create_do` 与 `/convert_do` 是两个 DO 创建 surface：前者无 server gate，后者在 service 检查 Sales Orders edit；两者 policy 不同且均为 GET。
4. Admin/Super Admin 绕过所有 checker action，但无 checker 的端点不是 Admin-only，而是所有可达主体都不受 permission matrix 限制。
5. 全局 CSRF middleware 覆盖 POST/PUT/PATCH/DELETE，但把 GET 视作 safe；因此不能补救 GET mutation。
6. 模块级 RBAC 不自动提供 owner、tenant、approver 或状态转换授权。

## Hard Boundaries

- 本包是 Legacy 知识抽取，不是源码迁移或目标授权模型。
- 只交叉引用 `risk-catalog/permission_holes` 与 `platform-obs`，不重写其权威内容。
- Human Confirm、browser confirm、菜单隐藏均不得解释为 server authorization。
- Admin role 字符串 bypass 不得作为 EAOS 目标模式；目标只能提炼为 default-deny、集中 command policy、对象范围和审计需求。
- 不打开 CRUD，不创建 G 号，不修改本包之外文件。

## Read-only Roots

- Legacy: `H:\Workspace\EZAM_CRM - 9.0\`
- Cross-reference: `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md`
- Cross-reference: `docs/knowledge/legacy-extract/platform-obs/identity_obs.md`
