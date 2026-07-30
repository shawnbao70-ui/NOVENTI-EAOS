# PWA 与离线能力 — Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Honesty summary:** Manifest、Service Worker 与后端离线框架存在；终端前端接线不完整；Web Push 未落地

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| `static/pwa` Manifest / Service Worker | 可安装元数据与缓存策略存在 | Strong static |
| `apps/ui_center/ux_pwa_api.py` | 状态、离线包、同步队列和冲突 API 已落地 | Strong |
| `v15/smart_terminal` | ACL bundle、终端注册与离线写队列存在 | Strong |
| PWA 前端脚本 | 安装、IndexedDB、同步脚本存在 | Strong static |
| Mobile terminal 模板接线 | 未加载关键安装与 offline-store 脚本 | Strong gap evidence |
| 真机安装、HTTPS、离线运行 | 本轮未启动浏览器/服务验证 | UNKNOWN |

---

## 2. 业务规则

| ID | PWA 行为规则 | 触发条件 | 例外/缺口 |
|----|--------------|----------|-----------|
| PWA-R1 | PWA 使用 `static/pwa` 的 manifest 与 service worker 作为主要资产 | Install | 另有 AI 包内旧副本 |
| PWA-R2 | 安装入口和应用 ID 指向 `/terminal`，display 为 standalone | Manifest | |
| PWA-R3 | Terminal HTML 和离线数据 API 要求登录 | Access | |
| PWA-R4 | 离线 bundle 按 Products/Customers/Quotes/Documents view 权限过滤 | Fetch bundle | 无权限时 fail closed |
| PWA-R5 | 离线写队列只允许 `terminal_note.upsert` | Flush ops | 不允许订单、库存或财务动作 |
| PWA-R6 | 同步版本冲突不能静默覆盖，必须人工 keep_server 或 keep_client | Conflict | |
| PWA-R7 | 同步响应明确不执行高风险企业动作 | Sync | |
| PWA-R8 | Service Worker 只处理 GET 缓存；静态资源 cache-first，terminal/PWA API network-first | Fetch | |
| PWA-R9 | Background Sync 事件只通知客户端触发离线队列同步 | Sync event | 依赖 SW 与 offline-store 成功接线 |
| PWA-R10 | 安装验收需要 HTTPS 或 localhost，并保留人工真机步骤 | Field install | 静态 gate 不等于真机通过 |
| PWA-R11 | 不宣称 App Store/Play Store 上架 | Readiness | |
| PWA-R12 | Web Push 当前未实现 | Push | 无 PushManager/VAPID/push handler |
| PWA-R13 | Mobile terminal 当前未加载 `pwa-install.js` 和 `offline-store.js` | Terminal render | 可能使安装、离线读写和同步链空转 |

---

## 3. 流程

### 3.1 预期安装流程

已登录用户打开 `/terminal` → 页面加载安装脚本 → 注册 `/service-worker.js` → 浏览器触发安装提示或 iOS 手工添加 → standalone 打开 Terminal。

当前缺口：mobile terminal 模板没有加载安装脚本，因此纯 Terminal 用户路径上 Service Worker 注册和安装按钮可能不可用。

### 3.2 缓存与离线读

在线访问 → Service Worker 预缓存核心 Terminal 资产 → API 获取按权限裁剪的离线 bundle → IndexedDB 保存 products/customers/quotations/knowledge。

离线时 Service Worker 可返回缓存的 Terminal 页面和部分 PWA API 响应；已观察到 IndexedDB 写入脚本，但没有确认业务 UI 从 IndexedDB 完整读回。

### 3.3 离线写队列

客户端生成 terminal note 操作 → IndexedDB pending queue → 在线或 Background Sync 时 POST `/api/v15/pwa/sync` → 服务端幂等处理 → applied / conflict / rejected → 冲突由用户显式解决。

当前缺口：`offline-store.js` 未被 terminal 模板加载，Profile 的队列 UI 可能提前退出。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| PWA-V1 | Manifest/SW 资产存在且字段符合 Terminal 安装 | Static Hard | |
| PWA-V2 | Terminal 和 PWA API 登录门 | Hard | 未登录 401 |
| PWA-V3 | Offline bundle 按模块权限裁剪 | Hard | |
| PWA-V4 | 离线 op 属于允许集合 | Hard | 仅 terminal note |
| PWA-V5 | `client_op_id` 幂等与版本冲突检测 | Hard | |
| PWA-V6 | `scope=all` 队列查看和跨用户解决只允许管理员 | Hard | |
| PWA-V7 | 真机安装、离线重开和同步 | UNKNOWN | 静态报告 live probe 曾跳过 |
| PWA-V8 | Mobile terminal 加载安装/离线脚本 | Failed static observation | 当前模板未引入 |
| PWA-V9 | Manifest 声明的 PNG 图标真实可访问 | UNKNOWN | 本轮文件扫描未确认全部图标 |
| PWA-V10 | Web Push 订阅与投递 | Absent | |

---

## 5. 数据含义

### 5.1 Offline bundle

| Data | Meaning |
|------|---------|
| `stores.products` | 最多一定数量的产品离线快照 |
| `stores.customers` | 当前权限允许的客户离线快照 |
| `stores.quotations` | 报价离线快照 |
| `stores.knowledge` | 文档/知识离线快照 |
| `allowed` | 当前用户是否允许缓存该 store |
| `skipped.reason` | 常见为 permission_denied |

### 5.2 同步队列

| Field | Meaning |
|-------|---------|
| `client_op_id` | 客户端幂等键 |
| `op` | 允许的操作类型 |
| `base_version` | 客户端所基于的服务端版本 |
| `status` | pending/applied/conflict/rejected/resolved_* |
| `resolution` | keep_server 或 keep_client |

### 5.3 缓存

Service Worker 分静态与 API 缓存桶。缓存的是页面/资源/API 快照，不是业务数据库权威；离线展示可能过期。

---

## 6. 状态词汇

| Value / family | Meaning |
|----------------|---------|
| live | PWA 功能状态判定为可用 |
| beta | Background Sync 等部分能力 |
| missing | 文件或能力缺失 |
| pending | 客户端离线操作待同步 |
| applied | 服务端已应用 |
| conflict | 版本冲突待人工处理 |
| rejected | 操作不允许或数据无效 |
| resolved_server | 保留服务端版本 |
| resolved_client | 接受客户端版本 |
| human_review | 冲突策略 |
| standalone | PWA 独立窗口显示模式 |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| Manifest 图标文件是否完整存在并可访问 | `static/pwa/manifest.json` 与 `static/pwa/icons` 文件扫描；未运行 HTTP |
| `/manifest.json`、`/service-worker.js` 实际是否返回 200 | 路由与静态资产已核查；未启动 live probe |
| Chromium/iOS 真机是否可安装 | 安装清单和静态脚本已读；未执行浏览器/HTTPS 测试 |
| 离线 Terminal UI 是否从 IndexedDB 读回业务数据 | `offline-store.js`、terminal 模板与业务脚本已核查；未观察到完整 UI 读回链 |
| 写队列是否端到端可用 | API/后端逻辑存在；mobile terminal 未加载 offline-store，未运行浏览器演练 |
| CDN 资源断网时的完整样式 | mobile terminal 使用外部 CDN，SW 预缓存未覆盖；未真机断网验证 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `static/pwa/manifest.json` | 安装元数据 | Strong static |
| `static/pwa/service-worker.js` | 缓存与 sync 事件 | Strong static |
| `static/js/pwa-install.js` | 安装提示与 SW 注册 | Strong |
| `static/js/offline-store.js` | IndexedDB 与离线 bundle/队列 | Strong |
| `static/js/smart-terminal.js` | Terminal 与 Background Sync 注册 | Strong |
| `static/js/terminal-sync-queue.js` | 队列与冲突 UI | Strong |
| `apps/ui_center/ux_pwa_api.py` | PWA API、ACL、同步和冲突解决 | Strong |
| `v15/smart_terminal/pwa.py` | 状态与实地安装 readiness | Strong |
| `v15/smart_terminal/offline.py` | 离线 bundle | Strong |
| `v15/smart_terminal/sync_queue.py` | 操作白名单、幂等与冲突 | Strong |
| `templates/layouts/mobile_terminal.html` | Terminal 壳与脚本接线缺口 | Strong |
| `templates/terminal/profile.html` / `settings.html` | 安装和队列 UI | Medium |
| `templates/base.html` | Desktop PWA 脚本接线 | Strong |
| `database/v151_smart_terminal_sync_queue_schema.py` | 服务端队列表 | Strong static |
| `docs/reports/Business_Strong_B001_PWA_Report.md` | PWA 静态 gate | Medium |
| `docs/reports/Business_Strong_B005_Sync_Queue_Report.md` | 写队列 gate | Medium |
| `docs/reports/Business_Strong_B007_PWA_Field_Install_Report.md` | 实地安装 gate（live skipped） | Medium |
| `docs/development/PWA_FIELD_INSTALL_CHECKLIST.md` | 人工验收步骤 | Medium |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
