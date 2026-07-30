# UI Shell 与导航 — Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Boundary:** UI 壳、导航和 workspace 只负责展示与可达性，不是业务规则权威

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| `templates/base.html` 与 `core/ui` | canonical layout/header/sidebar 模板链 | Strong |
| V15 UX persona | 会话 workspace、菜单与工作台上下文 | Strong |
| V16.2/V18 role workspace | 侧边栏白名单与角色专职表面 | Strong |
| Fixed Link Graph | Layer A/B/C URL 与入口法源 | Strong |
| `apps/ui_center` | 设计系统 registry、API 和残留路由挂载 | Medium |
| 首页模板 | 规范声明与运行时模板存在分歧 | Strong gap evidence |

Legacy 同时存在 V15 persona、V16 role workspace、Document workspace 和子平台表面。必须按各自 ID 空间理解，不能把菜单可见性解释为业务授权。

---

## 2. 业务规则

| ID | UI 行为规则 | 触发条件 | 例外/缺口 |
|----|-------------|----------|-----------|
| UI-R1 | 侧边栏链接必须属于已知 URL 并受角色 workspace 白名单约束 | Render nav | 依赖上游提供权限函数 |
| UI-R2 | Layer B 是 canonical hub；Layer C 详情/动作继承父入口，不另建菜单 | Navigation | |
| UI-R3 | 禁止项从菜单中省略，不用 CSS 隐藏 | Role render | |
| UI-R4 | V18 侧边栏重排最多六个顶层组，只改变展示分组，不改 URL | Render | |
| UI-R5 | 有专职 workspace 时优先用其菜单；否则用全局 registry 和角色 flags | Resolve menu | |
| UI-R6 | 菜单项可附 module/action 权限，运行时通过 `can_access` 过滤 | Render item | 缺少 `can_access` 时 renderer 默认放行 |
| UI-R7 | Legacy 菜单只在没有 role-workspace 菜单且 profile 允许时回退 | Render | |
| UI-R8 | 完整 workspace 切换器主要向 administrator/CEO/executive 开放 | Switcher | |
| UI-R9 | 非首页可进入 focus mode，隐藏部分平台/AI chrome | Page context | 只是展示 |
| UI-R10 | Header 操作槽顺序和 Sidebar 品牌位置由 canonical shell 控制 | Shell render | |
| UI-R11 | 导航 URL 可经过修复表映射到 canonical 路径 | Build menu | 修复表可能掩盖旧链接 |
| UI-R12 | ui_center 设计系统默认不接管 Legacy UI | Bootstrap | |
| UI-R13 | 业务角色 dashboard surface 可隐藏平台级 widgets | Workspace | 不影响业务数据权限 |

---

## 3. 流程

### 3.1 壳层渲染

`base.html` → shell start → platform brand + sidebar navigation → header/breadcrumb/actions → workspace/workbench/dashboard 内容 → shell end。

页面上下文依次吸收 workspace registry、语言、品牌、身份、role workspace 和 V15 UX 数据。

### 3.2 导航决策

会话角色与 UX flags → 解析 role workspace → 选择专职菜单或全局 registry → 检查 item flag 与权限 → V18 六组重排 → 渲染侧边栏。

菜单过滤只控制入口可见性；直接访问仍必须由业务路由执行权限和数据范围校验。

### 3.3 Workspace 切换

用户选择 V15 workspace → 写入 session `ux_workspace` → 解析该 persona 的 home route → 跳转。V16 role workspace 仍可独立决定侧边栏，因此两者不总是一一对应。

### 3.4 首页

UI ownership 文档声明 canonical homepage/workbench 管线；实际 `/` 和 `/home` 观察到主要渲染 `ux/todays_work.html`。最终运行模板需以启动后的路由表和 HTTP 结果确认。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| UI-V1 | 组件、主题、布局、颜色和图标 key 合法 | Hard for registry | |
| UI-V2 | 模板 ownership 不重复 | Hard/Static | |
| UI-V3 | 禁止引用 obsolete UI 路径 | Hard/Static | |
| UI-V4 | V18 IA 顶层组不超过六个 | Hard | |
| UI-V5 | Workspace URL 可达 | Static/runtime check | |
| UI-V6 | 导航项满足角色 flags 与 RBAC | Medium | renderer 依赖注入 |
| UI-V7 | Fixed Link Layer B hub 存在 | Static gate | |
| UI-V8 | 菜单隐藏等于业务拒绝 | Absent by design | 业务路由必须重复校验 |
| UI-V9 | V15 persona 与 V16 role workspace 一致 | Weak/Unknown | 双 ID 空间 |
| UI-V10 | `/` 与 `/home` 使用同一 canonical 模板 | Weak/Unknown | 规范与运行实现分歧 |

---

## 5. 数据含义

| Data | Meaning |
|------|---------|
| `ux.workspace_id` | V15 persona/workspace ID |
| `session.ux_workspace` | 用户当前选择的 V15 workspace |
| `ux.role_nav.*` | show_* 导航可见性 flags |
| `ux.menu.business_nav` | 业务语义链菜单 |
| `ux.menu.workspace_switcher` | 可切换 persona |
| `role_workspace.workspace_id` | V16.2 专职角色 workspace |
| `role_workspace.sidebar_groups` | 侧边栏渲染组 |
| `role_workspace.ui_runtime` | favorites、quick actions、chains、搜索范围 |
| `role_workspace.user_scope.mode` | owner/role/executive/platform 等 UI scope 提示 |
| `function_center.functions` | 工作台功能卡 |
| `allowed_nav_pages` | 客户端允许页面集合 |
| Fixed Link Layer A/B/C | 全 URL、canonical hub、继承详情/动作层 |

---

## 6. 状态词汇

| Value / family | Meaning |
|----------------|---------|
| owner / role / executive / platform / guest | Workspace 用户范围模式 |
| simplified_home | 聚焦角色的简化首页 |
| page_focus_mode | 非首页的聚焦 chrome |
| show_legacy_menu | 允许回退旧菜单 |
| multi_workspace | 显示完整 workspace 切换 |
| filter_flags | 是否按 role flags 过滤 registry |
| under_development | 占位页面状态 |
| hide_platform_widgets | 业务 dashboard 隐藏平台卡片 |
| use_eoc | Persona 的 EOC 倾向，不保证实际首页模板 |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| 已认证用户最终首页是否已切到 canonical homepage | `core/ui/ownership.py`、platform/ui_center 首页路由与模板引用；未启动 HTTP 实测 |
| `/` 与 `/home` 路由挂载先后和最终处理器 | `apps/platform/v14_residual.py`、`apps/ui_center/v15_ui_pages.py`、bootstrap；未读取运行路由表 |
| V15 与 V16 workspace 是否保持同步 | `v15/ux/registry.py`、`core/ui/role_workspace/workspaces/**`；未发现统一映射校验 |
| Document workspace registry 是否仍与 role workspace 双向同步 | `document/workspace_registry.py` 与 role workspace definitions；未运行 diff |
| 客户端 `allowed_nav_pages` 是否完整阻止越界导航 | 注入点与 static JS 已检索；完整浏览器行为未实测 |
| PWA 底部导航与 desktop sidebar 是否同源 | `v15/smart_terminal/**`、`static/pwa/**` 与 role workspace；留给 PWA 专题 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `templates/base.html` | 根壳层与静态资源 | Strong |
| `templates/core/ui/**` | canonical header/sidebar/workspace 模板 | Strong |
| `core/ui/ownership.py` / `canonical.py` | UI ownership 与 canonical 组件 | Strong |
| `core/ui/finalization.py` | obsolete 路径和最终检查 | Strong |
| `core/ui/runtime/pipeline.py` | 壳层渲染管线 | Strong |
| `core/ui/role_workspace/renderer.py` | 菜单决策 | Strong |
| `core/ui/role_workspace/menu_registry.py` | 全局侧边栏 registry | Strong |
| `core/ui/role_workspace/ia_v18.py` | 六组 presentation remap | Strong |
| `core/ui/role_workspace/workspaces/**` | 专职 role workspace | Strong |
| `v15/ux/controller.py` / `registry.py` | UX context 与 persona | Strong |
| `v15/ux/role_navigation.py` | 角色 flags | Strong |
| `v15/ux/smart_menu.py` / `workspace_switch.py` | 菜单与切换 | Strong |
| `v15/rbac/unified.py` | RBAC 收紧 UI flags | Strong |
| `apps/ui_center/` | 设计系统 API 与残留挂载 | Medium |
| `apps/platform/v14_residual.py` | 实际首页路径 | Strong |
| `docs/architecture/link_principle/FIXED_LINK_GRAPH.json` | Layer A/B/C 法源 | Strong |
| `docs/design/v17/INTERFACE_STANDARD.md` | 链接与界面标准 | Medium |
| `docs/reports/Navigation_Report.md` | 导航审计 | Medium |
| `docs/reports/V162_Navigation_Matrix.md` | Role workspace 导航矩阵 | Medium |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
