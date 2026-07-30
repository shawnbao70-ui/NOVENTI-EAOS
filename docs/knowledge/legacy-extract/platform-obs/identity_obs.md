# Login / Permission / Tenant — Legacy Identity Observation

**Evidence strength:** Strong（legacy 登录、session、role permission matrix）/ Medium（V15.1 Login/Tenant registry）/ Weak（跨业务 tenant scope 一致性）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件记录用户可见身份表象：`/login`、session、用户/角色、Permission Center、Login Center 与 Tenant Center。

Legacy auth 明确仍为权威；Login Center 默认关闭并以 registry/policy framework 形式并存。Tenant Center 也默认关闭，保留 legacy single-tenant。部分业务查询使用 tenant dual-read filter，部分不使用，不能认定全局隔离可靠。

本文件不是 EAOS Identity/Permission Kernel 方案。EAOS 必须另建，禁止继承旧 session、role 字符串、权限表结构、privileged bypass 与 tenant bridge。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| IDENTITY-OBS-RULE-001 | 登录按 active username 查用户并验证密码；成功/失败均记录 login log | 成功时旧 hash 可自动 rehash | Strong |
| IDENTITY-OBS-RULE-002 | 成功登录清空旧 session，写 user_id、username、role，绑定 runtime context 并建立 CSRF token | remember_me 传给 runtime context | Strong |
| IDENTITY-OBS-RULE-003 | logout 尝试记录退出后清空 session | 记录失败被吞掉 | Strong |
| IDENTITY-OBS-RULE-004 | 权限判断以 session username 找 users.role，再查 role_permissions 的 module/action 列 | module name 有 aliases | Strong |
| IDENTITY-OBS-RULE-005 | 权限动作包括 view/add/edit/delete/export/import/print/approve | print 在 can_view=1 时可回退允许 | Strong |
| IDENTITY-OBS-RULE-006 | Admin / Super Admin 角色绕过所有权限检查 | 字符串匹配，大小写归一 | Strong |
| IDENTITY-OBS-RULE-007 | Permission Center 按 role 展示模块矩阵和用户数；view/edit 分别受自身权限控制 | 无 role 时选择第一角色或 Admin | Strong |
| IDENTITY-OBS-RULE-008 | 有用户的角色和特权角色不可删除 | 普通角色删除有门禁 | Strong |
| IDENTITY-OBS-RULE-009 | 用户管理路由的门禁不一致：users list 强制 Admin；edit/add page 与 delete 路由存在缺失或弱门禁 | 说明 per-route enforcement 不可靠 | Strong |
| IDENTITY-OBS-RULE-010 | Login Center 首次读取 seed identity/policy/device/history metadata，并明确 legacy login active | 默认不接管登录 | Strong |
| IDENTITY-OBS-RULE-011 | Login Center schema 声明 login/password/session policy、device 与 login history | 是否被 legacy authenticate 强制消费需逐项验证 | Medium |
| IDENTITY-OBS-RULE-012 | Tenant Center seed default tenant，提供 list/resolve/profile/type/identity chain | API 未见管理员权限门 | Strong framework |
| IDENTITY-OBS-RULE-013 | tenant SQL helper 允许当前 tenant 同时读 exact/default/null/empty legacy rows | 是迁移兼容 dual-read，不是严格隔离 | Strong |
| IDENTITY-OBS-RULE-014 | tenant context 缺失时回退 `default`，新上传可按 tenant 文件夹分层 | 不代表所有数据库写入都 stamp tenant | Strong |
| IDENTITY-OBS-RULE-015 | Login/Tenant/Permission 三个 Center 的 registry/health 表象不取代 `core/auth + session + checker` 运行权威 | Center metadata 不等于 enforce | Strong |
| IDENTITY-OBS-RULE-016 | MFA、SSO/OIDC/SAML、账号恢复、强制锁定执行、集中 session revoke 为 `UNKNOWN` | schema policy 字段不证明 enforcement | Missing |

## 3. 流程

### 3.1 登录

1. GET `/login` 展示登录页及 session/CSRF 过期提示。
2. POST username/password/remember。
3. 查询 active user，验证 hash，写 Success/Failed log。
4. 成功时可升级 password hash。
5. 清 session，写用户核心字段，绑定运行上下文与 CSRF。
6. 跳转首页；logout 清 session。

### 3.2 权限决策

1. 从 session 取 username/role。
2. 优先按 username 回查用户当前 role。
3. Admin/Super Admin 直接允许。
4. 规范 module alias 后查 role_permissions。
5. 按 action 映射 can_* 字段判断。
6. 路由是否实际调用 checker 取决于每个 handler。

### 3.3 租户表象

访问 Tenant Center → seed default metadata → list/resolve tenant/profile/type/identity chain。请求 tenant context 缺失时使用 default；repository 可选择 dual-read filter。租户开通、成员加入、切换、停用与数据迁移流程为 `UNKNOWN`。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| IDENTITY-OBS-VAL-001 | 登录 username/password 为必填 form | 强 | 服务端验证 active user/hash |
| IDENTITY-OBS-VAL-002 | 重复 username 在 add user 时拒绝 | 强 | 编辑重名规则未核实 |
| IDENTITY-OBS-VAL-003 | 用户密码写入时 hash；已有 pbkdf2 字符串可原样保留 | 强 | 由字符串前缀判断 |
| IDENTITY-OBS-VAL-004 | Permission Center view/edit 自保护 | 强 | privileged bypass 仍适用 |
| IDENTITY-OBS-VAL-005 | 删除特权角色/有用户角色被阻断 | 强 | |
| IDENTITY-OBS-VAL-006 | 所有用户管理路由要求登录与 Users 权限 | 缺失/不一致 | edit page、add page、delete route 有缺口 |
| IDENTITY-OBS-VAL-007 | Login Center policy 被 authenticate/session 强制执行 | 缺失/未确认 | framework metadata 与 legacy auth 并行 |
| IDENTITY-OBS-VAL-008 | Tenant Center API 仅管理员可访问 | 缺失 | 路由未见权限检查 |
| IDENTITY-OBS-VAL-009 | 所有业务表读写强制 tenant scope | 缺失/不一致 | helper 采用 opt-in，legacy rows dual-read |
| IDENTITY-OBS-VAL-010 | MFA、device trust、并发登录、idle timeout、lockout | 缺失/未确认 | schema 有字段，执行链 `UNKNOWN` |

## 5. 数据含义

| 数据 | Legacy 表象 |
|---|---|
| `users` | 用户账号、password hash、role、status |
| `roles` | 角色定义 |
| `role_permissions` | role × module 的 can_view/add/edit/delete/export/import/print/approve |
| session `user_id/username/role` | 当前请求身份核心 |
| login logs | 成功/失败/退出历史 |
| `identity_registry` | Login Center 身份层级 metadata |
| login/password/session policies | V15.1 policy metadata |
| device registry | 设备 metadata/trust 标签 |
| `tenant_profiles/settings/types/brand_assets` | Tenant Center metadata |
| tenant context | 请求范围字符串，缺失时 default |
| dual-read tenant predicate | 当前 tenant + default/null/empty legacy 数据兼容读取 |

## 6. 状态词汇

| 词汇 | 含义 |
|---|---|
| Success / Failed | legacy login log 结果 |
| active | user/policy/device/tenant metadata 启用标签 |
| default | policy key、tenant code 或兼容上下文 |
| Admin / Super Admin | privileged bypass 角色 |
| enabled_by_default=false | Login/Tenant Center 不接管 legacy |
| legacy_login_active=true | 旧认证权威 |
| legacy_single_tenant=true | 旧单租户权威 |
| locked/suspended/revoked/expired | 完整执行语义部分为 `UNKNOWN` |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\business_modules\identity.md`
- `H:\Workspace\EZAM_CRM - 9.0\core\auth\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\auth\service.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\auth\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\auth\session.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\permission\checker.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\permission\module_catalog.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\permission_center\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\permission_center.html`
- `H:\Workspace\EZAM_CRM - 9.0\apps\login_center\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\login_center\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\login_center\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_login_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_tenant_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\runtime\tenant_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\database\tenant_scope.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v41_tenant_column_schema.py`

**Excluded:** 未打开或分析 Brain/Twin 文件与实现。

## 8. EAOS 重写备注

- 只保留身份业务需求：登录、登出、用户、角色、授权、审计、租户上下文、策略可配置性。
- EAOS Identity/Permission Kernel 必须从宪章独立设计；禁止复用 role 字符串 bypass、per-route opt-in、旧表结构和 default dual-read 作为目标模型。
- 权限应默认拒绝并集中执行，tenant 隔离应为强制数据边界，不依赖每个 repository 自愿调用 helper。
- Login Center policy metadata 只能作为需求候选，未验证 enforcement 的字段不得迁移为规则。
