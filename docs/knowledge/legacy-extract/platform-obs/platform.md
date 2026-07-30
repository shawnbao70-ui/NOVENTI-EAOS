# Platform / System 业务平台面 — Legacy Observation

**Evidence strength:** Strong（模块挂载清单、页面入口、session 语言切换）/ Medium（Platform/System 边界规范）/ Missing（可靠统一租户运营控制面）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件观察 Legacy 的 Platform/System 业务平台面：模块通过 manifest/router 被挂载，System 提供设置、组织、日志、健康等管理入口，Tenant Center 提供默认关闭的框架页与只读 API。

`business_modules/platform.md` 和 `system.md` 多为边界/未来重构规范；真正运行证据来自 manifest、已挂载路由、页面和中心服务。未形成一个可证明一致的多租户运营控制面。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| PLATFORM-OBS-RULE-001 | Platform manifest 按 foundation/core/v15/业务等层登记 router module path、factory 与 router 类型 | 登记不证明业务功能完整 | Strong |
| PLATFORM-OBS-RULE-002 | Platform 规范定位为共享基础设施，不拥有业务记录 | 这是边界意图，不是 EAOS Kernel 定义 | Medium |
| PLATFORM-OBS-RULE-003 | System 规范定位为运营管理层：设置、组织、通知、日志、健康、备份与模块 registry | 多项仍标 target/future | Medium |
| PLATFORM-OBS-RULE-004 | 平台页面可在 session 中即时切换 locale；非法 next 不以 `/` 开头时回首页 | 未见用户偏好持久化 | Strong |
| PLATFORM-OBS-RULE-005 | communication workspace landing 根据 workspace registry 重定向 | registry 是导航装配，不是权限证明 | Strong |
| PLATFORM-OBS-RULE-006 | Login/Tenant/AI Employee Center 都有 framework page、health API 和 seed-on-read 行为 | 各中心明示默认关闭或 legacy authoritative | Strong |
| PLATFORM-OBS-RULE-007 | Tenant Center framework 默认显示 `default` tenant 和 tenant types | Legacy single-tenant 仍保留 | Strong |
| PLATFORM-OBS-RULE-008 | 模块挂载既含页面 router，也含 API router、direct export 和 tuple router | 混合装配反映 Legacy 迁移过程 | Strong |
| PLATFORM-OBS-RULE-009 | manifest 中出现的模块数量、名称和路径是装配清单，不是 capability SLA | health/route 可用性需另证 | Strong |
| PLATFORM-OBS-RULE-010 | System 与 Identity 共享 admin workspace，边界存在重叠 | 日志、组织、权限归属在规范中也标 shared/partial | Medium |
| PLATFORM-OBS-RULE-011 | Canonical 挂载分三段：platform/business API manifest → business page manifest → V14 residual 去重；first-match 影响最终 handler | 这是迁移装配事实，不是目标 runtime 拓扑 | Strong |
| PLATFORM-OBS-RULE-012 | Center 的 enabled-by-default=false 不必然 unmount 路由；可能仍可访问 framework/health | feature flag 更接近激活 metadata，不是统一路由开关 | Strong |
| PLATFORM-OBS-RULE-013 | 实际 settings 入口与 registry 中 `/settings_center` 存在命名漂移 | 说明平台导航与运行入口未统一 | Medium |
| PLATFORM-OBS-RULE-014 | 租户运营的开通、停用、订阅、配额、计费、域名验证和数据导出规则为 `UNKNOWN` | Tenant Center API 主要 list/resolve | Missing |
| PLATFORM-OBS-RULE-015 | 模块启停、依赖解析、失败隔离、升级回滚和每租户挂载策略为 `UNKNOWN` | manifest 仅静态登记 | Missing |

## 3. 流程

### 3.1 模块装配观察

1. bootstrap manifest 收集 platform 与 business API 条目并挂载。
2. 第二阶段挂载 business page routers。
3. 第三阶段挂载 V14 residual，并按已存在路由去重；先匹配的 handler 可能保持权威。
4. 用户通过 workspace/navigation 访问页面或 API。
5. 单个模块是否 enabled、healthy、authorized 仍由各自实现决定；center flag 不等于必然卸载。

### 3.2 租户运营入口

1. 用户访问 `/tenant_center`。
2. 服务首次读取时 seed 默认 registry。
3. 页面展示版本、health、default tenant 和 tenant types。
4. API 可 list/resolve tenants/profiles/types/identity chain。
5. 创建/停用/迁移租户的运营流程未找到，标 `UNKNOWN`。

### 3.3 System 管理面

规范列出 settings、organization、notifications、logs、health、registry、backup/restore；本波只将其视为运营入口目录，不将规范中的 target service/table 自动认定为运行事实。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| PLATFORM-OBS-VAL-001 | locale redirect 仅接受站内 `/` 开头目标 | 强 | 防止直接外部跳转 |
| PLATFORM-OBS-VAL-002 | manifest entry 需提供 module path/factory 元数据 | 强（结构） | 不验证业务可用 |
| PLATFORM-OBS-VAL-003 | Tenant Center profile validator 存在 | 弱 | 页面/API 未提供 profile mutation |
| PLATFORM-OBS-VAL-004 | Tenant Center API 的认证/管理员权限 | 缺失/不明确 | list/resolve 路由未见权限门 |
| PLATFORM-OBS-VAL-005 | 模块挂载前依赖、版本和健康门禁 | 缺失 | `UNKNOWN` |
| PLATFORM-OBS-VAL-006 | 每租户模块 entitlement 与隔离 | 缺失 | `UNKNOWN` |
| PLATFORM-OBS-VAL-007 | System settings/backup/restore 的审批与审计 | 缺失/未核实 | 规范不等于运行校验 |

## 5. 数据含义

| 概念 | Legacy 表象 |
|---|---|
| ManifestEntry | router 装配描述：slug、module path、factory、layer、router kind |
| platform manifest | 启动挂载目录，不是业务模块主数据 |
| workspace registry | 页面导航与 landing 映射 |
| Platform | 规范中的共享基础设施边界 |
| System | 规范中的运营管理边界 |
| Tenant Center | 默认关闭的 tenant metadata/framework 中心 |
| default tenant | 为兼容 legacy single-tenant 使用的默认身份 |
| health API | 结构/seed 健康表象，不等于端到端业务健康 |

## 6. 状态词汇

| 词汇 | 含义 |
|---|---|
| enabled by default = false | 中心默认不接管 legacy runtime |
| legacy single-tenant = true | 旧单租户运行仍权威 |
| active | tenant/profile/type/metadata 的启用标签 |
| default | 缺省 tenant/context |
| configured / mounted | 装配状态；不等于业务 ready |
| healthy | 单中心健康输出；检查范围依实现 |
| suspended/disabled/degraded/failed | 平台统一运营状态为 `UNKNOWN` |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\business_modules\platform.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\system.md`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\manifest\platform_manifest.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\manifest\center_manifest.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\router_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\enterprise_cutover.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\business_pages.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\platform\v15_platform_pages.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\tenant_center\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_tenant_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\workspace_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\runtime\tenant_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\database\tenant_scope.py`

**Excluded:** 未打开或分析 Brain/Twin 文件与实现。

## 8. EAOS 重写备注

- 仅迁移“运营需求”：模块可发现性、健康、租户入口、语言/工作区体验等知识。
- 不迁移 manifest/router/bootstrap 结构为 EAOS Kernel。
- EAOS 模块生命周期、tenant control plane、entitlement、隔离与审计必须按新宪章独立设计。
- Legacy 的 `default`/dual-read 兼容策略只能作为迁移风险证据，不是目标多租户模型。
